import cv2
import numpy as np
import logging
import time
from typing import Dict, List, Optional, Tuple
from collections import deque

logger = logging.getLogger(__name__)

class LightweightAdasAnalyzer:
    """輕量級 ADAS 分析器，針對樹莓派優化"""
    
    def __init__(self, config):
        self.config = config
        
        # 輕量級物件檢測 (使用 Haar Cascades 替代 YOLO 以減少資源消耗)
        self.car_cascade = None
        self.traffic_light_cascade = None
        self._load_cascades()
        
        # 車道檢測參數
        self.roi_vertices = None
        self.lane_history = deque(maxlen=10)
        
        # 距離估算參數 (基於像素大小)
        self.car_reference_width = 150  # 參考車輛寬度 (像素)
        self.safe_distance_pixels = 100  # 安全距離 (像素)
        
        # 警報狀態
        self.lane_departure_frames = 0
        self.close_following_frames = 0
        self.traffic_light_violation_frames = 0
        
        # 效能優化 - 每N幀處理一次
        self.frame_skip = 2  # 每2幀處理一次
        self.frame_count = 0
        
    def _load_cascades(self):
        """載入 Haar Cascade 分類器 (較輕量)"""
        try:
            # 嘗試載入預訓練的分類器
            car_cascade_path = f"{self.config.models_dir}/haarcascade_car.xml"
            if cv2.os.path.exists(car_cascade_path):
                self.car_cascade = cv2.CascadeClassifier(car_cascade_path)
                logger.info("車輛檢測分類器載入成功")
            else:
                logger.warning("找不到車輛檢測分類器，將使用簡化檢測")
                
        except Exception as e:
            logger.error(f"載入檢測器失敗: {e}")
    
    def set_roi(self, frame_width: int, frame_height: int):
        """設定感興趣區域 (ROI)"""
        # 設定梯形ROI用於車道檢測
        bottom_width = frame_width
        top_width = int(frame_width * 0.3)
        height_ratio = 0.6
        
        self.roi_vertices = np.array([
            [0, frame_height],
            [0, int(frame_height * height_ratio)],
            [int((frame_width - top_width) / 2), int(frame_height * 0.35)],
            [int((frame_width + top_width) / 2), int(frame_height * 0.35)],
            [frame_width, int(frame_height * height_ratio)],
            [frame_width, frame_height]
        ], dtype=np.int32)
    
    def analyze_frame(self, frame, speed_kmh: float = 0, 
                     turn_signal_left: bool = False, 
                     turn_signal_right: bool = False) -> Dict:
        """分析外鏡頭影像"""
        self.frame_count += 1
        
        result = {
            'lane_detected': False,
            'vehicles_detected': [],
            'traffic_lights': [],
            'alerts': [],
            'debug_info': {}
        }
        
        try:
            # 效能優化 - 跳幀處理
            if self.frame_count % self.frame_skip != 0:
                return result
            
            frame_height, frame_width = frame.shape[:2]
            
            # 設定ROI (如果還沒設定)
            if self.roi_vertices is None:
                self.set_roi(frame_width, frame_height)
            
            # 車道檢測
            lane_result = self.detect_lanes(frame)
            result.update(lane_result)
            
            # 車輛檢測 (簡化版)
            vehicle_result = self.detect_vehicles_lightweight(frame)
            result.update(vehicle_result)
            
            # 交通號誌檢測 (簡化版)
            traffic_result = self.detect_traffic_lights_simple(frame)
            result.update(traffic_result)
            
            # 產生警報
            alerts = self.generate_alerts(result, speed_kmh, turn_signal_left, turn_signal_right)
            result['alerts'] = alerts
            
            # 調試資訊
            result['debug_info'] = {
                'frame_skip': self.frame_skip,
                'lane_departure_frames': self.lane_departure_frames,
                'close_following_frames': self.close_following_frames,
                'processing_fps': 1.0 / self.frame_skip * self.config.external_camera_fps
            }
            
        except Exception as e:
            logger.error(f"ADAS 分析錯誤: {e}")
        
        return result
    
    def detect_lanes(self, frame) -> Dict:
        """輕量級車道檢測"""
        try:
            # 轉為灰階
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 高斯模糊
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Canny 邊緣檢測
            edges = cv2.Canny(blur, 50, 150)
            
            # 應用ROI遮罩
            mask = np.zeros_like(edges)
            cv2.fillPoly(mask, [self.roi_vertices], 255)
            masked_edges = cv2.bitwise_and(edges, mask)
            
            # Hough 線檢測
            lines = cv2.HoughLinesP(
                masked_edges, 
                rho=2, 
                theta=np.pi/180, 
                threshold=50,
                minLineLength=40,
                maxLineGap=25
            )
            
            if lines is not None:
                # 分離左右車道線
                left_lines, right_lines = self.separate_lane_lines(lines, frame.shape[1])
                
                # 計算車道中心
                lane_center = self.calculate_lane_center(left_lines, right_lines, frame.shape)
                
                # 檢測車道偏離
                frame_center = frame.shape[1] // 2
                departure_distance = abs(lane_center - frame_center) if lane_center else 0
                
                self.lane_history.append({
                    'center': lane_center,
                    'departure': departure_distance,
                    'left_lines': left_lines,
                    'right_lines': right_lines
                })
                
                return {
                    'lane_detected': True,
                    'lane_center': lane_center,
                    'departure_distance': departure_distance,
                    'left_lane_lines': left_lines,
                    'right_lane_lines': right_lines
                }
            
        except Exception as e:
            logger.error(f"車道檢測錯誤: {e}")
        
        return {'lane_detected': False}
    
    def separate_lane_lines(self, lines, frame_width) -> Tuple[List, List]:
        """分離左右車道線"""
        left_lines = []
        right_lines = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # 計算斜率
            if x2 - x1 == 0:
                continue
            slope = (y2 - y1) / (x2 - x1)
            
            # 根據斜率和位置分類
            if slope < -0.3 and x1 < frame_width // 2:  # 左車道線
                left_lines.append(line[0])
            elif slope > 0.3 and x1 > frame_width // 2:  # 右車道線
                right_lines.append(line[0])
        
        return left_lines, right_lines
    
    def calculate_lane_center(self, left_lines, right_lines, frame_shape) -> Optional[int]:
        """計算車道中心"""
        try:
            frame_height, frame_width = frame_shape[:2]
            y_eval = int(frame_height * 0.8)  # 評估位置
            
            left_x = None
            right_x = None
            
            # 計算左車道線在評估位置的x座標
            if left_lines:
                left_x_points = []
                for x1, y1, x2, y2 in left_lines:
                    if y1 != y2:
                        x = x1 + (y_eval - y1) * (x2 - x1) / (y2 - y1)
                        left_x_points.append(x)
                if left_x_points:
                    left_x = np.mean(left_x_points)
            
            # 計算右車道線在評估位置的x座標
            if right_lines:
                right_x_points = []
                for x1, y1, x2, y2 in right_lines:
                    if y1 != y2:
                        x = x1 + (y_eval - y1) * (x2 - x1) / (y2 - y1)
                        right_x_points.append(x)
                if right_x_points:
                    right_x = np.mean(right_x_points)
            
            # 計算中心
            if left_x is not None and right_x is not None:
                return int((left_x + right_x) / 2)
            elif left_x is not None:
                return int(left_x + 100)  # 假設車道寬度
            elif right_x is not None:
                return int(right_x - 100)  # 假設車道寬度
            
        except Exception as e:
            logger.error(f"車道中心計算錯誤: {e}")
        
        return None
    
    def detect_vehicles_lightweight(self, frame) -> Dict:
        """輕量級車輛檢測"""
        vehicles = []
        
        try:
            # 使用 Haar Cascade (如果可用)
            if self.car_cascade is not None:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                cars = self.car_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.1, 
                    minNeighbors=3,
                    minSize=(30, 30)
                )
                
                for (x, y, w, h) in cars:
                    # 簡單的距離估算
                    distance_pixels = self.estimate_distance(w, h)
                    
                    vehicles.append({
                        'bbox': (x, y, w, h),
                        'distance_pixels': distance_pixels,
                        'confidence': 0.7  # 固定信心度
                    })
            else:
                # 備用方案：基於輪廓的簡單檢測
                vehicles = self.detect_vehicles_contour_based(frame)
            
        except Exception as e:
            logger.error(f"車輛檢測錯誤: {e}")
        
        return {'vehicles_detected': vehicles}
    
    def detect_vehicles_contour_based(self, frame) -> List[Dict]:
        """基於輪廓的簡單車輛檢測"""
        vehicles = []
        
        try:
            # 轉為灰階
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 背景減法 (簡化版)
            blur = cv2.GaussianBlur(gray, (21, 21), 0)
            
            # 閾值處理
            _, thresh = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY)
            
            # 尋找輪廓
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # 過濾小型輪廓
                if area > 1000:
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # 檢查長寬比 (車輛通常較寬)
                    aspect_ratio = w / h
                    if 1.2 < aspect_ratio < 4.0:
                        distance_pixels = self.estimate_distance(w, h)
                        
                        vehicles.append({
                            'bbox': (x, y, w, h),
                            'distance_pixels': distance_pixels,
                            'confidence': 0.5
                        })
            
        except Exception as e:
            logger.error(f"輪廓車輛檢測錯誤: {e}")
        
        return vehicles
    
    def estimate_distance(self, width, height) -> float:
        """估算距離 (基於物件大小)"""
        # 簡化的距離估算：假設標準車輛寬度
        if width > 0:
            # 距離與寬度成反比
            distance_factor = self.car_reference_width / width
            return distance_factor * 10  # 調整係數
        return 100  # 預設距離
    
    def detect_traffic_lights_simple(self, frame) -> Dict:
        """簡化的交通號誌檢測"""
        traffic_lights = []
        
        try:
            # 轉換到HSV色彩空間
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # 紅色範圍
            red_lower1 = np.array([0, 50, 50])
            red_upper1 = np.array([10, 255, 255])
            red_lower2 = np.array([160, 50, 50])
            red_upper2 = np.array([180, 255, 255])
            
            # 綠色範圍
            green_lower = np.array([40, 50, 50])
            green_upper = np.array([80, 255, 255])
            
            # 黃色範圍
            yellow_lower = np.array([20, 50, 50])
            yellow_upper = np.array([40, 255, 255])
            
            # 檢測紅色
            red_mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
            red_mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
            red_mask = cv2.bitwise_or(red_mask1, red_mask2)
            
            # 檢測綠色
            green_mask = cv2.inRange(hsv, green_lower, green_upper)
            
            # 檢測黃色
            yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
            
            # 尋找圓形輪廓
            for color, mask in [('red', red_mask), ('green', green_mask), ('yellow', yellow_mask)]:
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 100:  # 最小面積閾值
                        # 檢查圓形度
                        perimeter = cv2.arcLength(contour, True)
                        if perimeter > 0:
                            circularity = 4 * np.pi * area / (perimeter * perimeter)
                            
                            if circularity > 0.5:  # 圓形度閾值
                                x, y, w, h = cv2.boundingRect(contour)
                                
                                traffic_lights.append({
                                    'color': color,
                                    'bbox': (x, y, w, h),
                                    'confidence': circularity
                                })
            
        except Exception as e:
            logger.error(f"交通號誌檢測錯誤: {e}")
        
        return {'traffic_lights': traffic_lights}
    
    def generate_alerts(self, analysis_result, speed_kmh, turn_signal_left, turn_signal_right) -> List[Dict]:
        """產生ADAS警報"""
        alerts = []
        
        try:
            # B01: 車道偏離檢測
            if analysis_result.get('lane_detected', False):
                departure_distance = analysis_result.get('departure_distance', 0)
                
                if departure_distance > self.config.lane_departure_threshold:
                    # 檢查方向燈狀態
                    if not (turn_signal_left or turn_signal_right):
                        self.lane_departure_frames += 1
                        
                        if self.lane_departure_frames >= int(2 * self.config.external_camera_fps / self.frame_skip):
                            alerts.append({
                                'code': 'B01',
                                'name': '車道偏離',
                                'score': 5,
                                'description': f'未打方向燈偏離車道 {departure_distance:.0f}像素'
                            })
                    else:
                        self.lane_departure_frames = 0
                else:
                    self.lane_departure_frames = 0
            
            # B02: 前車過近檢測
            vehicles = analysis_result.get('vehicles_detected', [])
            if vehicles:
                # 找最近的車輛
                closest_vehicle = min(vehicles, key=lambda v: v['distance_pixels'])
                
                if closest_vehicle['distance_pixels'] < self.safe_distance_pixels:
                    self.close_following_frames += 1
                    
                    if self.close_following_frames >= int(3 * self.config.external_camera_fps / self.frame_skip):
                        alerts.append({
                            'code': 'B02',
                            'name': '前車過近',
                            'score': 15,
                            'description': f'與前車距離過近，距離係數: {closest_vehicle["distance_pixels"]:.1f}'
                        })
                else:
                    self.close_following_frames = 0
            else:
                self.close_following_frames = 0
            
            # B03: 闖紅燈檢測
            traffic_lights = analysis_result.get('traffic_lights', [])
            red_lights = [light for light in traffic_lights if light['color'] == 'red']
            
            if red_lights and speed_kmh > 5:  # 有紅燈且車輛在移動
                self.traffic_light_violation_frames += 1
                
                if self.traffic_light_violation_frames >= int(1 * self.config.external_camera_fps / self.frame_skip):
                    alerts.append({
                        'code': 'B03',
                        'name': '闖紅燈',
                        'score': 30,
                        'description': f'紅燈時繼續行駛，速度: {speed_kmh:.1f} km/h'
                    })
            else:
                self.traffic_light_violation_frames = 0
            
        except Exception as e:
            logger.error(f"警報產生錯誤: {e}")
        
        return alerts
    
    def draw_debug_overlay(self, frame, analysis_result) -> np.ndarray:
        """繪製調試覆蓋層"""
        debug_frame = frame.copy()
        
        try:
            # 繪製ROI
            if self.roi_vertices is not None:
                cv2.polylines(debug_frame, [self.roi_vertices], True, (255, 0, 0), 2)
            
            # 繪製車道線
            if analysis_result.get('lane_detected', False):
                # 左車道線
                for line in analysis_result.get('left_lane_lines', []):
                    x1, y1, x2, y2 = line
                    cv2.line(debug_frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                
                # 右車道線
                for line in analysis_result.get('right_lane_lines', []):
                    x1, y1, x2, y2 = line
                    cv2.line(debug_frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                
                # 車道中心
                lane_center = analysis_result.get('lane_center')
                if lane_center:
                    cv2.line(debug_frame, (lane_center, 0), (lane_center, frame.shape[0]), (255, 255, 0), 2)
            
            # 繪製檢測到的車輛
            for vehicle in analysis_result.get('vehicles_detected', []):
                x, y, w, h = vehicle['bbox']
                cv2.rectangle(debug_frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(debug_frame, f"D:{vehicle['distance_pixels']:.1f}", 
                           (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            # 繪製交通號誌
            for light in analysis_result.get('traffic_lights', []):
                x, y, w, h = light['bbox']
                color_bgr = {'red': (0, 0, 255), 'green': (0, 255, 0), 'yellow': (0, 255, 255)}
                color = color_bgr.get(light['color'], (255, 255, 255))
                cv2.rectangle(debug_frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(debug_frame, light['color'], 
                           (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
        except Exception as e:
            logger.error(f"繪製調試覆蓋層錯誤: {e}")
        
        return debug_frame