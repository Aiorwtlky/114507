# config.py
"""
MDG 車機系統設定檔
⚠️ 重要：所有設定都在這裡統一管理，請勿在其他檔案中寫死網址或設定值！
"""

# ==============================================
# 🌐 伺服器設定 - 只要在這裡改一個地方就好！
# ==============================================
SERVER_URL = "http://172.20.10.3:307"

# 未來 HTTPS 設定預留（取消註解即可切換）
# SERVER_URL = "https://your-domain.com"

# Flask 應用設定
APP_CONFIG = {
    'SECRET_KEY': 'your-secret-key-change-this',
    'DEBUG': True,
    'HOST': '0.0.0.0',
    'PORT': 5003
}

# 🔧 硬體通訊設定（GPIO + GPS 使用同一個序列埠）
HARDWARE_CONFIG = {
    'MAC_PORT': '/dev/cu.usbmodem1401',    # Mac 開發環境
    'RASPI_PORT': '/dev/ttyACM0',         # Raspberry Pi 實作環境
    'BAUD_RATE': 115200,
    'TIMEOUT': 2  # 統一超時時間
}

# GPIO 設定（方向燈、倒車檔）
GPIO_CONFIG = {
    **HARDWARE_CONFIG,  # 繼承硬體設定
    'TIMEOUT': 1  # GPIO 可以用較短超時
}

# GPS 設定（NEO-6M 經由 Pico2）
GPS_CONFIG = {
    **HARDWARE_CONFIG,  # 繼承硬體設定
    'UPDATE_INTERVAL': 1,  # GPS 更新間隔（秒）
    'MIN_SATELLITES': 4,   # 最少衛星數量才算有效定位
    'ACCURACY_THRESHOLD': 0.5  # 信號強度閾值
}

# RTSP 攝影機設定
CAMERA_URLS = {
    "inside": "rtsp://admin:123456@192.168.100.10/stream1",   # 車內鏡頭
    "outside": "rtsp://admin:123456@192.168.100.12/stream1"  # 車外鏡頭
}

# 攝影機相關設定
CAMERA_CONFIG = {
    'FRAME_WIDTH': 640,
    'FRAME_HEIGHT': 480,
    'FPS': 30,
    'BUFFER_SIZE': 1,  # 減少延遲
    'RECONNECT_TIMEOUT': 5,  # 斷線重連時間(秒)
    'MAX_RECONNECT_ATTEMPTS': 3
}

# SSL 設定預留
# SSL_CONFIG = {
#     'SSL_CERT': 'path/to/cert.pem',
#     'SSL_KEY': 'path/to/key.pem'
# }


# config.py 補充

# Demo 模式開關
DEMO_MODE = True  # 電腦開發時設為 True

# Demo 攝影機設定（電腦開發用）
if DEMO_MODE:
    CAMERA_SOURCES = {
        "inside": 0,  # 筆電內建攝影機
        "outside": "demo/test_videos/outside_demo.mp4"  # 或用影片檔
    }
else:
    # 正式環境用 RTSP
    CAMERA_SOURCES = CAMERA_URLS

# Demo GPIO 設定（使用鍵盤模擬）
DEMO_GPIO_KEYS = {
    'left_turn': 'a',      # 按 A 鍵 = 左轉燈
    'right_turn': 'd',     # 按 D 鍵 = 右轉燈
    'reverse': 's',        # 按 S 鍵 = 倒車
    'speed_up': 'w',       # 按 W 鍵 = 加速
    'speed_down': 'x'      # 按 X 鍵 = 減速
}

# Demo GPS 設定（固定路線）
DEMO_GPS_ROUTE = [
    {'lat': 25.033, 'lon': 121.565, 'speed': 40},
    {'lat': 25.034, 'lon': 121.566, 'speed': 50},
    {'lat': 25.035, 'lon': 121.567, 'speed': 45},
    # ... 更多點
]