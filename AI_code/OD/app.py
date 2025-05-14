from flask import Flask, render_template, Response, jsonify, request
import cv2
from ultralytics import YOLO
import threading
import time
from datetime import datetime

app = Flask(__name__)

cap = cv2.VideoCapture(0)
model = YOLO('yolov8n.pt')

lock = threading.Lock()
detected_objects = []

recorded_logs = []    # 存放 (timestamp, [物件列表])
recording = False     # 是否正在紀錄
record_thread = None

def record_loop():
    global recording, recorded_logs, detected_objects, lock
    while recording:
        time.sleep(15)
        with lock:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            objs = detected_objects.copy()
            recorded_logs.append((now, objs))
            print(f"[Record] {now}: {objs}")  # 確保有印


def gen_frames():
    global detected_objects

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (640, 480))
        results = model(frame)[0]

        objs = []
        for r in results.boxes.data.tolist():
            x1, y1, x2, y2, conf, cls = r
            label = model.names[int(cls)]
            objs.append(label)
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0,255,0), 2)
            cv2.putText(frame, f"{label} {conf:.2f}", (int(x1), int(y1)-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

        with lock:
            detected_objects = objs.copy()

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detected')
def detected():
    with lock:
        objs = detected_objects.copy()
    unique = list(set(objs))
    return jsonify(objects=unique)

@app.route('/start_recording', methods=['POST'])
def start_recording():
    global recording, record_thread
    if not recording:
        recording = True
        record_thread = threading.Thread(target=record_loop, daemon=True)
        record_thread.start()
        print("[Info] Recording thread started")
        return {'status': 'recording_started'}
    else:
        return {'status': 'already_recording'}


@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global recording
    recording = False
    return {'status': 'recording_stopped'}

@app.route('/records')
def records():
    with lock:
        logs = recorded_logs.copy()
    # 回傳時間與物件紀錄
    return jsonify(records=[{'time': t, 'objects': o} for t,o in logs])

if __name__ == '__main__':
    app.run(debug=False, threaded=True, use_reloader=False)