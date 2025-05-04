# routes/qr_driver.py
from flask import Blueprint, jsonify
import qrcode
import base64
from io import BytesIO
from db import db
import datetime
import random
import hashlib

qr_driver_token_bp = Blueprint('qr_driver_token', __name__)

def create_qr_and_save_token(driver_id, driver_name, state, device_serial):
    import qrcode
    import base64
    from io import BytesIO
    import datetime
    import random
    import hashlib

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    rand_num = random.randint(1000, 9999)
    raw_string = f"{driver_id},{driver_name},{rand_num},{timestamp},{state}"
    hashed_token = hashlib.sha256(raw_string.encode()).hexdigest()

    with db.cursor() as cursor:
        sql = '''
            INSERT INTO driver_tokens (driver_id, token, state, create_date)
            VALUES (%s, %s, %s, %s)
        '''
        cursor.execute(sql, (driver_id, hashed_token, state, timestamp))
    db.commit()

    # ✅ 加入 device_serial 參數
    bind_url = f"http://192.168.0.102:307/bind_driver/{hashed_token}?device_serial={device_serial}"

    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(bind_url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()

    return qr_base64, bind_url



@qr_driver_token_bp.route('/generate_qr/work', methods=['GET'])
def generate_qr_work():
    from flask import request

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

    

@qr_driver_token_bp.route('/bind_driver/<token>', methods=['GET'])
def bind_driver(token):
    from flask import request
    device_serial = request.args.get("device_serial")  # 👈 取得是哪台設備

    if not device_serial:
        return "❌ 缺少設備資訊", 400
    
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM driver_tokens WHERE token = %s", (token,))
            token_data = cursor.fetchone()

            if not token_data:
                return "❌ 無效 QR Code", 404

            cursor.execute("UPDATE driver_tokens SET state = 'O' WHERE token = %s", (token,))
            db.commit()

            # 從資料庫取得設備 IP（你必須提前在 DB 儲存它們）
            cursor.execute("SELECT ip_address FROM devices WHERE device_serial = %s", (device_serial,))
            result = cursor.fetchone()
            if not result:
                return "❌ 找不到設備 IP", 404
            device_ip = result['ip_address']

        # 通知對應設備
        import requests
        res = requests.post(f"http://{device_ip}:730/notify_driver_bound")
        if res.status_code != 200:
            print("⚠️ 設備端通知失敗")

        return "✅ 綁定成功！駕駛已打卡", 200

    except Exception as e:
        return f"❌ 錯誤：{str(e)}", 500



