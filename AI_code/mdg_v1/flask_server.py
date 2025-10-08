import os
import cv2
import numpy as np
from flask import Flask, render_template, Response
from ultralytics import YOLO
from event_manager import save_event
import time
from collections import deque

app = Flask(__name__)

model = YOLO("models/yolov8n.pt")
cap = cv2.VideoCapture(0)
roi_polygon = [(100, 100), (300, 100), (300, 300), (100, 300)]

frame_buffer = deque(maxlen=200)  # 儲存前10秒影格（20fps）
after_trigger_frames = []
triggered = False
last_event_time = 0
cooldown = 20  # 秒
recording_time = 10  # 事件發生後錄影秒數
fps = 20


def is_inside_roi(center, roi_polygon):
    return cv2.pointPolygonTest(np.array(roi_polygon, dtype=np.int32), center, False) >= 0


def generate_stream():
    global triggered, last_event_time, after_trigger_frames
    recording = False
    record_start_time = None

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame_buffer.append(frame.copy())
        results = model(frame, stream=True)

        detected = False

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                label = model.names[cls_id]
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                if label == "person" and is_inside_roi((cx, cy), roi_polygon):
                    detected = True

                color = (0, 0, 255) if is_inside_roi((cx, cy), roi_polygon) else (0, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        cv2.polylines(frame, [np.array(roi_polygon, dtype=np.int32)], isClosed=True, color=(255, 255, 0), thickness=2)

        if detected and not triggered and (time.time() - last_event_time > cooldown):
            print("🔔 事件觸發！")
            triggered = True
            recording = True
            record_start_time = time.time()
            after_trigger_frames = []
            last_event_time = time.time()

        if recording:
            after_trigger_frames.append(frame.copy())
            if time.time() - record_start_time >= recording_time:
                # 合併前後影格並儲存
                full_clip = list(frame_buffer) + after_trigger_frames

                height, width, _ = full_clip[0].shape
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                folder = f"events/{timestamp}"
                os.makedirs(folder, exist_ok=True)
                video_path = f"{folder}/{timestamp}_clip.mp4"
                out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
                for f in full_clip:
                    out.write(f)
                out.release()

                # 儲存 alert.jpg（最後一張）
                alert_path = f"{folder}/{timestamp}_alert.jpg"
                cv2.imwrite(alert_path, frame)

                # 呼叫 save_event 寫入 meta.json
                save_event(
                    image=frame,
                    record_duration=0,  # FFmpeg 不用
                    object_type="person",
                    location="right_cam",
                    device_serial="RPi-0001"
                )

                recording = False
                triggered = False

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(generate_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/camera")
def camera():
    return render_template("camera.html")


if __name__ == '__main__':
    app.run(debug=True)
