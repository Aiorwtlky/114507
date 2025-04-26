from flask import Blueprint, render_template, request, jsonify
import sqlite3
import requests

install_bp = Blueprint('install', __name__)

DEVICE_SERIAL = "mdgcs001"  # 車機序號
SERVER_URL = "http://localhost:307"  # Server端位置

@install_bp.route('/install', methods=['GET'])
def install():
    try:
        response = requests.post(f"{SERVER_URL}/register_device", json={"device_serial": DEVICE_SERIAL})
        if response.status_code == 200:
            data = response.json()
            qr_base64 = data.get('qr_base64')
            return render_template('install.html', qr_base64=qr_base64)
        else:
            return "⚠️ 註冊失敗，請稍後再試", 500
    except Exception as e:
        print(f"連線錯誤：{e}")
        return "⚠️ 無法連線伺服器", 500
    
@install_bp.route('/save_device_info', methods=['POST'])
def save_device_info():
    data = request.get_json()

    car_brand = data.get('car_brand')
    car_plate = data.get('car_plate')
    vehicle_type = data.get('vehicle_type')
    driver_position = data.get('driver_position')

    conn = sqlite3.connect('device.db')
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE devices
        SET car_brand = ?, car_plate = ?, vehicle_type = ?, driver_position = ?, status = 'online'
        WHERE device_serial = ?
    ''', (
        car_brand,
        car_plate,
        vehicle_type,
        driver_position,
        "mdgcs001"
    ))

    conn.commit()
    conn.close()

    return jsonify({"success": True})

@install_bp.route('/install_success')
def install_success():
    return render_template('install_success.html')
