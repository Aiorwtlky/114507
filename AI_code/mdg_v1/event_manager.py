import os
import cv2
import json
from datetime import datetime
from firebase_helper import upload_event_metadata

def record_video(save_path, duration=15, fps=20):
    """
    使用 WebCam 即時錄製影片。
    """
    cap = cv2.VideoCapture(0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(save_path, fourcc, fps, (width, height))

    total_frames = int(duration * fps)
    for _ in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    cap.release()
    out.release()


def save_event(image, record_duration=15, object_type=None, location=None, device_serial=None):
    """
    儲存一筆事件：擷取圖片、錄製影片、建立 meta.json，並上傳 Firestore。
    """
    # 產生時間戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    event_dir = os.path.join("events", timestamp)
    os.makedirs(event_dir, exist_ok=True)

    # 儲存圖片（命名含 timestamp）
    image_filename = f"{timestamp}_alert.jpg"
    image_path = os.path.join(event_dir, image_filename)
    cv2.imwrite(image_path, image)

    # 錄製影片（duration 秒）
    video_filename = f"{timestamp}_clip.mp4"
    video_path = os.path.join(event_dir, video_filename)
    record_video(video_path, duration=record_duration)

    # 建立 meta.json
    metadata = {
        "timestamp": timestamp,
        "object_type": object_type,
        "location": location,
        "event_type": "outside_roi_intrusion",
        "image_path": os.path.basename(image_path),
        "video_path": os.path.basename(video_path),
        "device_serial": device_serial
    }

    with open(os.path.join(event_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

    # 上傳 Firestore
    upload_event_metadata(metadata)
    print(f" 事件儲存成功：{event_dir}")
