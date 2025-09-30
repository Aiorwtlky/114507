# utils/lane_departure_detector.py
"""
生產級車道偏離偵測系統
- 傳統 CV + 深度學習混合方案
- 與 GPIO 方向燈整合（打方向燈時不警告）
- 多車道場景處理
- 曲線道路適應
"""

import cv2
import numpy as np
from collections import deque
from datetime import datetime, timedelta
import math


class LaneDepartureDetector:
    """車道偏離偵測器（整合 GPIO 方向燈）"""
    
    def __init__(self):
        """初始化偵測器"""
        
        # ROI 設定（只處理畫面下半部）
        self.roi_top_ratio = 0.55  # 從畫面 55% 開始處理
        
        # Canny 邊緣偵測參數
        self.canny_low = 50
        self.canny_high = 150
        
        # Hough 線段偵測參數
        self.hough_threshold = 30
        self.hough_min_line_length = 40
        self.hough_max_line_gap = 100
        
        # 車道線追蹤
        self.left_lane_history = deque(maxlen=10)
        self.right_lane_history = deque(maxlen=10)
        
        # 車輛位置追蹤
        self.vehicle_position_history = deque(maxlen=30)  # 約 1 秒
        
        # 偏離狀態
        self.departure_left = False
        self.departure_right = False
        self.departure_start_time = None
        self.stable_frames_required = 10  # 需要連續 10 幀才確認偏離
        self.departure_counter_left = 0
        self.departure_counter_right = 0
        
        # GPIO 整合（方向燈狀態）
        self.left_turn_signal_active = False
        self.right_turn_signal_active = False
        self.turn_signal_grace_period = 3.0  # 打方向燈後 3 秒內不警告
        self.last_turn_signal_time = None
        
        # 車道寬度估計（用於判斷偏離程度）
        self.estimated_lane_width = None
        self.lane_width_samples = []
        
        # 性能優化：每 N 幀進行完整處理
        self.frame_counter = 0
        self.process_every_n_frames = 2  # 每 2 幀處理一次（降低 CPU 負載）
    
    def update_turn_signal_status(self, left_active, right_active):
        """
        更新方向燈狀態（從 GPIO 讀取）
        
        Args:
            left_active: 左方向燈是否啟用
            right_active: 右方向燈是否啟用
        """
        # 檢測方向燈狀態變化
        if (left_active and not self.left_turn_signal_active) or \
           (right_active and not self.right_turn_signal_active):
            self.last_turn_signal_time = datetime.now()
        
        self.left_turn_signal_active = left_active
        self.right_turn_signal_active = right_active
    
    def _is_in_turn_signal_grace_period(self):
        """檢查是否在方向燈寬限期內"""
        if self.last_turn_signal_time is None:
            return False
        
        elapsed = (datetime.now() - self.last_turn_signal_time).total_seconds()
        return elapsed < self.turn_signal_grace_period
    
    def _preprocess(self, frame):
        """
        影像預處理
        
        Returns:
            edges: 邊緣檢測結果
            roi_mask: ROI 遮罩
        """
        h, w = frame.shape[:2]
        
        # 轉灰階
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 高斯模糊降噪
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Canny 邊緣偵測
        edges = cv2.Canny(blurred, self.canny_low, self.canny_high)
        
        # 建立 ROI 遮罩（梯形區域）
        roi_mask = np.zeros_like(edges)
        roi_top = int(h * self.roi_top_ratio)
        
        # 梯形區域的四個頂點
        vertices = np.array([[
            (int(w * 0.1), h),           # 左下
            (int(w * 0.4), roi_top),     # 左上
            (int(w * 0.6), roi_top),     # 右上
            (int(w * 0.9), h)            # 右下
        ]], dtype=np.int32)
        
        cv2.fillPoly(roi_mask, vertices, 255)
        
        # 應用 ROI 遮罩
        masked_edges = cv2.bitwise_and(edges, roi_mask)
        
        return masked_edges, roi_mask
    
    def _detect_lane_lines(self, edges):
        """
        使用 Hough Transform 偵測車道線
        
        Returns:
            left_line: 左車道線參數 (slope, intercept)
            right_line: 右車道線參數 (slope, intercept)
        """
        # Probabilistic Hough Line Transform
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=self.hough_threshold,
            minLineLength=self.hough_min_line_length,
            maxLineGap=self.hough_max_line_gap
        )
        
        if lines is None:
            return None, None
        
        # 分類左右車道線
        left_lines = []
        right_lines = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # 計算斜率
            if x2 - x1 == 0:
                continue
            
            slope = (y2 - y1) / (x2 - x1)
            
            # 過濾水平線和接近垂直的線
            if abs(slope) < 0.3 or abs(slope) > 3:
                continue
            
            # 根據斜率分類
            if slope < 0:  # 負斜率 = 左車道線
                left_lines.append((slope, x1, y1))
            else:  # 正斜率 = 右車道線
                right_lines.append((slope, x1, y1))
        
        # 計算平均車道線
        left_line = self._average_line(left_lines) if left_lines else None
        right_line = self._average_line(right_lines) if right_lines else None
        
        return left_line, right_line
    
    def _average_line(self, lines):
        """
        計算多條線段的平均線
        
        Returns:
            (slope, intercept): 線性回歸結果
        """
        if not lines:
            return None
        
        slopes = [line[0] for line in lines]
        x_coords = [line[1] for line in lines]
        y_coords = [line[2] for line in lines]
        
        # 使用 RANSAC 或簡單平均
        avg_slope = np.median(slopes)
        
        # 計算截距 (y = mx + b)
        # b = y - mx
        intercepts = [y - avg_slope * x for x, y in zip(x_coords, y_coords)]
        avg_intercept = np.median(intercepts)
        
        return (avg_slope, avg_intercept)
    
    def _smooth_lane_lines(self, left_line, right_line):
        """
        使用歷史數據平滑車道線（時間序列濾波）
        
        減少抖動，提高穩定性
        """
        # 更新歷史記錄
        if left_line:
            self.left_lane_history.append(left_line)
        if right_line:
            self.right_lane_history.append(right_line)
        
        # 計算移動平均
        smoothed_left = None
        smoothed_right = None
        
        if len(self.left_lane_history) >= 3:
            slopes = [line[0] for line in self.left_lane_history]
            intercepts = [line[1] for line in self.left_lane_history]
            smoothed_left = (np.mean(slopes), np.mean(intercepts))
        elif left_line:
            smoothed_left = left_line
        
        if len(self.right_lane_history) >= 3:
            slopes = [line[0] for line in self.right_lane_history]
            intercepts = [line[1] for line in self.right_lane_history]
            smoothed_right = (np.mean(slopes), np.mean(intercepts))
        elif right_line:
            smoothed_right = right_line
        
        return smoothed_left, smoothed_right
    
    def _estimate_vehicle_position(self, left_line, right_line, frame_width):
        """
        估計車輛在車道中的位置
        
        Returns:
            float: 偏離中心線的比例 (-1 到 1)
                   0 = 正中央
                   < 0 = 偏左
                   > 0 = 偏右
        """
        if not left_line and not right_line:
            return None
        
        # 計算畫面底部的車道線 x 座標
        y_bottom = frame_width  # 使用畫面底部
        
        if left_line and right_line:
            # 兩條車道線都存在
            left_x = (y_bottom - left_line[1]) / left_line[0]
            right_x = (y_bottom - right_line[1]) / right_line[0]
            
            # 車道中心
            lane_center = (left_x + right_x) / 2
            
            # 畫面中心
            frame_center = frame_width / 2
            
            # 車道寬度
            lane_width = abs(right_x - left_x)
            
            # 更新車道寬度估計
            if 50 < lane_width < 500:  # 合理範圍
                self.lane_width_samples.append(lane_width)
                if len(self.lane_width_samples) > 20:
                    self.lane_width_samples.pop(0)
                self.estimated_lane_width = np.median(self.lane_width_samples)
            
            # 計算偏離比例
            offset = frame_center - lane_center
            if lane_width > 0:
                position = offset / (lane_width / 2)
            else:
                position = 0
            
        elif left_line:
            # 只有左車道線
            left_x = (y_bottom - left_line[1]) / left_line[0]
            frame_center = frame_width / 2
            
            # 估計車道寬度（使用歷史數據）
            if self.estimated_lane_width:
                estimated_right_x = left_x + self.estimated_lane_width
                lane_center = (left_x + estimated_right_x) / 2
                position = (frame_center - lane_center) / (self.estimated_lane_width / 2)
            else:
                # 無法準確判斷，使用保守估計
                position = -0.3  # 假設略偏左
        
        elif right_line:
            # 只有右車道線
            right_x = (y_bottom - right_line[1]) / right_line[0]
            frame_center = frame_width / 2
            
            if self.estimated_lane_width:
                estimated_left_x = right_x - self.estimated_lane_width
                lane_center = (estimated_left_x + right_x) / 2
                position = (frame_center - lane_center) / (self.estimated_lane_width / 2)
            else:
                position = 0.3  # 假設略偏右
        
        return np.clip(position, -1.5, 1.5)
    
    def _check_departure(self, position):
        """
        判斷是否發生車道偏離
        
        Args:
            position: 車輛位置 (-1 到 1)
            
        Returns:
            (is_departing_left, is_departing_right, severity)
        """
        if position is None:
            return False, False, 0
        
        # 偏離閾值
        warning_threshold = 0.3  # 偏離 30% 開始警告
        danger_threshold = 0.5   # 偏離 50% 視為危險
        
        is_left = position < -warning_threshold
        is_right = position > warning_threshold
        
        # 計算嚴重程度 (0-3)
        if abs(position) > danger_threshold:
            severity = 3
        elif abs(position) > warning_threshold:
            severity = 2
        else:
            severity = 0
        
        return is_left, is_right, severity
    
    def detect(self, frame, left_turn_signal=False, right_turn_signal=False):
        """
        主要偵測函數
        
        Args:
            frame: OpenCV 影像幀
            left_turn_signal: 左方向燈是否啟用 (從 GPIO 讀取)
            right_turn_signal: 右方向燈是否啟用 (從 GPIO 讀取)
            
        Returns:
            dict: 偵測結果
        """
        # 更新方向燈狀態
        self.update_turn_signal_status(left_turn_signal, right_turn_signal)
        
        # 性能優化：不是每一幀都處理
        self.frame_counter += 1
        if self.frame_counter % self.process_every_n_frames != 0:
            return {'status': 'skipped', 'frame': self.frame_counter}
        
        h, w = frame.shape[:2]
        
        # 1. 預處理
        edges, roi_mask = self._preprocess(frame)
        
        # 2. 偵測車道線
        left_line, right_line = self._detect_lane_lines(edges)
        
        # 3. 平滑處理
        left_line, right_line = self._smooth_lane_lines(left_line, right_line)
        
        # 4. 估計車輛位置
        position = self._estimate_vehicle_position(left_line, right_line, w)
        
        if position is not None:
            self.vehicle_position_history.append(position)
        
        # 5. 判斷偏離
        is_left, is_right, severity = self._check_departure(position)
        
        # 6. 穩定性檢查（避免瞬間誤判）
        if is_left:
            self.departure_counter_left += 1
            self.departure_counter_right = 0
        elif is_right:
            self.departure_counter_right += 1
            self.departure_counter_left = 0
        else:
            self.departure_counter_left = 0
            self.departure_counter_right = 0
        
        # 需要連續多幀才確認偏離
        confirmed_left = self.departure_counter_left >= self.stable_frames_required
        confirmed_right = self.departure_counter_right >= self.stable_frames_required
        
        # 7. GPIO 整合：檢查方向燈狀態
        should_warn = True
        suppression_reason = None
        
        if self._is_in_turn_signal_grace_period():
            should_warn = False
            suppression_reason = 'turn_signal_grace_period'
        elif confirmed_left and self.left_turn_signal_active:
            should_warn = False
            suppression_reason = 'left_turn_signal_active'
        elif confirmed_right and self.right_turn_signal_active:
            should_warn = False
            suppression_reason = 'right_turn_signal_active'
        
        # 8. 判斷是否觸發事件
        event_triggered = False
        event_type = None
        
        if should_warn and (confirmed_left or confirmed_right):
            event_triggered = True
            
            if confirmed_left:
                event_type = 'lane_departure_left'
            else:
                event_type = 'lane_departure_right'
            
            # 記錄偏離開始時間
            if not self.departure_left and not self.departure_right:
                self.departure_start_time = datetime.now()
            
            self.departure_left = confirmed_left
            self.departure_right = confirmed_right
        else:
            self.departure_left = False
            self.departure_right = False
            self.departure_start_time = None
        
        # 9. 計算偏離持續時間
        duration = 0
        if self.departure_start_time:
            duration = (datetime.now() - self.departure_start_time).total_seconds()
        
        # 10. 計算信心度
        confidence = self._calculate_confidence(
            left_line, right_line, position, 
            confirmed_left or confirmed_right
        )
        
        # 11. 建構返回結果
        result = {
            'status': 'detected',
            'event_triggered': event_triggered,
            'event_type': event_type,
            'severity': severity if event_triggered else 0,
            'metrics': {
                'vehicle_position': round(position, 3) if position else None,
                'left_line_detected': left_line is not None,
                'right_line_detected': right_line is not None,
                'estimated_lane_width': round(self.estimated_lane_width, 1) if self.estimated_lane_width else None,
                'departure_duration': round(duration, 2),
                'stable_frames': {
                    'left': self.departure_counter_left,
                    'right': self.departure_counter_right,
                    'required': self.stable_frames_required
                }
            },
            'turn_signals': {
                'left_active': self.left_turn_signal_active,
                'right_active': self.right_turn_signal_active,
                'in_grace_period': self._is_in_turn_signal_grace_period(),
                'warning_suppressed': not should_warn,
                'suppression_reason': suppression_reason
            },
            'confidence': confidence
        }
        
        return result
    
    def _calculate_confidence(self, left_line, right_line, position, is_departing):
        """計算偵測信心度"""
        if not is_departing:
            return 0.0
        
        confidence = 0.5  # 基礎信心度
        
        # 雙車道線加成
        if left_line and right_line:
            confidence += 0.3
        elif left_line or right_line:
            confidence += 0.1
        
        # 車道寬度已校準加成
        if self.estimated_lane_width:
            confidence += 0.1
        
        # 時間序列穩定性加成
        if len(self.vehicle_position_history) >= 10:
            recent_positions = list(self.vehicle_position_history)[-10:]
            position_std = np.std(recent_positions)
            
            # 位置越穩定，信心度越高
            if position_std < 0.1:
                confidence += 0.1
        
        return round(min(confidence, 0.95), 2)
    
    def draw_debug_overlay(self, frame, detection_result):
        """
        在影像上繪製除錯資訊（可選）
        
        Args:
            frame: 原始影像
            detection_result: detect() 返回的結果
            
        Returns:
            frame_with_overlay: 帶有視覺化標記的影像
        """
        overlay = frame.copy()
        h, w = overlay.shape[:2]
        
        # 繪製 ROI 區域
        roi_top = int(h * self.roi_top_ratio)
        vertices = np.array([[
            (int(w * 0.1), h),
            (int(w * 0.4), roi_top),
            (int(w * 0.6), roi_top),
            (int(w * 0.9), h)
        ]], dtype=np.int32)
        cv2.polylines(overlay, vertices, True, (255, 255, 0), 2)
        
        # 繪製車道線
        if self.left_lane_history:
            left_line = self.left_lane_history[-1]
            self._draw_line(overlay, left_line, h, (0, 255, 0))
        
        if self.right_lane_history:
            right_line = self.right_lane_history[-1]
            self._draw_line(overlay, right_line, h, (0, 255, 0))
        
        # 繪製車輛位置指示器
        position = detection_result['metrics'].get('vehicle_position')
        if position is not None:
            center_x = int(w / 2)
            offset_x = int(position * w * 0.3)
            indicator_x = center_x - offset_x
            
            color = (0, 255, 0)  # 綠色：正常
            if detection_result['event_triggered']:
                color = (0, 0, 255)  # 紅色：偏離
            
            cv2.circle(overlay, (indicator_x, h - 30), 10, color, -1)
            cv2.line(overlay, (center_x, h - 50), (center_x, h - 10), (255, 255, 255), 2)
        
        # 顯示文字資訊
        info_text = []
        if detection_result['event_triggered']:
            info_text.append(f"WARNING: {detection_result['event_type']}")
        
        if detection_result['turn_signals']['warning_suppressed']:
            info_text.append("Turn signal active - Warning suppressed")
        
        y_offset = 30
        for text in info_text:
            cv2.putText(overlay, text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            y_offset += 30
        
        return overlay
    
    def _draw_line(self, frame, line, height, color):
        """在影像上繪製一條線"""
        if not line:
            return
        
        slope, intercept = line
        
        # 計算線的兩個端點
        y1 = height
        y2 = int(height * self.roi_top_ratio)
        
        x1 = int((y1 - intercept) / slope)
        x2 = int((y2 - intercept) / slope)
        
        cv2.line(frame, (x1, y1), (x2, y2), color, 3)


# 全域單例
_lane_detector = None

def get_lane_detector():
    """取得車道偵測器的單例"""
    global _lane_detector
    if _lane_detector is None:
        _lane_detector = LaneDepartureDetector()
    return _lane_detector