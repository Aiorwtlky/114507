from flask import Flask, Response, render_template
import cv2
import camera_config as cfg
import numpy as np
import time

app = Flask(__name__)

def open_stream(url):
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        cap.release()
        cap = None
    return cap

def blank_frame(text="NO FEED", w=640, h=480):
    frame = np.full((h, w, 3), 220, dtype=np.uint8)      # 淡灰底
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
        time.sleep(0.03)          # ≈30 fps

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video/<cam_id>')
def video(cam_id):
    return Response(gen(cam_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    import sys
    # 若執行時帶參數 → 用該 port，否則預設 5000
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    app.run(host='0.0.0.0', port=port, threaded=True)
