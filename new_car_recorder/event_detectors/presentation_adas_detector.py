# event_detectors/presentation_adas_detector.py
import cv2
import numpy as np
from ultralytics import YOLO
import warnings
warnings.filterwarnings('ignore')

class AdasDetector:
    def __init__(self, fps=30):
        # --- 核心 AI 模型 ---
        self.model = YOLO("assets/models/yolov8n.pt")
        self.class_names = self.model.names
        self.VEHICLE_CLASSES = ['car', 'truck', 'bus', 'motorcycle']
        self.FPS = fps

        # --- 實用且可靠的偵測邏輯 ---
        # 車距判斷 (基於 BBox 相對大小)
        self.DISTANCE_DANGER_RATIO = 0.40
        self.DISTANCE_WARNING_RATIO = 0.30
        self.unsafe_distance_counter = 0
        self.UNSAFE_FRAMES_THRESHOLD = int(fps * 0.5)

        # 車道偏離判斷
        self.lane_departure_counter = 0
        self.LANE_DEPARTURE_FRAMES_THRESHOLD = 10

        # --- 用於 HUD 顯示的事件佇列 ---
        self.recent_events = []
        self.event_history_max_len = 3 # 在 HUD 上最多顯示3個事件

    def analyze_frame(self, frame, frame_count, left_signal_on, right_signal_on):
        display_frame = frame.copy()
        triggered_event = None # 本幀觸發的最重要事件

        # 1. 執行可靠的偵測邏輯
        vehicle_detections = self.detect_vehicles(display_frame)
        distance_event = self.analyze_vehicle_distance(display_frame, vehicle_detections)
        lane_event = self.analyze_lane_departure(display_frame, left_signal_on, right_signal_on)

        # 2. 事件優先級處理
        # 如果同時發生，車道偏離優先於車距過近
        if lane_event:
            triggered_event = lane_event
        elif distance_event:
            triggered_event = distance_event
        
        # 3. 更新 HUD 事件列表
        if triggered_event:
            self.add_event_to_history(triggered_event)

        # 4. 繪製所有視覺化效果
        display_frame = self.visualize(display_frame, vehicle_detections)
        display_frame = self.draw_hud(display_frame) # 最後才畫 HUD，確保在最上層
        
        return triggered_event, display_frame

    def add_event_to_history(self, event_string):
        """將新事件加入到 HUD 的顯示列表中"""
        # 避免重複加入相同的事件
        if not self.recent_events or self.recent_events[0] != event_string:
            self.recent_events.insert(0, event_string)
            if len(self.recent_events) > self.event_history_max_len:
                self.recent_events.pop()

    def detect_vehicles(self, frame):
        detections = []
        results = self.model(frame, verbose=False, classes=[2, 3, 5, 7])  # 車輛類別
        for r in results:
            for box in r.boxes:
                detections.append(box)
        return detections

    def analyze_vehicle_distance(self, frame, detections):
        frame_h, frame_w = frame.shape[:2]
        is_unsafe = False
        front_vehicle_box = None
        max_bbox_height = 0

        for box in detections:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            bbox_h = y2 - y1
            bbox_center_x = (x1 + x2) / 2
            if y2 > frame_h * 0.6 and (frame_w * 0.3 < bbox_center_x < frame_w * 0.7):
                if bbox_h > max_bbox_height:
                    max_bbox_height = bbox_h
                    front_vehicle_box = box

        if front_vehicle_box:
            relative_size = max_bbox_height / frame_h
            if relative_size > self.DISTANCE_DANGER_RATIO:
                is_unsafe = True

        self.unsafe_distance_counter = self.unsafe_distance_counter + 1 if is_unsafe else 0
        if self.unsafe_distance_counter > self.UNSAFE_FRAMES_THRESHOLD:
            self.unsafe_distance_counter = 0  # 重置避免重複觸發
            return "B03: 未保持適當車距"
        return None
        
    def analyze_lane_departure(self, frame, left_signal, right_signal):
        # 簡化的車道線偵測邏輯 (參照 PDF: 使用 Canny + Hough)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 50, 150)
        h, w = frame.shape[:2]
        mask = np.zeros_like(edges)
        polygon = np.array([[(0, h), (w, h), (w*0.6, h*0.6), (w*0.4, h*0.6)]], np.int32)
        cv2.fillPoly(mask, polygon, 255)
        masked_edges = cv2.bitwise_and(edges, mask)
        lines = cv2.HoughLinesP(masked_edges, 1, np.pi/180, 20, minLineLength=20, maxLineGap=100)
        
        is_departing = False
        is_turning = False  # 區分轉彎或變道
        if lines is not None:
            slopes = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if x2 != x1:  # 避免垂直線
                    slope = (y2 - y1) / (x2 - x1)
                    slopes.append(slope)
                
                # 檢查水平線 (車道線交叉，表示變道)
                if abs(y2 - y1) < 10 and (y1 > h * 0.85):
                    is_departing = True
                    
            # 如果斜率變化大，可能為轉彎
            if slopes and np.std(slopes) > 0.5:
                is_turning = True
        
        self.lane_departure_counter = self.lane_departure_counter + 1 if is_departing else 0
        if self.lane_departure_counter > self.LANE_DEPARTURE_FRAMES_THRESHOLD:
            self.lane_departure_counter = 0
            if not left_signal and not right_signal:
                if is_turning:
                    return "B02: 轉彎未打方向燈"
                else:
                    return "B01: 切換車道未打方向燈"
        return None

    def visualize(self, frame, detections):
        """繪製物件偵測的 Bounding Box"""
        frame_h = frame.shape[0]
        for box in detections:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = box.conf[0]
            class_name = self.class_names[int(box.cls[0])]
            label = f'{class_name} {conf:.2f}'

            relative_size = (y2 - y1) / frame_h
            if relative_size > self.DISTANCE_DANGER_RATIO:
                color = (0, 0, 255) # 紅色
            elif relative_size > self.DISTANCE_WARNING_RATIO:
                color = (0, 165, 255) # 橙色
            else:
                color = (0, 255, 0) # 綠色
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        return frame

    def draw_hud(self, frame):
        """### VISUALIZATION ### 繪製最終的 HUD (Head-Up Display)"""
        h, w = frame.shape[:2]
        
        # --- 頂部資訊列 ---
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 50), (0, 0, 0), -1) # 黑色背景
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame) # 半透明效果

        # 速度顯示 (模擬)
        ### DEMO-ONLY ### - 這裡的速度是為了展示效果而寫死的
        speed_text = "Speed: 65 km/h (Simulated)"
        cv2.putText(frame, speed_text, (15, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # --- 左側事件列表 ---
        if self.recent_events:
            event_y = 100
            for i, event in enumerate(self.recent_events):
                alpha = 1.0 - (i * 0.3) # 越舊的事件越透明
                
                if 'B03' in event:
                    color = (0, 0, 255) # 紅色 for 車距
                elif 'B01' in event or 'B02' in event:
                    color = (0, 165, 255) # 橙色 for 變道/轉彎
                
                # 繪製帶背景的文字
                (text_width, text_height), _ = cv2.getTextSize(event, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                
                # 半透明背景
                bg_overlay = frame.copy()
                cv2.rectangle(bg_overlay, (15, event_y - 25), (20 + text_width, event_y + 10), (0,0,0), -1)
                cv2.addWeighted(bg_overlay, 0.6 * alpha, frame, 1 - (0.6 * alpha), 0, frame)
                
                # 文字
                cv2.putText(frame, event, (20, event_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                           (int(color[0]), int(color[1]), int(color[2])), 2)
                event_y += 45
                
        return frame