# detectors/outside/lane_detector.py
"""
車道偵測器 (B01, B02)
使用 OpenCV 傳統 CV 方法偵測車道線
結合 GPIO 方向燈狀態判斷違規
"""

import cv2
import numpy as np
from datetime import datetime
from collections import deque
from detectors.base_detector import BaseDetector

class LaneDetector(BaseDetector):
    """車道偵測器"""
    
    def __init__(self):
        super().__init__('LaneDetector', 'outside')
        
        # 車道偏移追蹤
        self.offset_history = deque(maxlen=30)  # 1秒歷史
        self.fps = 30
        
        # 偏移閾值（公尺）
        self.LANE_DEPARTURE_THRESHOLD = 0.3  # 偏移超過 0.3m 算偏離
        
        # 偏離狀態追蹤
        self.departure_frames = 0
        self.DEPARTURE_CONFIRM_FRAMES = 15  # 0.5秒確認
        
        # 事件去重
        self.last_event_time = {}  # {rule_id: timestamp}
        self.event_cooldown = 5.0  # 秒
        
        # 透視變換參數（需根據實際攝影機調整）
        self.src_points = np.float32([
            [550, 460],   # 左上
            [740, 460],   # 右上
            [1280, 720],  # 右下
            [128, 720]    # 左下
        ])
    
    def initialize(self):
        """初始化偵測器"""
        print(f"[{self.detector_name}] 車道偵測器已初始化")
    
    def _perspective_transform(self, img):
        """透視變換"""
        h, w = img.shape[:2]
        
        dst_points = np.float32([
            [0, 0],
            [w, 0],
            [w, h],
            [0, h]
        ])
        
        M = cv2.getPerspectiveTransform(self.src_points, dst_points)
        warped = cv2.warpPerspective(img, M, (w, h))
        
        return warped, M
    
    def _detect_lane_lines(self, img):
        """偵測車道線"""
        # 轉灰階
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 高斯模糊
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Canny 邊緣偵測
        edges = cv2.Canny(blurred, 50, 150)
        
        # 霍夫變換偵測直線
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi/180,
            threshold=50,
            minLineLength=50,
            maxLineGap=150
        )
        
        if lines is None:
            return None, None
        
        # 分離左右車道線
        left_lines = []
        right_lines = []
        
        img_center = img.shape[1] / 2
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # 計算斜率
            if x2 - x1 == 0:
                continue
            
            slope = (y2 - y1) / (x2 - x1)
            
            # 過濾接近水平的線
            if abs(slope) < 0.5:
                continue
            
            # 根據斜率和位置分類
            if slope < 0 and x1 < img_center:
                left_lines.append(line[0])
            elif slope > 0 and x1 > img_center:
                right_lines.append(line[0])
        
        return left_lines, right_lines
    
    def _calculate_offset(self, left_lines, right_lines, img_width):
        """計算車輛相對車道中心的偏移"""
        if not left_lines and not right_lines:
            return None
        
        # 計算左右車道線的平均 x 座標（底部）
        left_x = None
        right_x = None
        
        if left_lines:
            left_x = np.mean([line[2] for line in left_lines])  # x2
        
        if right_lines:
            right_x = np.mean([line[2] for line in right_lines])  # x2
        
        # 計算車道中心
        if left_x is not None and right_x is not None:
            lane_center = (left_x + right_x) / 2
        elif left_x is not None:
            lane_center = left_x + 100  # 假設車道寬度
        elif right_x is not None:
            lane_center = right_x - 100
        else:
            return None
        
        # 車輛中心
        vehicle_center = img_width / 2
        
        # 計算偏移（像素轉公尺）
        pixel_offset = vehicle_center - lane_center
        meter_offset = pixel_offset * (3.5 / 720)  # 假設 720px = 3.5m 車道寬
        
        return meter_offset
    
    def _detect_lane_change(self, offset_history):
        """
        偵測是否正在變換車道
        
        透過偏移量的變化判斷：
        - 快速橫向移動 = 變換車道
        - 大角度轉彎 = 轉彎
        """
        if len(offset_history) < 10:
            return False, 'unknown'
        
        recent_offsets = list(offset_history)[-10:]
        offset_change = abs(recent_offsets[-1] - recent_offsets[0])
        
        # 偏移變化超過 0.5m 算變換車道
        if offset_change > 0.5:
            return True, 'lane_change'
        
        # 偏移變化較大且持續 = 轉彎
        if offset_change > 0.3 and abs(recent_offsets[-1]) > 0.4:
            return True, 'turn'
        
        return False, 'unknown'
    
    def detect(self, frame, timestamp=None, **kwargs):
        """執行車道偵測"""
        if timestamp is None:
            timestamp = datetime.now()
        
        # 取得 GPIO 狀態
        left_turn_signal = kwargs.get('left_turn_signal', False)
        right_turn_signal = kwargs.get('right_turn_signal', False)
        
        h, w = frame.shape[:2]
        
        # 透視變換
        try:
            warped, M = self._perspective_transform(frame)
        except:
            return {
                'event_detected': False,
                'rule_id': None,
                'confidence': 0.0,
                'detection_data': {'status': 'transform_failed'},
                'timestamp': timestamp
            }
        
        # 偵測車道線
        left_lines, right_lines = self._detect_lane_lines(warped)
        
        if left_lines is None and right_lines is None:
            return {
                'event_detected': False,
                'rule_id': None,
                'confidence': 0.0,
                'detection_data': {'status': 'no_lanes_detected'},
                'timestamp': timestamp
            }
        
        # 計算偏移
        offset = self._calculate_offset(left_lines, right_lines, w)
        
        if offset is None:
            return {
                'event_detected': False,
                'rule_id': None,
                'confidence': 0.0,
                'detection_data': {'status': 'offset_calculation_failed'},
                'timestamp': timestamp
            }
        
        # 加入歷史
        self.offset_history.append(offset)
        
        # 判斷是否偏離車道
        is_departed = abs(offset) > self.LANE_DEPARTURE_THRESHOLD
        
        if is_departed:
            self.departure_frames += 1
        else:
            self.departure_frames = 0
        
        # 需要持續偏離才確認
        if self.departure_frames < self.DEPARTURE_CONFIRM_FRAMES:
            return {
                'event_detected': False,
                'rule_id': None,
                'confidence': 0.0,
                'detection_data': {
                    'offset': round(offset, 3),
                    'is_departed': is_departed,
                    'departure_frames': self.departure_frames
                },
                'timestamp': timestamp
            }
        
        # 判斷是變換車道還是轉彎
        is_changing, change_type = self._detect_lane_change(self.offset_history)
        
        if not is_changing:
            return {
                'event_detected': False,
                'rule_id': None,
                'confidence': 0.0,
                'detection_data': {
                    'offset': round(offset, 3),
                    'is_departed': is_departed
                },
                'timestamp': timestamp
            }
        
        # 事件判斷
        event_detected = False
        rule_id = None
        confidence = 0.0
        
        if change_type == 'lane_change':
            # B01: 變換車道未打燈
            if not left_turn_signal and not right_turn_signal:
                rule_id = 'B01'
                event_detected = True
                confidence = 0.80
                print(f"[{self.detector_name}] B01 變換車道未打燈")
        
        elif change_type == 'turn':
            # B02: 轉彎未打燈
            if not left_turn_signal and not right_turn_signal:
                rule_id = 'B02'
                event_detected = True
                confidence = 0.75
                print(f"[{self.detector_name}] B02 轉彎未打燈")
        
        # 事件去重
        if event_detected and rule_id:
            if rule_id in self.last_event_time:
                time_diff = (timestamp - self.last_event_time[rule_id]).total_seconds()
                if time_diff < self.event_cooldown:
                    event_detected = False
            
            if event_detected:
                self.last_event_time[rule_id] = timestamp
        
        return {
            'event_detected': event_detected,
            'rule_id': rule_id,
            'confidence': confidence,
            'detection_data': {
                'offset': round(offset, 3),
                'change_type': change_type,
                'left_turn_signal': left_turn_signal,
                'right_turn_signal': right_turn_signal,
                'left_lines_count': len(left_lines) if left_lines else 0,
                'right_lines_count': len(right_lines) if right_lines else 0
            },
            'timestamp': timestamp
        }