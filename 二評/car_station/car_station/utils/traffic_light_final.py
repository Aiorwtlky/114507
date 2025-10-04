# utils/traffic_light_detector_final.py

import cv2
import numpy as np
from collections import deque
from ultralytics import YOLO

class TrafficLightDetectorFinal:
    """
    終極版 B03 偵測器
    - YOLOv8 定位紅綠燈
    - 改良的 HSV 顏色判斷（過濾建築物）
    - 移動偵測
    """
    
    def __init__(self):
        print("載入 YOLOv8 模型...")
        self.model = YOLO('yolov8n.pt')
        print("模型載入完成")
        
        self.light_state_history = deque(maxlen=10)
        self.prev_frame_gray = None
        self.movement_history = deque(maxlen=5)
        self.frame_count = 0
        self.detection_count = 0
    
    def detect_traffic_light_location(self, frame):
        """YOLOv8 偵測紅綠燈位置"""
        results = self.model(frame, classes=[9], verbose=False, conf=0.3)
        
        traffic_lights = []
        height, width = frame.shape[:2]
        
        if len(results[0].boxes) > 0:
            for box in results[0].boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                
                w, h = x2 - x1, y2 - y1
                
                # ✅ 過濾條件（防止誤判建築物）
                # 1. 最小尺寸
                if w < 10 or h < 10:
                    continue
                
                # 2. 位置（紅綠燈在上半部）
                if y1 > height * 0.6:
                    continue
                
                # 3. 大小限制（不能太大）
                if w * h > width * height * 0.1:
                    continue
                
                # 4. 長寬比（垂直為主）
                aspect = h / w if w > 0 else 0
                if aspect < 0.5 or aspect > 5:
                    continue
                
                traffic_lights.append({
                    'bbox': (int(x1), int(y1), int(x2), int(y2)),
                    'confidence': conf
                })
        
        return traffic_lights
    
    def analyze_light_color(self, frame, bbox):
        """改良的 HSV 顏色分析"""
        x1, y1, x2, y2 = bbox
        roi = frame[y1:y2, x1:x2]
        
        if roi.size == 0:
            return 'unknown'
        
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # 更嚴格的顏色範圍
        color_ranges = {
            'red': [
                (np.array([0, 150, 100]), np.array([10, 255, 255])),  # 更高飽和度
                (np.array([170, 150, 100]), np.array([180, 255, 255]))
            ],
            'yellow': [
                (np.array([20, 150, 150]), np.array([35, 255, 255]))
            ],
            'green': [
                (np.array([40, 100, 100]), np.array([90, 255, 255]))
            ]
        }
        
        max_pixels = 0
        detected_color = 'unknown'
        
        for color, ranges in color_ranges.items():
            total = 0
            for lower, upper in ranges:
                mask = cv2.inRange(hsv, lower, upper)
                total += cv2.countNonZero(mask)
            
            if total > max_pixels:
                max_pixels = total
                detected_color = color
        
        # ✅ 更高的閾值（避免誤判）
        roi_area = roi.shape[0] * roi.shape[1]
        if max_pixels < roi_area * 0.1:  # 至少 10% 像素
            return 'unknown'
        
        return detected_color
    
    def detect_vehicle_movement(self, frame):
        """偵測移動"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        if self.prev_frame_gray is None:
            self.prev_frame_gray = gray
            return False
        
        diff = cv2.absdiff(self.prev_frame_gray, gray)
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        
        ratio = cv2.countNonZero(thresh) / (thresh.shape[0] * thresh.shape[1])
        self.prev_frame_gray = gray
        
        is_moving = ratio > 0.05
        self.movement_history.append(is_moving)
        
        return sum(self.movement_history) >= 2 if len(self.movement_history) >= 3 else False
    
    def detect(self, frame, draw_visualization=False):
        """主偵測"""
        self.frame_count += 1
        
        # 1. 偵測位置
        lights = self.detect_traffic_light_location(frame)
        
        light_state = 'unknown'
        light_conf = 0.0
        best_light = None
        
        # 2. 分析顏色
        if lights:
            self.detection_count += 1
            best_light = max(lights, key=lambda x: x['confidence'])
            light_state = self.analyze_light_color(frame, best_light['bbox'])
            light_conf = best_light['confidence']
            
            if light_state != 'unknown':
                self.light_state_history.append(light_state)
        
        # 3. 移動
        vehicle_moving = self.detect_vehicle_movement(frame)
        
        # 4. 闖紅燈
        red_light_violation = False
        if len(self.light_state_history) >= 5:
            if list(self.light_state_history).count('red') >= 3 and vehicle_moving:
                red_light_violation = True
        
        result = {
            'red_light_violation': red_light_violation,
            'light_state': light_state,
            'light_detected': light_state != 'unknown',
            'vehicle_moving': vehicle_moving,
            'confidence': light_conf,
            'visualization': None
        }
        
        # 視覺化
        if draw_visualization and best_light:
            vis = frame.copy()
            x1, y1, x2, y2 = best_light['bbox']
            
            colors = {'red': (0,0,255), 'yellow': (0,255,255), 'green': (0,255,0)}
            color = colors.get(light_state, (128,128,128))
            
            cv2.rectangle(vis, (x1, y1), (x2, y2), color, 2)
            cv2.putText(vis, f"{light_state.upper()}", (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            status = "B03 VIOLATION!" if red_light_violation else light_state.upper()
            cv2.putText(vis, status, (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,255) if red_light_violation else color, 3)
            
            result['visualization'] = vis
        else:
            result['visualization'] = frame
        
        return result