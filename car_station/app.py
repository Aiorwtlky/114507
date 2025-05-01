from flask import Flask, Response, render_template, redirect, url_for
import cv2
import camera_config as cfg
import numpy as np
import time
import sqlite3
import requests  # 加在最上面
from routes.config import SERVER_URL
from routes.install import install_bp
from routes.device import device_bp
from routes.reset import reset_bp
from routes.gpio import gpio_bp
import logging

logging.basicConfig(filename='flask.log', level=logging.INFO)


app = Flask(__name__)
app.config['SERVER_URL'] = SERVER_URL

#Blueprint
app.register_blueprint(install_bp)
app.register_blueprint(device_bp)
app.register_blueprint(reset_bp)
app.register_blueprint(gpio_bp)

def open_stream(url):
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        cap.release()
        cap = None
    return cap

def blank_frame(text="NO FEED", w=640, h=480):
    frame = np.full((h, w, 3), 220, dtype=np.uint8)
    cv2.putText(frame, text, (40, h // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
    return frame

def gen(camera_id):
    url = cfg.CAMERA_URLS[camera_id]
    cap = open_stream(url)

    while True:
        if cap:
            ok, frame = cap.read()
            if not ok:
                cap.release()
                cap = None
        if not cap:
            frame = blank_frame(f"{camera_id.upper()} OFFLINE")

        _, buffer = cv2.imencode('.jpg', frame)
        jpg_bytes = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' +
               jpg_bytes + b'\r\n')
        time.sleep(0.03)  # ≈30 fps

#修改 index()，開機時自動檢查是否需要設定
@app.route('/')
def index():
    conn = sqlite3.connect('device.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT car_brand, car_plate, vehicle_type, driver_position
        FROM devices WHERE device_serial = ?
    ''', ('mdgcs001',))
    device = cursor.fetchone()
    conn.close()

    print('📦 裝置欄位：', device)

    qr_base64 = None
    if device and all(field not in (None, '') for field in device):
        # ✅ 裝置資料齊全，取得 Server 的上班 QR Code
        try:
            res = requests.get("http://192.168.0.100:307/generate_qr/work")
            if res.status_code == 200:
                qr_base64 = res.json().get('qr_base64')
            else:
                print("⚠️ 從 Server 取得 QR 失敗")
        except Exception as e:
            print(f"❌ 無法連線 Server：{e}")

        logging.info('✅ 完整資料，跳 index.html')
        return render_template('index.html', qr_base64=qr_base64)

    elif device and any(field not in (None, '') for field in device):
        # ✅ 部分資料，跳轉安裝成功頁（只顯示一次）
        if not os.path.exists('shown_success.flag'):
            with open('shown_success.flag', 'w') as f:
                f.write('shown')
            logging.info('🟡 第一次安裝完成，跳 install_success.html')
            return render_template('install_success.html')
        else:
            return render_template('index.html', qr_base64=None)

    else:
        logging.info('❌ 沒資料，跳 install 設定頁')
        return redirect(url_for('install.install'))



@app.route('/work_state')
def work_state():
    try:
        res = requests.get("http://192.168.0.100:307/generate_qr/off")
        qr_base64 = None
        if res.status_code == 200:
            qr_base64 = res.json().get('qr_base64')
        else:
            print("⚠️ 從 Server 取得 QR 失敗")
    except Exception as e:
        print(f"❌ 無法連線 Server：{e}")
        qr_base64 = None

    return render_template('work_state.html', qr_base64=qr_base64)

@app.route('/video/<cam_id>')
def video(cam_id):
    return Response(gen(cam_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    import sys
    import threading
    import webbrowser
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 730
    threading.Timer(1.0, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    print(f"🚀 Flask 啟動中，port = {port}")
    app.run(host='0.0.0.0', port=port, threaded=True)
