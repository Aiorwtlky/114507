import os
from dotenv import load_dotenv
import logging

load_dotenv()

class Config:
    def __init__(self):
        # Cloudinary 配置
        self.cloudinary_cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        self.cloudinary_api_key = os.getenv('CLOUDINARY_API_KEY')
        self.cloudinary_api_secret = os.getenv('CLOUDINARY_API_SECRET')
        
        # 攝影機配置
        self.internal_camera_index = int(os.getenv('INTERNAL_CAMERA_INDEX', 0))
        self.external_camera_index = int(os.getenv('EXTERNAL_CAMERA_INDEX', 1))
        
        # 內鏡頭 (駕駛員監控) - 較低解析度以提升效能
        self.internal_camera_width = 320
        self.internal_camera_height = 240
        self.internal_camera_fps = 15
        
        # 外鏡頭 (ADAS) - 中等解析度
        self.external_camera_width = 640
        self.external_camera_height = 480
        self.external_camera_fps = 20
        
        # AI 模型配置 - 針對 Hailo 8 優化
        self.use_hailo_acceleration = os.getenv('USE_HAILO_ACCELERATION', 'true').lower() == 'true'
        self.hailo_model_path = os.getenv('HAILO_MODEL_PATH', 'models/')
        
        self.mediapipe_model_complexity = 0  # 最輕量
        self.mediapipe_min_detection_confidence = 0.7
        self.mediapipe_min_tracking_confidence = 0.5
        
        # 疲勞檢測閾值
        self.default_ear_threshold = 0.25
        self.eye_closed_frames_threshold = 45  # 3秒 @ 15fps
        self.drowsy_frames_threshold = 15     # 1秒 @ 15fps
        self.distraction_frames_threshold = 75 # 5秒 @ 15fps
        
        # ADAS 配置
        self.lane_departure_threshold = 50
        self.following_distance_threshold = 30
        self.yolo_confidence_threshold = 0.5
        
        # 系統配置
        self.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.video_duration = int(os.getenv('VIDEO_DURATION', 60))
        self.max_local_files = int(os.getenv('MAX_LOCAL_FILES', 5))
        
        # 資料目錄
        self.data_dir = 'data'
        self.temp_videos_dir = 'temp_videos'
        self.logs_dir = 'data/logs'
        self.models_dir = 'models'
        
        # 建立必要目錄
        self._create_directories()
        
        # 設定日誌
        self._setup_logging()
    
    def _create_directories(self):
        """建立必要的目錄"""
        directories = [
            self.data_dir,
            self.temp_videos_dir,
            self.logs_dir,
            self.models_dir
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def _setup_logging(self):
        """設定日誌系統"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format=log_format,
            handlers=[
                logging.FileHandler(f'{self.logs_dir}/system.log'),
                logging.StreamHandler()
            ]
        )

# 全域配置實例
config = Config()