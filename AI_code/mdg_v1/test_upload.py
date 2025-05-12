# test_upload.py

from firebase_helper import upload_event_metadata
from datetime import datetime

event_data = {
    "timestamp": datetime.utcnow().isoformat(),
    "object_type": "person",
    "location": "right_cam",
    "event_type": "outside_roi_intrusion",
    "image_path": "/events/20240511_203105/alert.jpg",
    "video_path": "/events/20240511_203105/clip.mp4",
    "device_serial": "RPi-0001"
}

upload_event_metadata(event_data)
