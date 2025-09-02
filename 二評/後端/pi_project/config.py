import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Dict, Any

# 載入環境變數
load_dotenv()

@dataclass
class CameraConfig:
    """攝影機配置"""
    # 內鏡頭 (駕駛員監控)
    internal_camera_index: int = int(os.getenv('INTERNAL_CAMERA_INDEX', 0))
    internal_camera_width: int = 640
    internal_camera_height: int = 480
    internal_camera_fps: int = 30
    
    # 外鏡頭 (ADAS)
    external_camera_index: int = int(os.getenv('EXTERNAL_CAMERA_INDEX', 1))
    external_camera_width: int = 1280
    external_camera_height: int = 720
    external_camera_fps: int = 30

@dataclass
class AIConfig:
    """AI 模型配置"""
    # MediaPipe 配置
    mp_detection_confidence: float = 0.5
    mp_tracking_confidence: float = 0.5
    mp_max_num_faces: int = 1
    mp_max_num_hands: int = 2
    
    # EAR 閾值
    default_ear_threshold: float = 0.25
    ear_history_size: int = 500
    threshold_update_interval: int = 100
    
    # YOLO 配置
    yolo_confidence: float = 0.5
    yolo_iou_threshold: float = 0.4
    yolo_model_path: str = 'models/yolo_adas.hef'
    
    # 距離估算參數
    focal_length: float = 640.0
    real_car_height: float = 1.5  # 一般車輛高度 (米)

@dataclass
class CloudinaryConfig:
    """Cloudinary 配置"""
    cloud_name: str = os.getenv('CLOUDINARY_CLOUD_NAME', '')
    api_key: str = os.getenv('CLOUDINARY_API_KEY', '')
    api_secret: str = os.getenv('CLOUDINARY_API_SECRET', '')
    upload_timeout: int = 60
    max_retries: int = 3
    folder_prefix: str = 'dashcam'
    
@dataclass
class RecordingConfig:
    """錄影配置"""
    duration_seconds: int = 60  # 1 分鐘
    video_quality: str = 'medium'  # low, medium, high
    video_codec: str = 'mp4v'
    max_local_files: int = 10  # 最多保留檔案數
    emergency_storage_limit: int = 100  # 緊急情況最大儲存
    
@dataclass
class HardwareConfig:
    """硬體配置"""
    # GPIO 接腳 (Raspberry Pi)
    left_turn_pin: int = int(os.getenv('LEFT_TURN_PIN', 18))
    right_turn_pin: int = int(os.getenv('RIGHT_TURN_PIN', 19))
    speed_sensor_pin: int = int(os.getenv('SPEED_SENSOR_PIN', 20))
    
    # 是否啟用 GPIO (非 Raspberry Pi 環境下設為 False)
    enable_gpio: bool = os.getenv('ENABLE_GPIO', 'False').lower() == 'true'

# 警報評分標準
ALERT_SCORING = {
    # A系列：內鏡頭 (駕駛員狀態)
    'A01': {'name': '重度疲勞駕駛 (閉眼超過3秒)', 'score': 25, 'enabled': True},
    'A02': {'name': '中度疲勞駕駛 (閉眼1-3秒)', 'score': 15, 'enabled': True},
    'A03': {'name': '長時間分心 (低頭/轉頭超過5秒)', 'score': 20, 'enabled': True},
    'A04': {'name': '駕駛中使用手機', 'score': 20, 'enabled': True},
    
    # B系列：外鏡頭 (路況環境)
    'B01': {'name': '車道偏離 (未打方向燈)', 'score': 5, 'enabled': True},
    'B02': {'name': '前車過近', 'score': 15, 'enabled': True},
    'B03': {'name': '闖紅燈', 'score': 30, 'enabled': True},
}

# 時間閾值設定
TIME_THRESHOLDS = {
    'eye_closed_medium': 1.0,    # 中度疲勞：閉眼1秒
    'eye_closed_severe': 3.0,    # 重度疲勞：閉眼3秒
    'head_distraction': 5.0,     # 分心：低頭/轉頭5秒
    'phone_detection': 1.0,      # 手機使用：持續1秒
    'lane_departure': 2.0,       # 車道偏離：持續2秒
    'close_vehicle': 3.0,        # 前車過近：持續3秒
}

class Config:
    """主配置類別"""
    def __init__(self):
        self.camera = CameraConfig()
        self.ai = AIConfig()
        self.cloudinary = CloudinaryConfig()
        self.recording = RecordingConfig()
        self.hardware = HardwareConfig()
        self.alert_scoring = ALERT_SCORING
        self.time_thresholds = TIME_THRESHOLDS
        
        # 系統設定
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
        
        # 路徑設定
        self.data_dir = 'data'
        self.temp_videos_dir = 'temp_videos'
        self.models_dir = 'models'
        self.logs_dir = 'data/logs'
        
        # 檔案路徑
        self.driver_profiles_file = os.path.join(self.data_dir, 'driver_profiles.json')
        self.database_file = os.path.join(self.data_dir, 'system.db')
        
        # 系統資訊
        self.version = "1.0.0"
        self.author = "JoyWuFN"
        self.created_date = "2025-08-31"
        
    def validate(self) -> bool:
        """驗證配置是否完整"""
        validation_results = []
        
        # 檢查 Cloudinary 配置
        required_cloudinary = [
            self.cloudinary.cloud_name,
            self.cloudinary.api_key,
            self.cloudinary.api_secret
        ]
        
        if not all(required_cloudinary):
            validation_results.append("Cloudinary 配置不完整")
        
        # 檢查攝影機配置
        if self.camera.internal_camera_index == self.camera.external_camera_index:
            validation_results.append("內外鏡頭不能使用相同索引")
        
        # 檢查路徑
        import os
        required_dirs = [self.data_dir, self.temp_videos_dir, self.logs_dir]
        for directory in required_dirs:
            if not os.path.exists(directory):
                validation_results.append(f"目錄不存在: {directory}")
        
        if validation_results:
            print("⚠️  配置驗證警告:")
            for warning in validation_results:
                print(f"   - {warning}")
            return False
        
        return True
    
    def get_system_info(self) -> Dict[str, Any]:
        """獲取系統資訊"""
        return {
            'version': self.version,
            'author': self.author,
            'created_date': self.created_date,
            'debug_mode': self.debug_mode,
            'log_level': self.log_level,
            'camera_config': {
                'internal_index': self.camera.internal_camera_index,
                'external_index': self.camera.external_camera_index,
            },
            'recording_duration': self.recording.duration_seconds,
            'alert_count': len(self.alert_scoring),
            'gpio_enabled': self.hardware.enable_gpio
        }

# 建立全域配置實例
config = Config()

# 導出常用的配置
__all__ = ['config', 'Config', 'ALERT_SCORING', 'TIME_THRESHOLDS']