# detectors/outside/distance_detector.py
"""
前車距離偵測器 (B03)
使用 YOLOv8 偵測車輛並估算距離
"""

import cv2
import numpy as np
from datetime import datetime
from collections import deque
from detectors.base_detector import BaseDetector

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("警告：ultralytics 未安裝，前車偵測將無法使用")

class DistanceDetector(BaseDetector):
    """前車距離偵測器"""
    
    def __init__(self, model_path='ai_models/yolov8n.pt'):
        super().__init__('DistanceDetector', 'outside')
        
        if not YOLO_AVAILABLE:
            raise ImportError("請安裝 ultralytics: pip install ultralytics")
        
        self.model_path = model_path
        self.model = None
        
        # COCO 車輛類別
        self.VEHICLE_CLASSES = {
            2: 'car',
            3: 'motorcycle',
            5: 'bus',
            7: 'truck'
        }
        
        # 距離估算參數（需根據實際攝影機校準）
        self.focal_length = 700  # 像素
        self.average_vehicle_width = 1.8  # 公尺
        
        # 安全距離計算（台灣規則：速度/10 × 3）
        self.safe_distance_multiplier = 3.0
        self.min_safe_distance = 10.0  # 最小安全距離（公尺）
        
        # 距離歷史（滑動平均）
        self.distance_history = deque(maxlen=10)
        
        # 危險狀態追蹤
        self.danger_frames = 0
        self.fps = 30
        self.DANGER_CONFIRM_FRAMES = 15  # 0.5秒確認
        
        # 事件去重
        self.last_event_time = None
        self.event_cooldown = 5.0  # 秒
    
    def initialize(self):
        """初始化 YOLOv8 模型"""
        try:
            self.model = YOLO(self.model_path)
            print(f"[{self.detector_name}] YOLOv8 模型已載入: {self.model_path}")
        except Exception as e:
            print(f"[{self.detector_name}] 模型載入失敗: {e}")
            raise
    
    def _calculate_safe_distance(self, speed_kmh):
        """
        計算安全距離
        
        公式：速度（km/h）÷ 10 × 3
        例：50 km/h → 15m
        """
        safe_distance = (speed_kmh / 10) * self.safe_distance_multiplier
        return max(safe_distance, self.min_safe_distance)
    
    def _estimate_distance(self, bbox_width, vehicle_type='car'):
        """
        估算距離（單目視覺）
        
        公式：距離 = (焦距 × 實際寬度) / 像素寬度
        """
        real_widths = {
            'car': 1.8,
            'bus': 2.5,
            'truck': 2.5,
            'motorcycle': 0.8
        }
        
        real_width = real_widths.get(vehicle_type, 1.8)
        
        if bbox_width <= 0:
            return None
        
        distance = (self.focal_length * real_width) / bbox_width
        
        # 合理範圍檢查（1-100 公尺）
        if distance < 1 or distance > 100:
            return None
        
        return distance
    
    def detect(self, frame, timestamp=None, **kwargs):
        """執行前車距離偵測"""
        if timestamp is None:
            timestamp = datetime.now()
        
        # 取得車速（from GPS）
        vehicle_speed = kwargs.get('vehicle_speed', 50)  # 預設 50 km/h
        
        h, w = frame.shape[:2]
        
        # YOLOv8 偵測
        results = self.model.predict(
            frame,
            classes=list(self.VEHICLE_CLASSES.keys()),
            conf=0.5,
            verbose=False
        )[0]
        
        if len(results.boxes) == 0:
            self.danger_frames = 0
            self.distance_history.clear()
            return {
                'event_detected': False,
                'rule_id': None,
                'confidence': 0.0,
                'detection_data': {'status': 'no_vehicle_detected'},
                'timestamp': timestamp
            }
        
        # 找最近的車輛
        closest_vehicle = None
        min_distance = float('inf')
        
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            
            # 只處理畫面下半部（前方車輛）
            if y1 < h * 0.3:
                continue
            
            bbox_width = x2 - x1
            vehicle_type = self.VEHICLE_CLASSES.get(cls_id, 'car')
            
            distance = self._estimate_distance(bbox_width, vehicle_type)
            
            if distance and distance < min_distance:
                min_distance = distance
                closest_vehicle = {
                    'type': vehicle_type,
                    'distance': distance,
                    'confidence': conf,
                    'bbox': (int(x1), int(y1), int(x2), int(y2))
                }
        
        if not closest_vehicle:
            self.danger_frames = 0
            self.distance_history.clear()
            return {
                'event_detected': False,
                'rule_id': None,
                'confidence': 0.0,
                'detection_data': {'status': 'distance_estimation_failed'},
                'timestamp': timestamp
            }
        
        # 滑動平均
        self.distance_history.append(closest_vehicle['distance'])
        avg_distance = np.mean(self.distance_history)
        
        # 計算安全距離
        safe_distance = self._calculate_safe_distance(vehicle_speed)
        
        # 判斷是否過近
        is_danger = avg_distance < safe_distance
        
        if is_danger:
            self.danger_frames += 1
        else:
            self.danger_frames = 0
        
        # 需要持續過近才確認
        if self.danger_frames < self.DANGER_CONFIRM_FRAMES:
            return {
                'event_detected': False,
                'rule_id': None,
                'confidence': 0.0,
                'detection_data': {
                    'distance': round(avg_distance, 1),
                    'safe_distance': round(safe_distance, 1),
                    'vehicle_speed': vehicle_speed,
                    'is_danger': is_danger,
                    'danger_frames': self.danger_frames
                },
                'timestamp': timestamp
            }
        
        # B03 事件觸發
        event_detected = True
        confidence = 0.85
        
        print(f"[{self.detector_name}] B03 前車過近: {avg_distance:.1f}m < {safe_distance:.1f}m")
        
        # 事件去重
        if self.last_event_time:
            time_diff = (timestamp - self.last_event_time).total_seconds()
            if time_diff < self.event_cooldown:
                event_detected = False
        
        if event_detected:
            self.last_event_time = timestamp
        
        return {
            'event_detected': event_detected,
            'rule_id': 'B03' if event_detected else None,
            'confidence': confidence,
            'detection_data': {
                'distance': round(avg_distance, 1),
                'safe_distance': round(safe_distance, 1),
                'vehicle_speed': vehicle_speed,
                'vehicle_type': closest_vehicle['type'],
                'vehicle_confidence': closest_vehicle['confidence'],
                'danger_duration': round(self.danger_frames / self.fps, 2)
            },
            'timestamp': timestamp
        }