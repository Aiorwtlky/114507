from flask import Blueprint, render_template, request
import sqlite3
import requests
from routes.config import SERVER_URL, DB_PATH  # ✅ 加入 DB_PATH

reset_bp = Blueprint('reset', __name__)

DEVICE_SERIAL = "mdgcs001"

@reset_bp.route('/reset_device_info', methods=['POST'])
def reset_device_info():
    try:
        # ✅ 本地清除 SQLite 資料
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE devices
            SET car_brand = NULL, car_plate = NULL, vehicle_type = NULL, driver_position = NULL, status = 'offline'
            WHERE device_serial = ?
        ''', (DEVICE_SERIAL,))

        conn.commit()
        conn.close()

        # ✅ 呼叫伺服器產生 reset QR
        response = requests.post(f"{SERVER_URL}/generate_reset_token", json={"device_serial": DEVICE_SERIAL})
        if response.status_code == 200:
            data = response.json()
            qr_base64 = data.get('qr_base64')
            return render_template('reset_qr.html', qr_base64=qr_base64)
        else:
            return "⚠️ 伺服器產生Reset QR失敗", 500

    except Exception as e:
        print(f"錯誤：{e}")
        return "⚠️ 連線或寫入失敗", 500


@reset_bp.route('/reset_success')
def reset_success():
    return render_template('reset_success.html')
