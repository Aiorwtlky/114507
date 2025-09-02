import cv2
import numpy as np
import time
import threading
from typing import Dict, Any, Optional, List, Tuple
from utils import (
    setup_logging,
    get_performance_monitor
)
from config import config

class AdasAnalyzer:
    """ADAS (Advanced Driver Assistance Systems) 分析系統"""
    
    def __init__(self, config_obj=None):
        self.config = config_obj or config
        self.logger = setup_logging()
        self.performance_monitor = get_performance_monitor('adas_analyzer')
        
        # 車道線檢測參數
        self.lane_detection_params = {
            'canny_low': 50,
            'canny_high': 150,
            'hough_threshold': 50,
            'min_line_length': 50,
            'max_line_gap': 10,
            'roi_vertices': None  # 將在第一幀時設定
        }
        
        # 物體檢測（簡化版本，實際應使用 YOLO）
        self.vehicle_detector = cv2.CascadeClassifier()
        
        # 狀態追蹤
        self.lane_departure_start_time = None
        self.close_vehicle_start_time = None
        self.red_light_violation_start_time = None
        
        # 歷史資料
        self.lane_history = []
        self.vehicle_history = []
        self.traffic_light_history = []
        
        # 方向燈狀態（需要從硬體讀取）
        self.turn_signal_left = False
        self.turn_signal_right = False
        
        # 執行緒安全
        self._lock = threading.Lock()
        
        self.logger.info("ADAS 分析系統已初始化")
    
    def analyze_frame(self, frame: np.ndarray, speed_kmh: float = 0.0, 
                     turn_signal_left: bool = False, turn_signal_right: bool = False) -> Dict[str, Any]:
        """
        分析單幀影像
        
        Args:
            frame: 輸入影像
            speed_kmh: 車輛速度 (公里/小時)
            turn_signal_left: 左方向燈狀態
            turn_signal_right: 右方向燈狀態
            
        Returns:
            Dict: 分析結果
        """
        self.performance_monitor.start_frame()
        current_time = time.time()
        
        try:
            # 更新方向燈狀態
            self.turn_signal_left = turn_signal_left
            self.turn_signal_right = turn_signal_right
            
            alerts = []
            adas_state = {}
            
            # 車道線檢測
            lane_info = self._detect_lanes(frame)
            adas_state.update(lane_info)
            
            # 車道偏離檢測
            if lane_info.get('lanes_detected', False):
                lane_alerts = self._detect_lane_departure(lane_info, current_time)
                alerts.extend(lane_alerts)
            
            # 前車檢測
            vehicle_info = self._detect_vehicles(frame)
            adas_state.update(vehicle_info)
            
            # 前車過近檢測
            if vehicle_info.get('vehicles_detected', False):
                vehicle_alerts = self._detect_close_vehicle(vehicle_info, speed_kmh, current_time)
                alerts.extend(vehicle_alerts)
            
            # 交通燈檢測
            traffic_light_info = self._detect_traffic_lights(frame)
            adas_state.update(traffic_light_info)
            
            # 闖紅燈檢測
            if traffic_light_info.get('red_light_detected', False):
                red_light_alerts = self._detect_red_light_violation(speed_kmh, current_time)
                alerts.extend(red_light_alerts)
            
            # 添加系統狀態
            adas_state.update({
                'speed_kmh': speed_kmh,
                'turn_signal_left': turn_signal_left,
                'turn_signal_right': turn_signal_right
            })
            
            result = {
                'timestamp': current_time,
                'alerts': alerts,
                'adas_state': adas_state
            }
            
            self.performance_monitor.end_frame()
            return result
            
        except Exception as e:
            self.logger.error(f"ADAS 分析時發生錯誤: {e}")
            self.performance_monitor.end_frame()
            return {
                'timestamp': current_time,
                'alerts': [],
                'adas_state': {},
                'error': str(e)
            }
    
    def _detect_lanes(self, frame: np.ndarray) -> Dict[str, Any]:
        """檢測車道線"""
        try:
            height, width = frame.shape[:2]
            
            # 設定 ROI (Region of Interest)
            if self.lane_detection_params['roi_vertices'] is None:
                self.lane_detection_params['roi_vertices'] = np.array([
                    [(0, height), (width//2 - 50, height//2 + 50), 
                     (width//2 + 50, height//2 + 50), (width, height)]
                ], dtype=np.int32)
            
            # 轉換為灰度
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 高斯濾波
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Canny 邊緣檢測
            edges = cv2.Canny(blur, 
                             self.lane_detection_params['canny_low'],
                             self.lane_detection_params['canny_high'])
            
            # 應用 ROI 遮罩
            mask = np.zeros_like(edges)
            cv2.fillPoly(mask, self.lane_detection_params['roi_vertices'], 255)
            masked_edges = cv2.bitwise_and(edges, mask)
            
            # Hough 直線檢測
            lines = cv2.HoughLinesP(
                masked_edges,
                rho=1,
                theta=np.pi/180,
                threshold=self.lane_detection_params['hough_threshold'],
                minLineLength=self.lane_detection_params['min_line_length'],
                maxLineGap=self.lane_detection_params['max_line_gap']
            )
            
            # 分析車道線
            lane_analysis = self._analyze_lane_lines(lines, width, height)
            
            # 更新歷史記錄
            with self._lock:
                self.lane_history.append({
                    'timestamp': time.time(),
                    'lanes': lane_analysis
                })
                if len(self.lane_history) > 50:
                    self.lane_history.pop(0)
            
            return {
                'lanes_detected': lines is not None and len(lines) > 0,
                'raw_lines': lines,
                'lane_analysis': lane_analysis,
                'roi_applied': True
            }
            
        except Exception as e:
            self.logger.error(f"車道線檢測錯誤: {e}")
            return {'lanes_detected': False, 'error': str(e)}
    
    def _analyze_lane_lines(self, lines: Optional[np.ndarray], width: int, height: int) -> Dict[str, Any]:
        """分析車道線"""
        if lines is None or len(lines) == 0:
            return {
                'left_lane': None,
                'right_lane': None,
                'lane_center': width // 2,
                'vehicle_position': 'center',
                'lane_width': 0
            }
        
        try:
            # 分離左右車道線
            left_lines = []
            right_lines = []
            
            for line in lines:
                x1, y1, x2, y2 = line[0]
                slope = (y2 - y1) / (x2 - x1) if x2 != x1 else 0
                
                # 根據斜率分類
                if slope < -0.5:  # 左車道線
                    left_lines.append(line[0])
                elif slope > 0.5:  # 右車道線
                    right_lines.append(line[0])
            
            # 計算平均車道線
            left_lane = self._average_lines(left_lines) if left_lines else None
            right_lane = self._average_lines(right_lines) if right_lines else None
            
            # 計算車道中心和車輛位置
            lane_center = width // 2
            vehicle_position = 'center'
            lane_width = 0
            
            if left_lane and right_lane:
                # 計算車道底部的中心點
                left_x = self._extrapolate_line(left_lane, height)
                right_x = self._extrapolate_line(right_lane, height)
                
                if left_x and right_x:
                    lane_center = (left_x + right_x) // 2
                    lane_width = abs(right_x - left_x)
                    
                    # 車輛位置偏移
                    vehicle_center = width // 2
                    offset = vehicle_center - lane_center
                    
                    if abs(offset) < lane_width * 0.1:
                        vehicle_position = 'center'
                    elif offset < 0:
                        vehicle_position = 'left'
                    else:
                        vehicle_position = 'right'
            
            return {
                'left_lane': left_lane,
                'right_lane': right_lane,
                'lane_center': lane_center,
                'vehicle_position': vehicle_position,
                'lane_width': lane_width,
                'offset_pixels': abs(width // 2 - lane_center) if lane_center else 0
            }
            
        except Exception as e:
            self.logger.error(f"車道線分析錯誤: {e}")
            return {'error': str(e)}
    
    def _average_lines(self, lines: List[List[int]]) -> Optional[Tuple[float, float]]:
        """計算線段的平均斜率和截距"""
        if not lines:
            return None
        
        try:
            slopes = []
            intercepts = []
            
            for x1, y1, x2, y2 in lines:
                if x2 != x1:
                    slope = (y2 - y1) / (x2 - x1)
                    intercept = y1 - slope * x1
                    slopes.append(slope)
                    intercepts.append(intercept)
            
            if slopes:
                avg_slope = np.mean(slopes)
                avg_intercept = np.mean(intercepts)
                return (avg_slope, avg_intercept)
            
            return None
            
        except Exception:
            return None
    
    def _extrapolate_line(self, line: Tuple[float, float], y: int) -> Optional[int]:
        """根據線性方程計算指定y座標的x值"""
        try:
            slope, intercept = line
            if slope != 0:
                x = (y - intercept) / slope
                return int(x)
            return None
        except Exception:
            return None
    
    def _detect_vehicles(self, frame: np.ndarray) -> Dict[str, Any]:
        """檢測車輛（簡化版本）"""
        try:
            # 這裡應該使用 YOLO 或其他深度學習模型
            # 目前使用簡化的邊緣檢測方法
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 簡化的車輛檢測：檢測矩形物體
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            vehicles = []
            height, width = frame.shape[:2]
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 500 < area < 10000:  # 篩選合適大小的物體
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # 簡單的車輛特徵檢查
                    aspect_ratio = w / h
                    if 0.5 < aspect_ratio < 3.0 and y > height * 0.3:  # 在下半部分
                        distance = self._estimate_distance(h, w)
                        vehicles.append({
                            'bbox': (x, y, w, h),
                            'distance': distance,
                            'area': area
                        })
            
            # 排序：距離最近的在前
            vehicles.sort(key=lambda v: v['distance'])
            
            # 更新歷史記錄
            with self._lock:
                self.vehicle_history.append({
                    'timestamp': time.time(),
                    'vehicles': vehicles
                })
                if len(self.vehicle_history) > 50:
                    self.vehicle_history.pop(0)
            
            return {
                'vehicles_detected': len(vehicles) > 0,
                'vehicles': vehicles,
                'closest_vehicle_distance': vehicles[0]['distance'] if vehicles else None
            }
            
        except Exception as e:
            self.logger.error(f"車輛檢測錯誤: {e}")
            return {'vehicles_detected': False, 'error': str(e)}
    
    def _estimate_distance(self, height: int, width: int) -> float:
        """估算距離（簡化版本）"""
        try:
            # 使用簡化的距離估算公式
            # 實際應用中需要相機校準參數
            focal_length = self.config.ai.focal_length
            real_height = self.config.ai.real_car_height
            
            if height > 0:
                distance = (focal_length * real_height) / height
                return max(1.0, min(100.0, distance))  # 限制在合理範圍
            
            return 50.0  # 預設距離
            
        except Exception:
            return 50.0
    
    def _detect_traffic_lights(self, frame: np.ndarray) -> Dict[str, Any]:
        """檢測交通燈（簡化版本）"""
        try:
            # 簡化的紅燈檢測：檢測紅色區域
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # 紅色範圍
            lower_red1 = np.array([0, 50, 50])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 50, 50])
            upper_red2 = np.array([180, 255, 255])
            
            # 綠色範圍
            lower_green = np.array([40, 50, 50])
            upper_green = np.array([80, 255, 255])
            
            # 黃色範圍
            lower_yellow = np.array([15, 50, 50])
            upper_yellow = np.array([35, 255, 255])
            
            # 建立遮罩
            red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            red_mask = red_mask1 + red_mask2
            
            green_mask = cv2.inRange(hsv, lower_green, upper_green)
            yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
            
            # 檢測圓形（交通燈的形狀）
            height, width = frame.shape[:2]
            roi_y_start = int(height * 0.1)  # 只檢測上半部分
            roi_y_end = int(height * 0.6)
            
            red_count = cv2.countNonZero(red_mask[roi_y_start:roi_y_end, :])
            green_count = cv2.countNonZero(green_mask[roi_y_start:roi_y_end, :])
            yellow_count = cv2.countNonZero(yellow_mask[roi_y_start:roi_y_end, :])
            
            # 判斷交通燈狀態
            light_threshold = 100  # 像素數閾值
            
            red_detected = red_count > light_threshold
            green_detected = green_count > light_threshold
            yellow_detected = yellow_count > light_threshold
            
            # 確定主要顏色
            traffic_light_state = 'unknown'
            confidence = 0.0
            
            max_count = max(red_count, green_count, yellow_count)
            if max_count > light_threshold:
                if red_count == max_count:
                    traffic_light_state = 'red'
                    confidence = min(1.0, red_count / 1000.0)
                elif green_count == max_count:
                    traffic_light_state = 'green'
                    confidence = min(1.0, green_count / 1000.0)
                elif yellow_count == max_count:
                    traffic_light_state = 'yellow'
                    confidence = min(1.0, yellow_count / 1000.0)
            
            # 更新歷史記錄
            traffic_light_data = {
                'timestamp': time.time(),
                'state': traffic_light_state,
                'confidence': confidence,
                'pixel_counts': {
                    'red': red_count,
                    'green': green_count,
                    'yellow': yellow_count
                }
            }
            
            with self._lock:
                self.traffic_light_history.append(traffic_light_data)
                if len(self.traffic_light_history) > 30:
                    self.traffic_light_history.pop(0)
            
            return {
                'traffic_light_detected': traffic_light_state != 'unknown',
                'traffic_light_state': traffic_light_state,
                'red_light_detected': red_detected,
                'green_light_detected': green_detected,
                'yellow_light_detected': yellow_detected,
                'confidence': confidence
            }
            
        except Exception as e:
            self.logger.error(f"交通燈檢測錯誤: {e}")
            return {
                'traffic_light_detected': False,
                'red_light_detected': False,
                'error': str(e)
            }
    
    def _detect_lane_departure(self, lane_info: Dict[str, Any], current_time: float) -> List[Dict[str, Any]]:
        """檢測車道偏離"""
        alerts = []
        
        try:
            lane_analysis = lane_info.get('lane_analysis', {})
            vehicle_position = lane_analysis.get('vehicle_position', 'center')
            offset_pixels = lane_analysis.get('offset_pixels', 0)
            
            # 設定偏離閾值
            departure_threshold = 50  # 像素
            
            # 檢查是否偏離車道
            is_departing = (
                vehicle_position != 'center' and 
                offset_pixels > departure_threshold
            )
            
            # 檢查方向燈狀態
            turn_signal_active = self.turn_signal_left or self.turn_signal_right
            
            # 只有在沒有打方向燈的情況下才算車道偏離
            if is_departing and not turn_signal_active:
                if self.lane_departure_start_time is None:
                    self.lane_departure_start_time = current_time
                
                departure_duration = current_time - self.lane_departure_start_time
                
                # 車道偏離持續時間超過閾值
                if departure_duration >= self.config.time_thresholds.get('lane_departure', 2.0):
                    alerts.append({
                        'code': 'B01',
                        'name': self.config.alert_scoring['B01']['name'],
                        'score': self.config.alert_scoring['B01']['score'],
                        'duration': departure_duration,
                        'vehicle_position': vehicle_position,
                        'offset_pixels': offset_pixels,
                        'turn_signal_active': turn_signal_active,
                        'confidence': min(1.0, offset_pixels / 100.0),
                        'timestamp': current_time
                    })
            else:
                self.lane_departure_start_time = None
        
        except Exception as e:
            self.logger.error(f"車道偏離檢測錯誤: {e}")
        
        return alerts
    
    def _detect_close_vehicle(self, vehicle_info: Dict[str, Any], speed_kmh: float, current_time: float) -> List[Dict[str, Any]]:
        """檢測前車過近"""
        alerts = []
        
        try:
            closest_distance = vehicle_info.get('closest_vehicle_distance')
            
            if closest_distance is None:
                self.close_vehicle_start_time = None
                return alerts
            
            # 根據速度計算安全距離
            safe_distance = self._calculate_safe_distance(speed_kmh)
            
            # 檢查是否過近
            is_too_close = closest_distance < safe_distance
            
            if is_too_close:
                if self.close_vehicle_start_time is None:
                    self.close_vehicle_start_time = current_time
                
                close_duration = current_time - self.close_vehicle_start_time
                
                # 前車過近持續時間超過閾值
                if close_duration >= self.config.time_thresholds.get('close_vehicle', 3.0):
                    # 計算危險程度
                    danger_level = max(0.0, (safe_distance - closest_distance) / safe_distance)
                    
                    alerts.append({
                        'code': 'B02',
                        'name': self.config.alert_scoring['B02']['name'],
                        'score': self.config.alert_scoring['B02']['score'],
                        'duration': close_duration,
                        'closest_distance': closest_distance,
                        'safe_distance': safe_distance,
                        'speed_kmh': speed_kmh,
                        'danger_level': danger_level,
                        'confidence': min(1.0, danger_level + 0.5),
                        'timestamp': current_time
                    })
            else:
                self.close_vehicle_start_time = None
        
        except Exception as e:
            self.logger.error(f"前車過近檢測錯誤: {e}")
        
        return alerts
    
    def _calculate_safe_distance(self, speed_kmh: float) -> float:
        """計算安全距離"""
        try:
            # 簡化的安全距離計算
            # 實際應考慮天氣、路況等因素
            
            if speed_kmh <= 0:
                return 5.0  # 最小安全距離
            
            # 基本公式：速度(km/h) / 3.6 * 2 秒跟車時間
            base_distance = (speed_kmh / 3.6) * 2
            
            # 最小和最大限制
            safe_distance = max(5.0, min(50.0, base_distance))
            
            return safe_distance
            
        except Exception:
            return 10.0  # 預設安全距離
    
    def _detect_red_light_violation(self, speed_kmh: float, current_time: float) -> List[Dict[str, Any]]:
        """檢測闖紅燈"""
        alerts = []
        
        try:
            # 只有在車輛移動時才檢測闖紅燈
            if speed_kmh < 5.0:  # 低於 5 km/h 認為是停車
                self.red_light_violation_start_time = None
                return alerts
            
            # 檢查最近的交通燈歷史
            recent_red_lights = []
            with self._lock:
                current_time_threshold = current_time - 2.0  # 最近2秒內
                recent_red_lights = [
                    tl for tl in self.traffic_light_history 
                    if tl['timestamp'] > current_time_threshold and 
                       tl['state'] == 'red' and 
                       tl['confidence'] > 0.5
                ]
            
            if recent_red_lights:
                if self.red_light_violation_start_time is None:
                    self.red_light_violation_start_time = current_time
                
                violation_duration = current_time - self.red_light_violation_start_time
                
                # 立即觸發闖紅燈警報
                if violation_duration >= 0.5:  # 0.5秒後確認
                    highest_confidence = max(tl['confidence'] for tl in recent_red_lights)
                    
                    alerts.append({
                        'code': 'B03',
                        'name': self.config.alert_scoring['B03']['name'],
                        'score': self.config.alert_scoring['B03']['score'],
                        'duration': violation_duration,
                        'speed_kmh': speed_kmh,
                        'red_light_confidence': highest_confidence,
                        'confidence': highest_confidence,
                        'timestamp': current_time
                    })
            else:
                self.red_light_violation_start_time = None
        
        except Exception as e:
            self.logger.error(f"闖紅燈檢測錯誤: {e}")
        
        return alerts
    
    def update_turn_signals(self, left: bool, right: bool):
        """更新方向燈狀態"""
        self.turn_signal_left = left
        self.turn_signal_right = right
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        try:
            with self._lock:
                lane_history_count = len(self.lane_history)
                vehicle_history_count = len(self.vehicle_history)
                traffic_light_history_count = len(self.traffic_light_history)
            
            performance_stats = self.performance_monitor.get_stats()
            
            return {
                'system_name': 'AdasAnalyzer',
                'status': 'running',
                'lane_history_count': lane_history_count,
                'vehicle_history_count': vehicle_history_count,
                'traffic_light_history_count': traffic_light_history_count,
                'turn_signals': {
                    'left': self.turn_signal_left,
                    'right': self.turn_signal_right
                },
                'performance': performance_stats,
                'detection_params': self.lane_detection_params
            }
            
        except Exception as e:
            return {
                'system_name': 'AdasAnalyzer',
                'status': 'error',
                'error': str(e)
            }
    
    def reset_state(self):
        """重置 ADAS 狀態"""
        try:
            with self._lock:
                self.lane_departure_start_time = None
                self.close_vehicle_start_time = None
                self.red_light_violation_start_time = None
                self.lane_history.clear()
                self.vehicle_history.clear()
                self.traffic_light_history.clear()
                self.turn_signal_left = False
                self.turn_signal_right = False
            
            self.logger.info("ADAS 分析狀態已重置")
            
        except Exception as e:
            self.logger.error(f"重置 ADAS 狀態時發生錯誤: {e}")
    
    def draw_debug_overlay(self, frame: np.ndarray, adas_state: Dict[str, Any]) -> np.ndarray:
        """在影像上繪製除錯資訊"""
        try:
            debug_frame = frame.copy()
            height, width = frame.shape[:2]
            
            # 繪製車道線
            lane_analysis = adas_state.get('lane_analysis', {})
            if lane_analysis.get('left_lane'):
                self._draw_lane_line(debug_frame, lane_analysis['left_lane'], height, (0, 255, 0))
            if lane_analysis.get('right_lane'):
                self._draw_lane_line(debug_frame, lane_analysis['right_lane'], height, (0, 255, 0))
            
            # 繪製車道中心
            lane_center = lane_analysis.get('lane_center', width // 2)
            cv2.line(debug_frame, (lane_center, height), (lane_center, height - 100), (255, 0, 0), 2)
            
            # 繪製車輛檢測框
            vehicles = adas_state.get('vehicles', [])
            for vehicle in vehicles:
                x, y, w, h = vehicle['bbox']
                distance = vehicle['distance']
                cv2.rectangle(debug_frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(debug_frame, f"{distance:.1f}m", (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            # 顯示交通燈狀態
            traffic_light_state = adas_state.get('traffic_light_state', 'unknown')
            if traffic_light_state != 'unknown':
                color = (0, 0, 255) if traffic_light_state == 'red' else \
                        (0, 255, 0) if traffic_light_state == 'green' else \
                        (0, 255, 255)
                cv2.putText(debug_frame, f"Traffic Light: {traffic_light_state}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            # 顯示方向燈狀態
            turn_info = ""
            if self.turn_signal_left:
                turn_info += "LEFT "
            if self.turn_signal_right:
                turn_info += "RIGHT"
            
            if turn_info:
                cv2.putText(debug_frame, f"Turn Signal: {turn_info}", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            return debug_frame
            
        except Exception as e:
            self.logger.error(f"繪製除錯覆蓋層錯誤: {e}")
            return frame
    
    def _draw_lane_line(self, frame: np.ndarray, line: Tuple[float, float], height: int, color: Tuple[int, int, int]):
        """繪製車道線"""
        try:
            slope, intercept = line
            y1 = height
            y2 = int(height * 0.6)
            x1 = int((y1 - intercept) / slope) if slope != 0 else 0
            x2 = int((y2 - intercept) / slope) if slope != 0 else 0
            
            cv2.line(frame, (x1, y1), (x2, y2), color, 3)
            
        except Exception:
            pass

# 如果直接執行此檔案，則進入測試模式
if __name__ == "__main__":
    import sys
    
    print("ADAS 分析測試模式")
    
    analyzer = AdasAnalyzer()
    cap = cv2.VideoCapture(config.camera.external_camera_index)
    
    if not cap.isOpened():
        print("無法開啟攝影機")
        sys.exit(1)
    
    print("開始 ADAS 分析，按 'q' 退出")
    print("按鍵控制:")
    print("  'a' - 切換左方向燈")
    print("  'd' - 切換右方向燈")
    print("  's' - 重置方向燈")
    
    # 模擬參數
    speed_kmh = 50.0
    left_signal = False
    right_signal = False
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 分析幀
            result = analyzer.analyze_frame(frame, speed_kmh, left_signal, right_signal)
            
            # 顯示警報
            if result['alerts']:
                for alert in result['alerts']:
                    print(f"ADAS 警報: {alert['code']} - {alert['name']} (信心度: {alert['confidence']:.2f})")
            
            # 繪製除錯資訊
            if result['adas_state']:
                debug_frame = analyzer.draw_debug_overlay(frame, result['adas_state'])
                
                # 顯示速度
                cv2.putText(debug_frame, f"Speed: {speed_kmh:.1f} km/h", 
                           (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imshow('ADAS Analyzer Test', debug_frame)
            
            # 處理按鍵
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('a'):
                left_signal = not left_signal
                print(f"左方向燈: {'開' if left_signal else '關'}")
            elif key == ord('d'):
                right_signal = not right_signal
                print(f"右方向燈: {'開' if right_signal else '關'}")
            elif key == ord('s'):
                left_signal = False
                right_signal = False
                print("方向燈已重置")
            elif key == ord('+'):
                speed_kmh = min(120.0, speed_kmh + 5.0)
                print(f"速度: {speed_kmh:.1f} km/h")
            elif key == ord('-'):
                speed_kmh = max(0.0, speed_kmh - 5.0)
                print(f"速度: {speed_kmh:.1f} km/h")
    
    except KeyboardInterrupt:
        print("用戶中斷測試")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("測試結束")