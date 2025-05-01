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

def create_qr_and_save_token(driver_id, driver_name, state):
    # 組合原始內容：driver_id, driver_name, 隨機數字, 時間, 狀態
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    rand_num = random.randint(1000, 9999)
    raw_string = f"{driver_id},{driver_name},{rand_num},{timestamp},{state}"

    # SHA256 加密成 token
    hashed_token = hashlib.sha256(raw_string.encode()).hexdigest()

    # 寫入資料庫
    with db.cursor() as cursor:
        sql = '''
            INSERT INTO driver_tokens (driver_id, token, state, create_date)
            VALUES (%s, %s, %s, %s)
        '''
        cursor.execute(sql, (driver_id, hashed_token, state, timestamp))
    db.commit()

    # 產生 QR Code base64
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(raw_string)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()

    return qr_base64, raw_string

@qr_driver_token_bp.route('/generate_qr/work', methods=['GET'])
def generate_qr_work():
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT driver_id, driver_name FROM drivers ORDER BY RAND() LIMIT 1")
            driver = cursor.fetchone()
        if not driver:
            return jsonify({"error": "找不到駕駛資料"}), 404

        qr_base64, raw = create_qr_and_save_token(driver['driver_id'], driver['driver_name'], 'W')
        return jsonify({"qr_base64": qr_base64, "info": raw})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@qr_driver_token_bp.route('/generate_qr/off', methods=['GET'])
def generate_qr_off():
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT driver_id, driver_name FROM drivers ORDER BY RAND() LIMIT 1")
            driver = cursor.fetchone()
        if not driver:
            return jsonify({"error": "找不到駕駛資料"}), 404

        qr_base64, raw = create_qr_and_save_token(driver['driver_id'], driver['driver_name'], 'O')
        return jsonify({"qr_base64": qr_base64, "info": raw})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def generate_driver_qr_image(state='W'):
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT driver_id, driver_name FROM drivers ORDER BY RAND() LIMIT 1")
            driver = cursor.fetchone()
        if not driver:
            return None
        qr_base64, _ = create_qr_and_save_token(driver['driver_id'], driver['driver_name'], state)
        return qr_base64
    except Exception as e:
        print(f"❌ generate_driver_qr_image 錯誤：{e}")
        return None

