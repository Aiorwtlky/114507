from flask import Blueprint, request, jsonify, render_template
from db import db

manage_bp = Blueprint('device', __name__)

# 首頁按鈕：管理駕駛 → 跳轉表單
@manage_bp.route('/manage_driver', methods=['GET'])
def manage_driver():
    return render_template('driver_manage.html')

# 駕駛新增表單頁
@manage_bp.route('/driver_form', methods=['GET'])
def driver_form():
    return render_template('add_driver_form.html')
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from db import db

manage_bp = Blueprint('device', __name__)

# 首頁按鈕：管理駕駛 → 跳轉表單
@manage_bp.route('/manage_driver', methods=['GET'])
def manage_driver():
    return render_template('driver_manage.html')

# 駕駛新增表單頁
@manage_bp.route('/driver_form', methods=['GET'])
def driver_form():
    return render_template('add_driver_form.html')

# 寫入駕駛資料
@manage_bp.route('/add_driver', methods=['POST'])
def add_driver():
    try:
        driver_id = request.form.get('driver_id')
        driver_name = request.form.get('driver_name')

        with db.cursor() as cursor:
            sql = "INSERT INTO drivers (driver_id, driver_name) VALUES (%s, %s)"
            cursor.execute(sql, (driver_id, driver_name))

        db.commit()
        return render_template('register_success.html')
    except Exception as e:
        return render_template('register_error.html', message=str(e))