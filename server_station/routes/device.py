from flask import Blueprint, request, jsonify
from db import db

device_bp = Blueprint('device', __name__)

@device_bp.route('/add_device', methods=['POST'])
def add_device():
    data = request.get_json()
    try:
        with db.cursor() as cursor:
            sql = '''
                INSERT INTO devices (device_serial, manufacturer, manufacturer_address, software_version)
                VALUES (%s, %s, %s, %s)
            '''
            cursor.execute(sql, (
                data['device_serial'],
                data['manufacturer'],
                data['manufacturer_address'],
                data['software_version']
            ))
        db.commit()
        return jsonify({"message": "設備新增成功"})
    except Exception as e:
        return jsonify({"message": f"新增失敗：{str(e)}"})

@device_bp.route('/get_device/<device_serial>', methods=['GET'])
def get_device(device_serial):
    with db.cursor() as cursor:
        sql = 'SELECT * FROM devices WHERE device_serial = %s'
        cursor.execute(sql, (device_serial,))
        device = cursor.fetchone()
        if device:
            return jsonify(device)
        else:
            return jsonify({"message": "查無此設備"})

@device_bp.route('/sync_device', methods=['POST'])
def sync_device():
    data = request.get_json()
    device_serial = data.get('device_serial')

    try:
        with db.cursor() as cursor:
            sql = 'SELECT car_brand, car_plate, vehicle_type, driver_position, bind_status FROM devices WHERE device_serial = %s'
            cursor.execute(sql, (device_serial,))
            device = cursor.fetchone()

            if not device:
                return jsonify({"message": "設備不存在"}), 404

            if device['bind_status'] == 1:
                return jsonify({
                    "status": "bound",
                    "car_brand": device['car_brand'],
                    "car_plate": device['car_plate'],
                    "vehicle_type": device['vehicle_type'],
                    "driver_position": device['driver_position']
                })
            else:
                return jsonify({"status": "pending"})

    except Exception as e:
        print(f"錯誤：{e}")
        return jsonify({"message": "伺服器錯誤"}), 500