# utils/image_recognition.py (生產級版本)
"""
生產級 AI 視覺辨識系統
整合真實可用的模型：
- MediaPipe: 疲勞駕駛偵測（個體化校準）
- OpenCV: 車道偏離偵測（整合 GPIO）
- YOLOv8: 前車偵測與交通號誌
"""

import cv2
import numpy as np
from datetime import datetime
from typing import Dict, Optional

from utils.unified_ai_detector import get_unified_detector


class VisionRecognitionSystem:
    """視覺辨識系統 - 生產級版本"""
    
    def __init__(self):
        """初始化系統"""
        self.unified_detector = None
        self.current_driver_id = None
        
        # 校準狀態
        self.is_calibrated = False
        self.calibration_in_progress = False
    
    def set_driver(self, driver_id):
        """
        設定當前駕駛員
        
        會載入該駕駛員的個體化校準數據
        
        Args:
            driver_id: 駕駛員 ID
        """
        if driver_id != self.current_driver_id:
            self.current_driver_id = driver_id
            self.unified_detector = get_unified_detector(driver_id)
            self.is_calibrated = False
            self.calibration_in_progress = False
            
            print(f"📋 切換駕駛員: {driver_id}")
    
    def start_calibration(self):
        """開始校準程序"""
        self.calibration_in_progress = True
        self.is_calibrated = False
        print("🔧 開始駕駛員校準...")
    
    def calibrate(self, frame: np.ndarray) -> Dict:
        """
        執行校準（內鏡頭）
        
        Args:
            frame: 內鏡頭影像幀
            
        Returns:
            dict: 校準狀態
        """
        if not self.unified_detector:
            self.unified_detector = get_unified_detector(self.current_driver_id)
        
        result = self.unified_detector.calibrate_driver(frame)
        
        if result['status'] == 'completed':
            self.is_calibrated = True
            self.calibration_in_progress = False
            print(f"✅ 校準完成！基準 EAR: {result.get('baseline_ear', 'N/A')}")
        
        return result
    
    def predict_from_frame(
        self,
        frame: np.ndarray,
        camera_type: str,
        save_image: bool = False,
        gpio_data: Optional[Dict] = None,
        gps_data: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        從影像框架進行預測
        
        Args:
            frame: OpenCV 影像幀
            camera_type: 'inside' 或 'outside'
            save_image: 是否儲存截圖
            gpio_data: GPIO 數據 {'left_turn': bool, 'right_turn': bool}
            gps_data: GPS 數據 {'speed': float}
            
        Returns:
            事件資訊字典，若無事件則回傳 None
        """
        if frame is None or frame.size == 0:
            return None
        
        # 確保偵測器已初始化
        if not self.unified_detector:
            self.unified_detector = get_unified_detector(self.current_driver_id)
        
        # 如果正在校準，執行校準流程
        if self.calibration_in_progress and camera_type == 'inside':
            calibration_result = self.calibrate(frame)
            if calibration_result['status'] == 'calibrating':
                return None  # 校準中不產生事件
        
        # 根據鏡頭類型選擇偵測方法
        if camera_type == 'inside':
            # 內鏡頭：駕駛行為偵測
            event_record = self.unified_detector.detect_inside_camera(frame)
            
            if event_record and save_image:
                # 儲存截圖
                image_path = self._save_event_image(frame, event_record)
                event_record['local_image_path'] = image_path
            
            return event_record
            
        elif camera_type == 'outside':
            # 外鏡頭：道路狀況偵測
            # 解析 GPIO 和 GPS 數據
            left_turn = gpio_data.get('left_turn', False) if gpio_data else False
            right_turn = gpio_data.get('right_turn', False) if gpio_data else False
            speed = gps_data.get('speed', 0.0) if gps_data else 0.0
            
            events = self.unified_detector.detect_outside_camera(
                frame,
                left_turn_signal=left_turn,
                right_turn_signal=right_turn,
                vehicle_speed=speed
            )
            
            # 外鏡頭可能同時偵測到多個事件
            # 只回傳第一個（優先級最高的）
            if events and len(events) > 0:
                event_record = events[0]
                
                if save_image:
                    image_path = self._save_event_image(frame, event_record)
                    event_record['local_image_path'] = image_path
                
                return event_record
            
            return None
        
        return None
    
    def _save_event_image(self, frame: np.ndarray, event_record: dict) -> str:
        """
        儲存事件截圖
        
        Args:
            frame: 影像框架
            event_record: 事件記錄
            
        Returns:
            圖片儲存路徑
        """
        import os
        
        # 建立儲存目錄
        image_dir = "trip_data/event_images"
        os.makedirs(image_dir, exist_ok=True)
        
        # 生成檔案名稱
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        event_code = event_record['event_number']
        camera = event_record['camera_type']
        filename = f"{event_code}_{camera}_{timestamp}.jpg"
        filepath = os.path.join(image_dir, filename)
        
        # 儲存圖片（壓縮以節省空間）
        cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        
        return filepath
    
    def reset_trackers(self):
        """重置所有追蹤器（行程結束時呼叫）"""
        if self.unified_detector:
            self.unified_detector.reset_all()
        
        print("🔄 所有偵測器已重置")
    
    def get_system_status(self) -> Dict:
        """取得系統狀態"""
        return {
            'driver_id': self.current_driver_id,
            'calibrated': self.is_calibrated,
            'calibration_in_progress': self.calibration_in_progress,
            'unified_detector_loaded': self.unified_detector is not None
        }


# 全域單例
_vision_system = None

def get_vision_system() -> VisionRecognitionSystem:
    """取得視覺辨識系統的單例"""
    global _vision_system
    if _vision_system is None:
        _vision_system = VisionRecognitionSystem()
    return _vision_system