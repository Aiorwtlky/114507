from flask import Flask, Response, render_template, redirect, url_for
import cv2
import camera_config as cfg
import numpy as np
import time
import sqlite3
from routes.install import install_bp
from routes.device import device_bp
from routes.reset import reset_bp

app = Flask(__name__)

#Blueprint
app.register_blueprint(install_bp)
app.register_blueprint(device_bp)
app.register_blueprint(reset_bp)

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
    cursor.execute('SELECT car_plate, car_brand, vehicle_type, driver_position FROM devices WHERE device_serial = ?', ('mdgcs001',))
    device = cursor.fetchone()
    conn.close()

    # 如果車輛資料還沒填，就跳去安裝設定頁
    if device is None or None in device or '' in device:
        return redirect(url_for('install.install'))

    return render_template('index.html')

@app.route('/video/<cam_id>')
def video(cam_id):
    return Response(gen(cam_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 730
    app.run(host='0.0.0.0', port=port, threaded=True)
