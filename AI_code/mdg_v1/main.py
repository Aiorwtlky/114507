import cv2
import numpy as np
from ultralytics import YOLO
from event_manager import save_event
import time
import subprocess

# 初始化模型與攝影機
model = YOLO("models/yolov8n.pt")
cap = cv2.VideoCapture(0)

device_serial = "RPi-0001"
cooldown_time = 20  # 單位秒
last_trigger_time = 0
roi_config = {
    "right_cam": [(100, 100), (300, 100), (300, 300), (100, 300)]
}

def is_inside_roi(center, roi_polygon):
    return cv2.pointPolygonTest(np.array(roi_polygon, dtype=np.int32), center, False) >= 0

print("系統啟動，按 Q 鍵離開")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, stream=True)

    for result in results:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            # 畫框
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            if label == "person":
                roi_polygon = roi_config["right_cam"]
                if is_inside_roi((cx, cy), roi_polygon):
                    current_time = time.time()
                    if current_time - last_trigger_time > cooldown_time:
                        print("🎯 偵測到進入 ROI，開始儲存事件")
                        save_event(
                            image=frame,
                            record_duration=15,
                            object_type="person",
                            location="right_cam",
                            device_serial=device_serial
                        )
                        last_trigger_time = current_time

    # 畫出 ROI 區域
    roi_polygon = roi_config["right_cam"]
    cv2.polylines(frame, [np.array(roi_polygon, dtype=np.int32)], isClosed=True, color=(255, 255, 0), thickness=2)

    cv2.imshow("WebCam", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
