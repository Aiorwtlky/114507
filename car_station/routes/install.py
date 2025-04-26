from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3

install_bp = Blueprint('install', __name__)

@install_bp.route('/install', methods=['GET', 'POST'])
def install():
    if request.method == 'POST':
        car_brand = request.form.get('car_brand')
        car_plate = request.form.get('car_plate')
        vehicle_type = request.form.get('vehicle_type')
        driver_position = request.form.get('driver_position')

        conn = sqlite3.connect('device.db')
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE devices
            SET car_brand = ?, car_plate = ?, vehicle_type = ?, driver_position = ?
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

        print("✅ 安裝設定成功，設備資料已更新！")

        return render_template('install_success.html')

    return render_template('install.html')
