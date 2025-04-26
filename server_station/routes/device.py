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
