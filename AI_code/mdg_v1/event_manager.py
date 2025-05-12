import os
import cv2
import json
from datetime import datetime
from firebase_helper import upload_event_metadata
import subprocess

def record_video_ffmpeg(save_path, duration=15):
    """
    使用 FFmpeg 錄製影片（需安裝 FFmpeg 並在系統 PATH 中）
    """
    command = [
        'ffmpeg',
        '-y',  # 覆蓋輸出
        '-f', 'dshow',
        '-i', 'video=Integrated Camera',  # 視訊設備名稱（依你的電腦調整）
        '-t', str(duration),
        '-vcodec', 'libx264',
        '-preset', 'ultrafast',
        save_path
    ]
    try:
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"FFmpeg 錄影失敗: {e}")

def save_event(image, record_duration=15, object_type=None, location=None, device_serial=None):
    """
    儲存一筆事件：包含截圖、錄影、meta.json 並上傳 metadata。
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_path = os.path.join("events", timestamp)
    os.makedirs(folder_path, exist_ok=True)

    image_filename = f"{timestamp}_alert.jpg"
    video_filename = f"{timestamp}_clip.mp4"

    image_path = os.path.join(folder_path, image_filename)
    cv2.imwrite(image_path, image)

    video_path = os.path.join(folder_path, video_filename)
    record_video_ffmpeg(video_path, duration=record_duration)

    metadata = {
        "timestamp": timestamp,
        "object_type": object_type,
        "location": location,
        "event_type": "outside_roi_intrusion",
        "image_path": image_filename,
        "video_path": video_filename,
        "device_serial": device_serial
    }

    with open(os.path.join(folder_path, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

    upload_event_metadata(metadata)
    print(f"✅ 事件儲存成功：{folder_path}")
