# utils/vehicle_traffic_detector.py
"""
生產級前車與交通號誌偵測系統
- 使用 YOLOv8n (輕量級) 進行即時偵測
- 前車距離估計（單目視覺 + 物理模型）
- 交通號誌辨識（紅綠燈狀態）
- Raspberry Pi 優化
"""

import cv2
import numpy as np
from collections import deque
from datetime import datetime
import math


class VehicleTrafficDetector:
    """車輛與交通號誌偵測器"""
    
    def __init__(self, model_path='models/yolov8n.pt', use_optimized=True):
        """
        初始化偵測器
        
        Args:
            model_path: YOLOv8 模型路徑
            use_optimized: 是否使用優化模式（for Raspberry Pi）
        """
        self.use_optimized = use_optimized
        
        # 延遲載入 YOLO（只在第一次使用時載入）
        self.model = None
        self.model_path = model_path
        self.model_loaded = False
        
        # COCO 類別 ID
        self.VEHICLE_CLASSES = {
            2: 'car',
            3: 'motorcycle',
            5: 'bus',
            7: 'truck'
        }
        
        self.TRAFFIC_LIGHT_CLASS = 9  # COCO 中的 traffic light
        
        # 前車追蹤
        self.tracked_vehicles = {}
        self.vehicle_id_counter = 0
        self.max_tracking_age = 30  # 最多追蹤 30 幀
        
        # 距離估計參數（基於相機校準）
        self.focal_length = 700  # 像素（需根據實際相機校準）
        self.average_vehicle_width = 1.8  # 米（標準車輛寬度）
        self.safe_following_distance = 20  # 米（安全距離）
        self.danger_distance = 10  # 米（危險距離）
        
        # 交通號誌追蹤
        self.traffic_light_history = deque(maxlen=15)  # 約 0.5 秒歷史
        self.last_red_light_time = None
        self.red_light_stable_frames = 0
        
        # 偵測狀態
        self.tailgating_start_time = None
        self.tailgating_consecutive_frames = 0
        
        # 效能優化
        self.frame_counter = 0
        self.process_every_n_frames = 3 if use_optimized else 1
        
        # 輸入影像尺寸（降低解析度提升速度）
        self.input_size = (416, 416) if use_optimized else (640, 640)
    
    def _load_model(self):
        """懶加載 YOLO 模型"""
        if self.model_loaded:
            return
        
        try:
            from ultralytics import YOLO
            
            print(f"Loading YOLOv8 model from {self.model_path}...")
            self.model = YOLO(self.model_path)
            
            # Raspberry Pi 優化設定
            if self.use_optimized:
                # 使用 INT8 量化（需要先轉換模型）
                # self.model.export(format='onnx', int8=True)
                pass
            
            self.model_loaded = True
            print("✅ YOLOv8 model loaded successfully")
            
        except ImportError:
            print("❌ ultralytics not installed. Install: pip install ultralytics")
            raise
        except Exception as e:
            print(f"❌ Failed to load YOLO model: {e}")
            raise
    
    def _estimate_distance(self, bbox_width, object_type='car'):
        """
        估計物體距離（單目視覺）
        
        使用相似三角形原理：
        distance = (real_width * focal_length) / pixel_width
        
        Args:
            bbox_width: 邊界框寬度（像素）
            object_type: 物體類型
            
        Returns:
            float: 估計距離（米）
        """
        # 根據物體類型選擇實際寬度
        real_widths = {
            'car': 1.8,
            'bus': 2.5,
            'truck': 2.5,
            'motorcycle': 0.8
        }
        
        real_width = real_widths.get(object_type, 1.8)
        
        if bbox_width == 0:
            return None
        
        distance = (real_width * self.focal_length) / bbox_width
        
        # 合理範圍檢查（1-100 米）
        if distance < 1 or distance > 100:
            return None
        
        return distance
    
    def _track_vehicle(self, bbox, vehicle_class, frame_id):
        """
        追蹤車輛（簡單的 IoU 追蹤）
        
        Returns:
            vehicle_id: 車輛追蹤 ID
        """
        x1, y1, x2, y2 = bbox
        current_center = ((x1 + x2) / 2, (y1 + y2) / 2)
        
        # 尋找最近的已追蹤車輛
        min_distance = float('inf')
        matched_id = None
        
        for vid, tracked in self.tracked_vehicles.items():
            if frame_id - tracked['last_seen'] > self.max_tracking_age:
                continue
            
            prev_center = tracked['center']
            distance = math.sqrt(
                (current_center[0] - prev_center[0]) ** 2 +
                (current_center[1] - prev_center[1]) ** 2
            )
            
            if distance < min_distance and distance < 100:  # 100 像素閾值
                min_distance = distance
                matched_id = vid
        
        # 更新或建立追蹤
        if matched_id:
            self.tracked_vehicles[matched_id].update({
                'bbox': bbox,
                'center': current_center,
                'class': vehicle_class,
                'last_seen': frame_id
            })
            return matched_id
        else:
            # 建立新追蹤
            self.vehicle_id_counter += 1
            self.tracked_vehicles[self.vehicle_id_counter] = {
                'bbox': bbox,
                'center': current_center,
                'class': vehicle_class,
                'last_seen': frame_id
            }
            return self.vehicle_id_counter
    
    def _detect_red_light(self, traffic_light_bbox, frame):
        """
        偵測紅綠燈狀態
        
        使用 HSV 色彩空間判斷紅色/綠色
        
        Args:
            traffic_light_bbox: 紅綠燈邊界框
            frame: 原始影像
            
        Returns:
            str: 'red', 'green', 'yellow', 'unknown'
        """
        x1, y1, x2, y2 = map(int, traffic_light_bbox)
        
        # 擷取紅綠燈區域
        roi = frame[y1:y2, x1:x2]
        
        if roi.size == 0:
            return 'unknown'
        
        # 轉換到 HSV
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # 分成上中下三個區域（對應紅黃綠）
        h, w = roi.shape[:2]
        third = h // 3
        
        top_region = hsv[0:third, :]
        middle_region = hsv[third:2*third, :]
        bottom_region = hsv[2*third:, :]
        
        # 紅色 HSV 範圍（兩個範圍，因為紅色在 HSV 的兩端）
        red_mask1 = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255]))
        red_mask2 = cv2.inRange(hsv, np.array([160, 100, 100]), np.array([180, 255, 255]))
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        
        # 綠色 HSV 範圍
        green_mask = cv2.inRange(hsv, np.array([40, 50, 50]), np.array([90, 255, 255]))
        
        # 黃色 HSV 範圍
        yellow_mask = cv2.inRange(hsv, np.array([20, 100, 100]), np.array([30, 255, 255]))
        
        # 計算各顏色的像素數量
        red_pixels = cv2.countNonZero(red_mask)
        green_pixels = cv2.countNonZero(green_mask)
        yellow_pixels = cv2.countNonZero(yellow_mask)
        
        # 判斷最亮的顏色
        max_pixels = max(red_pixels, green_pixels, yellow_pixels)
        
        if max_pixels < 10:  # 太少像素，可能是誤判
            return 'unknown'
        
        if red_pixels == max_pixels:
            return 'red'
        elif green_pixels == max_pixels:
            return 'green'
        elif yellow_pixels == max_pixels:
            return 'yellow'
        else:
            return 'unknown'
    
    def detect(self, frame):
        """
        主要偵測函數
        
        Args:
            frame: OpenCV 影像幀
            
        Returns:
            dict: 偵測結果
        """
        # 確保模型已載入
        if not self.model_loaded:
            self._load_model()
        
        # 效能優化：不是每幀都處理
        self.frame_counter += 1
        if self.frame_counter % self.process_every_n_frames != 0:
            return {'status': 'skipped', 'frame': self.frame_counter}
        
        h, w = frame.shape[:2]
        
        # YOLO 推論
        results = self.model.predict(
            frame,
            imgsz=self.input_size,
            conf=0.4,  # 信心度閾值
            verbose=False
        )[0]
        
        # 解析結果
        vehicles = []
        traffic_lights = []
        
        for box in results.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            bbox = box.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2]
            
            # 車輛偵測
            if class_id in self.VEHICLE_CLASSES:
                vehicle_class = self.VEHICLE_CLASSES[class_id]
                
                # 只處理畫面前方的車輛（下半部）
                if bbox[1] < h * 0.3:  # 太高，可能是遠方車輛
                    continue
                
                bbox_width = bbox[2] - bbox[0]
                distance = self._estimate_distance(bbox_width, vehicle_class)
                
                if distance:
                    # 追蹤車輛
                    vehicle_id = self._track_vehicle(bbox, vehicle_class, self.frame_counter)
                    
                    vehicles.append({
                        'id': vehicle_id,
                        'class': vehicle_class,
                        'bbox': bbox.tolist(),
                        'confidence': confidence,
                        'distance': round(distance, 1)
                    })
            
            # 交通號誌偵測
            elif class_id == self.TRAFFIC_LIGHT_CLASS:
                # 偵測紅綠燈狀態
                light_state = self._detect_red_light(bbox, frame)
                
                traffic_lights.append({
                    'bbox': bbox.tolist(),
                    'confidence': confidence,
                    'state': light_state
                })
        
        # 分析前車距離
        tailgating_event = self._analyze_tailgating(vehicles)
        
        # 分析交通號誌
        red_light_event = self._analyze_red_light(traffic_lights)
        
        # 建構結果
        result = {
            'status': 'detected',
            'vehicles': vehicles,
            'traffic_lights': traffic_lights,
            'events': []
        }
        
        if tailgating_event:
            result['events'].append(tailgating_event)
        
        if red_light_event:
            result['events'].append(red_light_event)
        
        return result
    
    def _analyze_tailgating(self, vehicles):
        """分析前車過近情況"""
        if not vehicles:
            self.tailgating_consecutive_frames = 0
            self.tailgating_start_time = None
            return None
        
        # 找最近的車輛
        closest_vehicle = min(vehicles, key=lambda v: v['distance'])
        distance = closest_vehicle['distance']
        
        # 判斷是否過近
        is_danger = distance < self.danger_distance
        is_warning = distance < self.safe_following_distance
        
        if is_warning:
            self.tailgating_consecutive_frames += 1
            
            if not self.tailgating_start_time:
                self.tailgating_start_time = datetime.now()
        else:
            self.tailgating_consecutive_frames = 0
            self.tailgating_start_time = None
        
        # 需要連續偵測才確認
        if self.tailgating_consecutive_frames >= 10:  # 約 1 秒
            duration = 0
            if self.tailgating_start_time:
                duration = (datetime.now() - self.tailgating_start_time).total_seconds()
            
            severity = 3 if is_danger else 2
            
            return {
                'event_type': 'tailgating',
                'severity': severity,
                'distance': distance,
                'safe_distance': self.safe_following_distance,
                'duration': round(duration, 2),
                'vehicle_info': closest_vehicle,
                'confidence': 0.85 if is_danger else 0.75
            }
        
        return None
    
    def _analyze_red_light(self, traffic_lights):
        """分析闖紅燈情況"""
        if not traffic_lights:
            self.red_light_stable_frames = 0
            return None
        
        # 檢查是否有紅燈
        red_lights = [tl for tl in traffic_lights if tl['state'] == 'red']
        
        if red_lights:
            self.red_light_stable_frames += 1
            self.traffic_light_history.append('red')
        else:
            self.red_light_stable_frames = 0
            self.traffic_light_history.append('non_red')
        
        # 判斷闖紅燈：連續偵測到紅燈且車輛仍在移動
        # 注意：這需要結合 GPS 速度數據才能準確判斷
        # 目前只做紅燈偵測，實際闖紅燈判斷需要在上層整合
        
        if self.red_light_stable_frames >= 5:  # 連續 5 幀
            # 計算最近歷史中紅燈的比例
            if len(self.traffic_light_history) >= 10:
                recent_red_count = sum(1 for state in list(self.traffic_light_history)[-10:] if state == 'red')
                red_ratio = recent_red_count / 10
                
                if red_ratio > 0.7:  # 70% 以上都是紅燈
                    return {
                        'event_type': 'red_light_detected',
                        'severity': 2,
                        'red_lights': red_lights,
                        'stable_frames': self.red_light_stable_frames,
                        'confidence': 0.80,
                        'note': 'Combine with GPS speed to determine violation'
                    }
        
        return None


# 全域單例
_vehicle_traffic_detector = None

def get_vehicle_traffic_detector(model_path='models/yolov8n.pt'):
    """取得車輛交通偵測器的單例"""
    global _vehicle_traffic_detector
    if _vehicle_traffic_detector is None:
        _vehicle_traffic_detector = VehicleTrafficDetector(model_path)
    return _vehicle_traffic_detector