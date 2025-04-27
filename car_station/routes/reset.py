from flask import Blueprint, render_template, request
import sqlite3
import requests

reset_bp = Blueprint('reset', __name__)

DEVICE_SERIAL = "mdgcs001"
SERVER_URL = "http://192.168.0.48:307" # Server端位置
@reset_bp.route('/reset_device_info', methods=['POST'])
def reset_device_info():
    # 本地清除SQLite資料
    conn = sqlite3.connect('device.db')
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE devices
        SET car_brand = NULL, car_plate = NULL, vehicle_type = NULL, driver_position = NULL, status = 'offline'
        WHERE device_serial = ?
    ''', (DEVICE_SERIAL,))

    conn.commit()
    conn.close()

    # 呼叫Server端產生reset QR
    try:
        response = requests.post(f"{SERVER_URL}/generate_reset_token", json={"device_serial": DEVICE_SERIAL})
        if response.status_code == 200:
            data = response.json()
            qr_base64 = data.get('qr_base64')
            return render_template('reset_qr.html', qr_base64=qr_base64)
        else:
            return "⚠️ 伺服器產生Reset QR失敗", 500
    except Exception as e:
        print(f"錯誤：{e}")
        return "⚠️ 連線伺服器失敗", 500

@reset_bp.route('/reset_success')
def reset_success():
    return render_template('reset_success.html')
