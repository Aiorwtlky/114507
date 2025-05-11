# main.py
import numpy as np
import cv2
import json
import os
from datetime import datetime
from ultralytics import YOLO
from event_manager import save_event

# 初始化 YOLO 模型
model = YOLO("models/yolov8n.pt")

# 讀取 ROI 設定
with open("config/roi_config.json") as f:
    roi_config = json.load(f)

# 讀取裝置資訊
with open("config/device_info.json") as f:
    device_info = json.load(f)
device_serial = device_info["device_serial"]

# 設定測試影片路徑
test_video_path = "static/test1.mp4"
if not os.path.exists(test_video_path):
    print("⚠️ 找不到測試影片，影片儲存將略過")
    test_video_path = None

# 開啟 WebCam（index=0）
cap = cv2.VideoCapture(0)
already_triggered = False

def is_inside_roi(center, roi_points):
    return cv2.pointPolygonTest(roi_points, center, False) >= 0

print("系統啟動，按 Q 鍵離開")

while True:
    ret, frame = cap.read()
    if not ret:
        print("攝影機讀取失敗")
        break

    results = model(frame)

    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]

            if label == "person":
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                roi_points = roi_config["right_cam"]
                roi_polygon = np.array(roi_points, dtype=np.int32)


                if is_inside_roi((cx, cy), roi_polygon):
                    if not already_triggered:
                        print("人物進入 ROI，觸發事件")

                        save_event(
                            image=frame,
                            video_path=test_video_path,
                            object_type="person",
                            location="right_cam",
                            device_serial=device_serial
                        )
                        already_triggered = True
                else:
                    already_triggered = False

    cv2.imshow("WebCam", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
