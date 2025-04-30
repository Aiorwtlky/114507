from flask import Blueprint, request, jsonify, render_template, redirect, url_for
import qrcode
import base64
from io import BytesIO
from db import db
from utils.token_manager import generate_token, verify_token
import time

reset_bp = Blueprint('reset', __name__)

@reset_bp.route('/generate_reset_token', methods=['POST'])
def generate_reset_token():
    data = request.get_json()
    device_serial = data.get('device_serial')

    try:
        with db.cursor() as cursor:
            # 產生reset專用token
            token, timestamp = generate_token(device_serial)

            # 寫入tokens表
            sql = '''
                INSERT INTO tokens (device_serial, token, created_at, used, is_reset)
                VALUES (%s, %s, FROM_UNIXTIME(%s), 0, 1)
            '''
            cursor.execute(sql, (device_serial, token, timestamp))
        
        db.commit()

        # 產生 QR code
        reset_url = f"http://192.168.0.103:307/reset_bind/{token}"
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=2
        )
        qr.add_data(reset_url)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()

        return jsonify({"qr_base64": qr_base64})

    except Exception as e:
        print(f"錯誤：{e}")
        return jsonify({"message": "伺服器錯誤"}), 500
    
@reset_bp.route('/reset_bind/<token>', methods=['GET', 'POST'])
def reset_bind(token):
    try:
        with db.cursor() as cursor:
            # 查token資料
            sql = "SELECT * FROM tokens WHERE token = %s"
            cursor.execute(sql, (token,))
            token_data = cursor.fetchone()

            if not token_data:
                return render_template('bind_error.html', message="無效的Reset Token！")

            if token_data['used'] == 1:
                return render_template('bind_error.html', message="Reset Token已被使用！")

            created_time = int(token_data['created_at'].timestamp())
            if not verify_token(created_time):
                return render_template('bind_error.html', message="Reset Token已過期！")

            if request.method == 'POST':
                device_serial = token_data['device_serial']

                # 清空設備資料
                sql_update = '''
                    UPDATE devices
                    SET car_brand=NULL, car_plate=NULL, vehicle_type=NULL, driver_position=NULL, bind_status=0, status='offline'
                    WHERE device_serial=%s
                '''
                cursor.execute(sql_update, (device_serial,))

                # 標記token已使用
                cursor.execute('UPDATE tokens SET used=1 WHERE token=%s', (token,))

                db.commit()

                return render_template('reset_success.html')

            return render_template('confirm_reset.html', token=token)

    except Exception as e:
        print(f"錯誤：{e}")
        return render_template('bind_error.html', message="伺服器錯誤！")
