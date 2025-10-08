from flask import Blueprint, render_template, request, redirect, url_for
from db import db
from utils.token_manager import verify_token
import time

bind_bp = Blueprint('bind', __name__)

@bind_bp.route('/bind/<token>', methods=['GET', 'POST'])
def bind_device(token):
    try:
        with db.cursor() as cursor:
            # 查詢token資料
            sql = "SELECT * FROM tokens WHERE token = %s"
            cursor.execute(sql, (token,))
            token_data = cursor.fetchone()

            if not token_data:
                return render_template('bind_error.html', message="無效的Token！")

            if token_data['used'] == 1:
                return render_template('bind_error.html', message="Token已被使用！")

            created_time = int(token_data['created_at'].timestamp())
            if not verify_token(created_time):
                return render_template('bind_error.html', message="Token已過期！")

            device_serial = token_data['device_serial']

            if request.method == 'POST':
                car_brand = request.form.get('car_brand')
                car_plate = request.form.get('car_plate')
                vehicle_type = request.form.get('vehicle_type')
                driver_position = request.form.get('driver_position')

                # 更新設備資料
                update_sql = '''
                    UPDATE devices
                    SET car_brand=%s, car_plate=%s, vehicle_type=%s, driver_position=%s, bind_status=1
                    WHERE device_serial=%s
                '''
                cursor.execute(update_sql, (
                    car_brand,
                    car_plate,
                    vehicle_type,
                    driver_position,
                    device_serial
                ))

                # 標記token已使用
                cursor.execute('UPDATE tokens SET used=1 WHERE token=%s', (token,))
                
                db.commit()

                return render_template('bind_success.html')

            return render_template('bind_form.html', device_serial=device_serial)

    except Exception as e:
        print(f"錯誤：{e}")
        return render_template('bind_error.html', message="伺服器錯誤！")
