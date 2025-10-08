# config.py
"""
MDG 車機系統設定檔
"""

# Demo 模式開關
DEMO_MODE = True

# 伺服器設定
SERVER_URL = "http://172.20.10.3:307"

# Flask 應用設定
APP_CONFIG = {
    'SECRET_KEY': 'your-secret-key-change-this',
    'DEBUG': True,
    'HOST': '0.0.0.0',
    'PORT': 5003
}

# GPIO 設定（方向燈、倒車檔、車速）
GPIO_CONFIG = {
    'MAC_PORT': '/dev/cu.usbmodem1401',
    'RASPI_PORT': '/dev/ttyACM0',
    'BAUD_RATE': 115200,
    'TIMEOUT': 1
}

# RTSP 攝影機設定（正式環境）
CAMERA_URLS = {
    # "inside": "rtsp://admin:123456@192.168.100.10/stream1",
    # "outside": "rtsp://admin:123456@192.168.100.12/stream1"
    "inside": 0,  # 筆電攝影機（測試用）
    "outside": "demo/test_videos/test_outsideCamera.mov"  # 改成正確的檔名
}

# Demo 攝影機設定
if DEMO_MODE:
    CAMERA_SOURCES = {
        "inside": 0,  # 筆電攝影機
        "outside": "demo/test_videos/test_outsideCamera.mov"  # 改成正確的檔名
    }
else:
    CAMERA_SOURCES = CAMERA_URLS

# 攝影機相關設定
CAMERA_CONFIG = {
    'FRAME_WIDTH': 640,
    'FRAME_HEIGHT': 480,
    'FPS': 30,
    'BUFFER_SIZE': 1,
    'RECONNECT_TIMEOUT': 5,
    'MAX_RECONNECT_ATTEMPTS': 3
}

# Demo GPIO 鍵盤控制
DEMO_GPIO_KEYS = {
    'left_turn': 'a',
    'right_turn': 'd',
    'reverse': 's',
    'speed_up': 'w',
    'speed_down': 'x',
    'reset': 'q'
}