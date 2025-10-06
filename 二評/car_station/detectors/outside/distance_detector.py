# detectors/outside/distance_detector.py
"""
前車距離偵測器 (B03)
優化版：ROI處理 + 車輛追蹤 + 降低誤判
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

class DistanceDetector(BaseDetector):
    """前車距離偵測器"""
    
    def __init__(self, model_path='ai_models/yolov8n.pt'):
        super().__init__('DistanceDetector', 'outside')
        
        if not YOLO_AVAILABLE:
            raise ImportError("請安裝 ultralytics")
        
        self.model_path = model_path
        self.model = None
        
        # 車輛類別
        self.VEHICLE_CLASSES = {2: 'car', 3: 'motorcycle', 5: 'bus', 7: 'truck'}
        
        # 距離估算參數
        self.focal_length = 700
        self.vehicle_widths = {'car': 1.8, 'bus': 2.5, 'truck': 2.5, 'motorcycle': 0.8}
        
        # 安全距離（台灣規則）
        self.safe_distance_multiplier = 3.0
        self.min_safe_distance = 10.0
        
        # 車輛追蹤（避免跳動）
        self.tracked_vehicles = {}
        self.vehicle_id_counter = 0
        self.max_tracking_frames = 10
        
        # 距離歷史（滑動平均）
        self.distance_history = deque(maxlen=5)
        
        # 危險狀態追蹤
        self.danger_frames = 0
        self.DANGER_CONFIRM_FRAMES = 10
        
        # 事件去重
        self.last_event_time = None
        self.event_cooldown = 5.0
        
        # 幀計數
        self.frame_count = 0
    
    def initialize(self):
        """初始化 YOLOv8"""
        try:
            import torch
            # 允許載入 ultralytics 模型（解決 PyTorch 2.6 問題）
            try:
                torch.serialization.add_safe_globals(['ultralytics.nn.tasks.DetectionModel'])
            except:
                pass  # 舊版 PyTorch 沒有這個方法
            
            self.model = YOLO(self.model_path)
            self.model.fuse()
            print(f"[{self.detector_name}] YOLOv8 已載入")
        except Exception as e:
            print(f"[{self.detector_name}] 模型載入失敗: {e}")
            raise
    
    def _calculate_safe_distance(self, speed_kmh):
        """計算安全距離"""
        safe_distance = (speed_kmh / 10) * self.safe_distance_multiplier
        return max(safe_distance, self.min_safe_distance)
    
    def _estimate_distance(self, bbox_width, vehicle_type):
        """估算距離"""
        real_width = self.vehicle_widths.get(vehicle_type, 1.8)
        if bbox_width <= 0:
            return None
        distance = (self.focal_length * real_width) / bbox_width
        return distance if 1 < distance < 100 else None
    
    def _track_vehicle(self, bbox, vehicle_type, distance):
        """簡單的車輛追蹤"""
        x1, y1, x2, y2 = bbox
        center = ((x1 + x2) / 2, (y1 + y2) / 2)
        
        min_dist = float('inf')
        matched_id = None
        
        for vid, tracked in self.tracked_vehicles.items():
            if self.frame_count - tracked['last_seen'] > self.max_tracking_frames:
                continue
            
            tracked_center = tracked['center']
            dist = np.sqrt(
                (center[0] - tracked_center[0])**2 +
                (center[1] - tracked_center[1])**2
            )
            
            if dist < min_dist and dist < 50:
                min_dist = dist
                matched_id = vid
        
        if matched_id:
            self.tracked_vehicles[matched_id].update({
                'center': center,
                'distance': distance,
                'type': vehicle_type,
                'last_seen': self.frame_count
            })
            return matched_id
        else:
            self.vehicle_id_counter += 1
            self.tracked_vehicles[self.vehicle_id_counter] = {
                'center': center,
                'distance': distance,
                'type': vehicle_type,
                'last_seen': self.frame_count
            }
            return self.vehicle_id_counter
    
    def detect(self, frame, timestamp=None, **kwargs):
        """執行距離偵測"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.frame_count += 1
        
        # 取得車速
        vehicle_speed = kwargs.get('vehicle_speed', 50)
        
        try:
            h, w = frame.shape[:2]
            
            # ROI 優化：只處理下半部
            roi_y_start = int(h * 0.3)
            roi = frame[roi_y_start:h, :]
            
            # YOLOv8 推論
            results = self.model.predict(
                roi,
                classes=list(self.VEHICLE_CLASSES.keys()),
                conf=0.5,
                verbose=False,
                imgsz=416
            )[0]
            
            if len(results.boxes) == 0:
                self.danger_frames = 0
                self.distance_history.clear()
                return {
                    'event_detected': False,
                    'rule_id': None,
                    'confidence': 0.0,
                    'detection_data': {'status': 'no_vehicle'},
                    'timestamp': timestamp
                }
            
            # 找最近的車輛
            closest_vehicle = None
            min_distance = float('inf')
            
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                
                bbox_width = x2 - x1
                vehicle_type = self.VEHICLE_CLASSES[cls_id]
                distance = self._estimate_distance(bbox_width, vehicle_type)
                
                if distance and distance < min_distance:
                    min_distance = distance
                    bbox_orig = (x1, y1 + roi_y_start, x2, y2 + roi_y_start)
                    closest_vehicle = {
                        'type': vehicle_type,
                        'distance': distance,
                        'confidence': conf,
                        'bbox': bbox_orig
                    }
            
            if not closest_vehicle:
                self.danger_frames = 0
                return {
                    'event_detected': False,
                    'rule_id': None,
                    'confidence': 0.0,
                    'detection_data': {'status': 'distance_failed'},
                    'timestamp': timestamp
                }
            
            # 車輛追蹤
            self._track_vehicle(
                closest_vehicle['bbox'],
                closest_vehicle['type'],
                closest_vehicle['distance']
            )
            
            # 滑動平均
            self.distance_history.append(closest_vehicle['distance'])
            avg_distance = np.mean(self.distance_history)
            
            # 計算安全距離
            safe_distance = self._calculate_safe_distance(vehicle_speed)
            
            # 判斷是否危險
            is_danger = avg_distance < safe_distance
            
            if is_danger:
                self.danger_frames += 1
            else:
                self.danger_frames = 0
            
            # 事件判斷
            event_detected = False
            confidence = 0.0
            
            if self.danger_frames >= self.DANGER_CONFIRM_FRAMES:
                event_detected = True
                confidence = 0.85
                
                # 事件去重
                if self.last_event_time:
                    time_diff = (timestamp - self.last_event_time).total_seconds()
                    if time_diff < self.event_cooldown:
                        event_detected = False
                
                if event_detected:
                    self.last_event_time = timestamp
                    print(f"[{self.detector_name}] B03 前車過近: {avg_distance:.1f}m < {safe_distance:.1f}m")
            
            return {
                'event_detected': event_detected,
                'rule_id': 'B03' if event_detected else None,
                'confidence': confidence,
                'detection_data': {
                    'distance': round(avg_distance, 1),
                    'safe_distance': round(safe_distance, 1),
                    'vehicle_speed': vehicle_speed,
                    'vehicle_type': closest_vehicle['type'],
                    'danger_frames': self.danger_frames
                },
                'timestamp': timestamp
            }
            
        except Exception as e:
            print(f"[{self.detector_name}] 偵測錯誤: {e}")
            return {
                'event_detected': False,
                'rule_id': None,
                'confidence': 0.0,
                'detection_data': {'status': 'error', 'message': str(e)},
                'timestamp': timestamp
            }