import torch
import cv2
import time
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# 讀取 YOLOv5 模型
model = torch.hub.load('ultralytics/yolov5', 'yolov5n', pretrained=True)

# 初始攝影機設定
camera_index = 0
cap = cv2.VideoCapture(camera_index)

def set_camera_index(new_index):
    global cap, camera_index
    camera_index = new_index
    cap.release()
    cap = cv2.VideoCapture(camera_index)
    print(f"[INFO] 手動切換至攝影機 {camera_index}")

_latest_status = {
    "status": "safe",
    "object": None,
    "danger": False,
    "objects": [],
    "last_updated": time.time()
}

def get_detection_status():
    global _latest_status, cap

    ret, frame = cap.read()
    if not ret or frame is None:
        return _latest_status

    results = model(frame)

    detected_objects = []
    for *box, conf, cls in results.xyxy[0]:
        label = model.names[int(cls)]
        detected_objects.append(label)

    detected = 'person' in detected_objects
    unique_objects = list(set(detected_objects))

    _latest_status = {
        "status": "danger" if detected else "safe",
        "object": "行人" if detected else None,
        "danger": detected,
        "objects": unique_objects,
        "last_updated": time.time()
    }

    return {
        "status": _latest_status["status"],
        "object": _latest_status["object"],
        "danger": _latest_status["danger"],
        "objects": _latest_status["objects"]
    }

def get_stream_frame():
    global cap, camera_index
    prev_time = time.time()

    while True:
        if not cap.isOpened():
            cap = cv2.VideoCapture(camera_index)
            time.sleep(1)
            continue

        ret, frame = cap.read()
        if not ret or frame is None:
            time.sleep(0.1)
            continue

        # YOLO 辨識與畫框
        results = model(frame)
        for *xyxy, conf, cls in results.xyxy[0]:
            label = model.names[int(cls)]
            x1, y1, x2, y2 = map(int, xyxy)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 128, 255), 2)
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 128, 255), 2)

        # FPS 與鏡頭 index 顯示
        curr_time = time.time()
        fps = 1.0 / (curr_time - prev_time)
        prev_time = curr_time
        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 50, 50), 2)
        cv2.putText(frame, f"Cam Index: {camera_index}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 255, 100), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
