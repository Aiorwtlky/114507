from flask import Blueprint, render_template
import sqlite3

reset_bp = Blueprint('reset', __name__)

@reset_bp.route('/reset_device_info', methods=['POST'])
def reset_device_info():
    conn = sqlite3.connect('device.db')
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE devices
        SET car_brand = NULL, car_plate = NULL, vehicle_type = NULL, driver_position = NULL
        WHERE device_serial = ?
    ''', ('mdgcs001',))

    conn.commit()
    conn.close()
    return '', 200

@reset_bp.route('/reset_success', methods=['GET'])
def reset_success():
    return render_template('reset_success.html')

