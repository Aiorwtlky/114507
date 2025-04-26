from flask import Blueprint, request, jsonify
import qrcode
import base64
from io import BytesIO
from db import db
from utils.token_manager import generate_token

qr_bp = Blueprint('qr', __name__)

@qr_bp.route('/register_device', methods=['POST'])
def register_device():
    data = request.get_json()
    device_serial = data.get('device_serial')

    if not device_serial:
        return jsonify({"message": "缺少 device_serial"}), 400

    try:
        with db.cursor() as cursor:
            # 確認設備是否存在，不存在就新增
            cursor.execute('SELECT * FROM devices WHERE device_serial = %s', (device_serial,))
            device = cursor.fetchone()
            if not device:
                sql_insert = '''
                    INSERT INTO devices (device_serial, manufacturer, manufacturer_address, software_version)
                    VALUES (%s, %s, %s, %s)
                '''
                cursor.execute(sql_insert, (
                    device_serial,
                    "北商資管114507",
                    "臺北市中正區濟南路321號行政大樓4樓資研討室4",
                    "V1.0.0"
                ))

            # 產生新token
            token, timestamp = generate_token(device_serial)

            # 寫入tokens表
            sql_token = '''
                INSERT INTO tokens (device_serial, token, created_at, used)
                VALUES (%s, %s, FROM_UNIXTIME(%s), 0)
            '''
            cursor.execute(sql_token, (device_serial, token, timestamp))
        
        db.commit()

        # 產生 QR code
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=2
        )
        bind_url = f"http://192.168.0.48:307/bind/{token}"
        qr.add_data(bind_url)

        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()

        return jsonify({
            "qr_base64": qr_base64
        })

    except Exception as e:
        print(f"錯誤：{e}")
        return jsonify({"message": "伺服器錯誤"}), 500
