# routes/qr_driver.py
from flask import Blueprint, jsonify, request
import qrcode
import base64
from io import BytesIO
from db import db
import datetime
import random
import hashlib
from datetime import datetime, timedelta
from routes.config import DEVICE_URL,SERVER_URL

qr_driver_token_bp = Blueprint('qr_driver_token', __name__)


@qr_driver_token_bp.route('/generate_qr/work', methods=['GET'])
def generate_qr_work():
    from flask import request
    print("🎯 收到 generate_qr/work 請求！")
    device_serial = request.args.get('device_serial')  # 從 URL 拿 device_serial
    if not device_serial:
        return jsonify({"error": "缺少 device_serial 參數"}), 400

    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT driver_id, driver_name FROM drivers ORDER BY RAND() LIMIT 1")
            driver = cursor.fetchone()
        if not driver:
            return jsonify({"error": "找不到駕駛資料"}), 404

        qr_base64, raw = create_qr_and_save_token(driver['driver_id'], driver['driver_name'], 'W', device_serial)
        return jsonify({"qr_base64": qr_base64, "info": raw})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@qr_driver_token_bp.route('/generate_qr/off', methods=['GET'])
def generate_qr_off():
    from flask import request
    device_serial = request.args.get('device_serial')
    if not device_serial:
        return jsonify({"error": "缺少 device_serial 參數"}), 400

    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT driver_id, driver_name FROM drivers ORDER BY RAND() LIMIT 1")
            driver = cursor.fetchone()
        if not driver:
            return jsonify({"error": "找不到駕駛資料"}), 404

        qr_base64, raw = create_qr_and_save_token(
            driver['driver_id'], driver['driver_name'], 'O', device_serial
        )
        return jsonify({"qr_base64": qr_base64, "info": raw})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
def generate_driver_qr_image(state='W', device_serial=None):
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT driver_id, driver_name FROM drivers ORDER BY RAND() LIMIT 1")
            driver = cursor.fetchone()
        if not driver or not device_serial:
            return None
        qr_base64, _ = create_qr_and_save_token(driver['driver_id'], driver['driver_name'], state, device_serial)
        return qr_base64
    except Exception as e:
        print(f"❌ generate_driver_qr_image 錯誤：{e}")
        return None


def create_qr_and_save_token(driver_id, driver_name, state, device_serial):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    rand_num = random.randint(1000, 9999)
    raw_string = f"{driver_id},{driver_name},{rand_num},{timestamp},{state}"
    hashed_token = hashlib.sha256(raw_string.encode()).hexdigest()

    try:
        cursor = db.cursor()
        if state == 'W':  
            expire_time = (datetime.now() + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')
            sql = '''
                INSERT INTO driver_tokens (driver_id, token, state, create_date, expire_time, used)
                VALUES (%s, %s, %s, %s, %s, 0)
            '''
            cursor.execute(sql, (driver_id, hashed_token, state, timestamp, expire_time))
        else:  # 下班 token 無限期
            sql = '''
                INSERT INTO driver_tokens (driver_id, token, state, create_date)
                VALUES (%s, %s, %s, %s)
            '''
            cursor.execute(sql, (driver_id, hashed_token, state, timestamp))
        db.commit()
        cursor.close()
    except Exception as e:
        print(f"❌ 寫入 token 時發生錯誤：{e}")
        return None, None

    bind_url = f"{SERVER_URL}/bind_driver/{hashed_token}?device_serial={device_serial}"

    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(bind_url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()

    return qr_base64, bind_url





@qr_driver_token_bp.route('/bind_driver/<token>', methods=['GET'], endpoint='bind_driver_token')
def bind_driver(token):
    device_serial = request.args.get("device_serial")
    if not device_serial:
        return "❌ 缺少設備資訊", 400

    try:
        with db.cursor() as cursor:
            # 查詢 token
            cursor.execute("""
                SELECT * FROM driver_tokens
                WHERE token = %s AND (
                    (state = 'W' AND used = 0 AND expire_time > NOW()) OR
                    (state = 'O')
                )
            """, (token,))
            token_data = cursor.fetchone()

            if not token_data:
                return "❌ QR Code 無效或已過期", 400

            bind_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            
            if token_data['state'] == 'W':
                sql = '''
                    INSERT INTO driver_tokens (driver_id, token, state, create_date, expire_time, used, bind_time)
                    VALUES (%s, %s, %s, %s, %s, 1, %s)
                '''
                cursor.execute(sql, (
                    token_data['driver_id'],
                    token_data['token'],
                    token_data['state'],
                    token_data['create_date'],
                    token_data['expire_time'],
                    bind_time
                ))
            else:
                sql = '''
                    INSERT INTO driver_tokens (driver_id, token, state, create_date, used, bind_time)
                    VALUES (%s, %s, %s, %s, 1, %s)
                '''
                cursor.execute(sql, (
                    token_data['driver_id'],
                    token_data['token'],
                    token_data['state'],
                    token_data['create_date'],
                    bind_time
                ))

            db.commit()

            # 查詢設備 IP 並通知
            cursor.execute("SELECT ip_address FROM devices WHERE device_serial = %s", (device_serial,))
            result = cursor.fetchone()
            if not result:
                return "❌ 找不到設備 IP", 404
            device_ip = result['ip_address']
            print(f"📡 通知設備端 IP：{device_ip}")

        import requests
        res = requests.post(f"http://{device_ip}:730/notify_driver_bound", timeout=3)
        if res.status_code != 200:
            print("⚠️ 設備端通知失敗")

        return "✅ 綁定成功！駕駛已打卡", 200
    
    except Exception as e:
        return f"❌ 錯誤：{str(e)}", 500





