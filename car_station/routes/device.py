from flask import Blueprint, jsonify
import sqlite3
from routes.config import DB_PATH  # ✅ 引入統一資料庫路徑

device_bp = Blueprint('device', __name__)

@device_bp.route('/device_info', methods=['GET'])
def device_info():
    try:
        conn = sqlite3.connect(DB_PATH)  # ✅ 使用正確路徑
        cursor = conn.cursor()

        cursor.execute('''
            SELECT manufacturer, manufacturer_address, device_serial, software_version,
                   car_brand, car_plate, vehicle_type, driver_position
            FROM devices
            WHERE device_serial = ?
        ''', ('mdgcs001',))

        row = cursor.fetchone()
        conn.close()

        if row:
            keys = ["manufacturer", "manufacturer_address", "device_serial", "software_version",
                    "car_brand", "car_plate", "vehicle_type", "driver_position"]
            data = dict(zip(keys, row))
            return jsonify(data)
        else:
            return jsonify({"error": "Device not found"}), 404

    except Exception as e:
        return jsonify({"error": f"資料庫錯誤：{str(e)}"}), 500
