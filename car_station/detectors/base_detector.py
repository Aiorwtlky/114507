# detectors/base_detector.py
"""
偵測器基類
所有 AI 偵測器的共同介面
"""

from abc import ABC, abstractmethod
from datetime import datetime
import time

class BaseDetector(ABC):
    """偵測器基類"""
    
    def __init__(self, detector_name, camera_type):
        """
        初始化偵測器
        
        Args:
            detector_name: 偵測器名稱
            camera_type: 'inside' 或 'outside'
        """
        self.detector_name = detector_name
        self.camera_type = camera_type
        
        # 偵測狀態
        self.is_initialized = False
        self.last_detection_time = None
        
        # 效能統計
        self.total_detections = 0
        self.total_events = 0
        self.total_processing_time = 0.0
        self.avg_processing_time = 0.0
        
        # 錯誤處理
        self.consecutive_errors = 0
        self.max_consecutive_errors = 10
    
    @abstractmethod
    def initialize(self):
        """
        初始化偵測器（載入模型、設定參數等）
        子類必須實作
        """
        pass
    
    @abstractmethod
    def detect(self, frame, timestamp=None, **kwargs):
        """
        執行偵測
        
        Args:
            frame: OpenCV 影像 (numpy array)
            timestamp: 時間戳記
            **kwargs: 其他參數（如 GPIO 狀態、GPS 速度等）
        
        Returns:
            dict: {
                'event_detected': bool,
                'rule_id': str,
                'confidence': float,
                'detection_data': dict,
                'timestamp': datetime
            }
        """
        pass
    
    def safe_detect(self, frame, timestamp=None, **kwargs):
        """
        安全的偵測包裝器（含錯誤處理和效能統計）
        
        Returns:
            dict or None: 偵測結果，錯誤時返回 None
        """
        if not self.is_initialized:
            try:
                self.initialize()
                self.is_initialized = True
            except Exception as e:
                print(f"[{self.detector_name}] 初始化失敗: {e}")
                return None
        
        start_time = time.time()
        
        try:
            result = self.detect(frame, timestamp, **kwargs)
            
            # 更新統計
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time
            self.total_detections += 1
            self.avg_processing_time = self.total_processing_time / self.total_detections
            
            if result and result.get('event_detected'):
                self.total_events += 1
            
            self.last_detection_time = datetime.now()
            self.consecutive_errors = 0
            
            return result
            
        except Exception as e:
            self.consecutive_errors += 1
            print(f"[{self.detector_name}] 偵測錯誤 ({self.consecutive_errors}/{self.max_consecutive_errors}): {e}")
            
            if self.consecutive_errors >= self.max_consecutive_errors:
                print(f"[{self.detector_name}] 超過最大錯誤次數，需要重新初始化")
                self.is_initialized = False
            
            return None
    
    def get_status(self):
        """取得偵測器狀態"""
        return {
            'detector_name': self.detector_name,
            'camera_type': self.camera_type,
            'is_initialized': self.is_initialized,
            'total_detections': self.total_detections,
            'total_events': self.total_events,
            'avg_processing_time_ms': round(self.avg_processing_time * 1000, 2),
            'last_detection': self.last_detection_time.isoformat() if self.last_detection_time else None,
            'consecutive_errors': self.consecutive_errors
        }
    
    def reset(self):
        """重置偵測器狀態"""
        self.total_detections = 0
        self.total_events = 0
        self.total_processing_time = 0.0
        self.avg_processing_time = 0.0
        self.consecutive_errors = 0