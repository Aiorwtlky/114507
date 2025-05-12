from flask import Flask, render_template, Response
import cv2
from ultralytics import YOLO
import numpy as np

app = Flask(__name__)

# 初始化模型與攝影機
model = YOLO("models/yolov8n.pt")
cap = cv2.VideoCapture(0)
roi_polygon = [(100, 100), (300, 100), (300, 300), (100, 300)]  # 可根據需求調整


def is_inside_roi(center, roi_polygon):
    return cv2.pointPolygonTest(np.array(roi_polygon, dtype=np.int32), center, False) >= 0


def generate_stream():
    while True:
        success, frame = cap.read()
        if not success:
            break

        results = model(frame, stream=True)

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                label = model.names[cls_id]
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                if label == "person":
                    color = (0, 0, 255) if is_inside_roi((cx, cy), roi_polygon) else (0, 255, 0)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # 畫出 ROI 區域
        cv2.polylines(frame, [np.array(roi_polygon, dtype=np.int32)], isClosed=True, color=(255, 255, 0), thickness=2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route("/video_feed")
def video_feed():
    return Response(generate_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/camera")
def camera():
    return render_template("camera.html")


if __name__ == '__main__':
    app.run(debug=True)
