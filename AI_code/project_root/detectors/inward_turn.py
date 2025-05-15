import cv2
from ultralytics import YOLO
import numpy as np

model = YOLO("yolov8n.pt")

def detect_inward(frame):
    results = model(frame)[0]
    h, w = frame.shape[:2]

    inward_zone = None
    alerts = []

    # 搜尋所有目標
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls = int(box.cls[0])
        label = model.names[cls]

        # 若為車輛（目標車），畫車框，模擬內輪差區域
        if label in ['car', 'truck', 'bus']:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # 根據車框模擬內輪差區域（右下方偏移區域）
            offset_x = int((x2 - x1) * 0.3)
            offset_y = int((y2 - y1) * 0.4)

            inward_zone = np.array([
                [x2, y2],
                [x2 + offset_x, y2],
                [x2 + offset_x, y2 + offset_y],
                [x2, y2 + offset_y]
            ])

            # 繪製內輪差區域
            cv2.polylines(frame, [inward_zone], isClosed=True, color=(255, 0, 0), thickness=2)
            cv2.putText(frame, "Inward Zone", (x2, y2 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

    # 檢查其他物件是否進入內輪差區域
    if inward_zone is not None:
        for box in results.boxes:
            cls = int(box.cls[0])
            label = model.names[cls]
            if label not in ['person', 'bicycle', 'motorbike']:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

            if cv2.pointPolygonTest(inward_zone, (center_x, center_y), False) >= 0:
                # 入侵警示
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, f"{label} ALERT", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                alerts.append(label)

    return frame
