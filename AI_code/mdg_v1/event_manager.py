# event_manager.py

import os
import cv2
import json
from datetime import datetime
from firebase_helper import upload_event_metadata
import shutil

def save_event(image, video_path=None, object_type=None, location=None, device_serial=None):
    """
    儲存一筆事件：圖片、影片（可選）、meta.json，並上傳事件資料至 Firestore。
    """

    # 產生資料夾名稱（依時間）
    timestamp = datetime.now()
    folder_name = timestamp.strftime("%Y%m%d_%H%M%S")
    save_path = os.path.join("events", folder_name)
    os.makedirs(save_path, exist_ok=True)

    # 儲存圖片
    image_filename = os.path.join(save_path, "alert.jpg")
    cv2.imwrite(image_filename, image)

    # 儲存影片（如果有）
    if video_path and os.path.exists(video_path):
        video_filename = os.path.join(save_path, "clip.mp4")
        shutil.copy(video_path, video_filename)
    else:
        video_filename = None

    # 建立事件 JSON 紀錄
    metadata = {
        "timestamp": timestamp.isoformat(),
        "object_type": object_type,
        "location": location,
        "event_type": "outside_roi_intrusion",
        "image_path": image_filename,
        "video_path": video_filename,
        "device_serial": device_serial
    }

    with open(os.path.join(save_path, "meta.json"), "w") as f:
        json.dump(metadata, f, indent=4)

    # 上傳至 Firestore
    upload_event_metadata(metadata)
