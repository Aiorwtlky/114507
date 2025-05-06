from flask import Blueprint, render_template, request, jsonify
import sqlite3
import requests
from routes.config import SERVER_URL, DB_PATH  # ✅ 引入 Server URL 與正確的 DB 路徑

install_bp = Blueprint('install', __name__)

DEVICE_SERIAL = "mdgcs001"  # 車機序號

@install_bp.route('/install', methods=['GET'])
def install():
    try:
        # 註冊設備（產生 QR）
        reg_res = requests.post(f"{SERVER_URL}/register_device", json={"device_serial": DEVICE_SERIAL})
        if reg_res.status_code != 200:
            return "⚠️ 註冊失敗", 500

        data = reg_res.json()
        qr_base64 = data.get('qr_base64')

        # 嘗試同步綁定資料
        sync_res = requests.post(f"{SERVER_URL}/sync_device", json={"device_serial": DEVICE_SERIAL})
        if sync_res.status_code == 200:
            sync_data = sync_res.json()
            if sync_data.get("status") == "bound":
                # 寫入 SQLite（呼叫本地 route 儲存資料）
                requests.post("http://127.0.0.1:730/save_device_info", json={
                    "car_brand": sync_data.get("car_brand"),
                    "car_plate": sync_data.get("car_plate"),
                    "vehicle_type": sync_data.get("vehicle_type"),
                    "driver_position": sync_data.get("driver_position")
                })

        return render_template('install.html', qr_base64=qr_base64)

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

    try:
        conn = sqlite3.connect(DB_PATH)  # ✅ 使用正確的資料庫路徑
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
            DEVICE_SERIAL
        ))

        conn.commit()
        conn.close()
        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@install_bp.route('/install_success')
def install_success():
    return render_template('install_success.html')
