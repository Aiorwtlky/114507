# detectors/outside/lane_detector.py
"""
車道偵測器 (B01, B02)
基於滑動窗口算法 + 偏移量監測
優化版：ROI處理 + 歷史平滑 + 簡化事件邏輯
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
        
        # 相機參數（固定，避免重複計算）
        self.K = np.array([
            [1.15422732e+03, 0.00000000e+00, 6.71627794e+02],
            [0.00000000e+00, 1.14818221e+03, 3.86046312e+02],
            [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]
        ])
        self.d = np.array([
            -2.42565104e-01, -4.77893070e-02, -1.31388084e-03,
            -8.79107779e-05, 2.20573263e-02
        ])
        
        # 透視變換參數
        self.src_points = np.float32([
            [550, 460], [740, 460],
            [1280, 720], [128, 720]
        ])
        
        # 歷史平滑（移動平均）
        self.offset_history = deque(maxlen=10)
        self.left_fit_history = deque(maxlen=10)
        self.right_fit_history = deque(maxlen=10)
        
        # 偏離閾值（公尺）
        self.DEPARTURE_THRESHOLD = 0.3  # 偏移超過 0.3m
        self.CONTINUOUS_FRAMES = 60      # 持續 2 秒（假設 30 FPS）
        
        # 狀態追蹤
        self.departure_start_time = None
        self.departure_frames = 0
        
        # 事件去重
        self.last_event_time = None
        self.event_cooldown = 5.0
        
        # 效能優化標記
        self.skip_undistort = True  # 跳過去畸變（提升速度）
        
    
    def initialize(self):
        """初始化偵測器"""
        print(f"[{self.detector_name}] 車道偵測器已初始化（滑動窗口算法）")
    
    def _undistort(self, img):
        """去畸變（可選）"""
        if self.skip_undistort:
            return img
        
        h, w = img.shape[:2]
        newcameramatrix, roi = cv2.getOptimalNewCameraMatrix(
            self.K, self.d, (w, h), 0, (w, h)
        )
        dst = cv2.undistort(img, self.K, self.d, None, newcameramatrix)
        return dst
    
    def _perspective_warp(self, img):
        """透視變換"""
        h, w = img.shape[:2]
        dst_points = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        M = cv2.getPerspectiveTransform(self.src_points, dst_points)
        warped = cv2.warpPerspective(img, M, (w, h))
        return warped, M
    
    def _image_processing(self, img):
        """影像處理：提取車道線特徵"""
        # 轉 HLS 色彩空間
        hls = cv2.cvtColor(img, cv2.COLOR_RGB2HLS).astype(float)
        h, l, s = cv2.split(hls)
        
        # Sobel X 梯度
        sobel_x = cv2.Sobel(l, cv2.CV_64F, 1, 0)
        abs_sobel = np.absolute(sobel_x)
        scaled_sobel = np.uint8(255 * abs_sobel / (np.max(abs_sobel) + 1e-6))
        
        # 閾值處理
        sx_binary = np.zeros_like(scaled_sobel)
        sx_binary[(scaled_sobel >= 15) & (scaled_sobel <= 255)] = 1
        
        s_binary = np.zeros_like(s)
        s_binary[(s >= 100) & (s <= 255)] = 1
        
        # 合併
        combined = np.zeros_like(sx_binary)
        combined[(s_binary == 1) | (sx_binary == 1)] = 1
        
        return combined
    
    def _get_histogram(self, img):
        """計算直方圖"""
        histogram = np.sum(img[img.shape[0]//2:, :], axis=0)
        return histogram
    
    def _sliding_window(self, binary_img):
        """滑動窗口搜尋車道線"""
        histogram = self._get_histogram(binary_img)
        midpoint = int(histogram.shape[0] / 2)
        
        # 找左右車道基準點
        leftx_base = np.argmax(histogram[:midpoint])
        rightx_base = np.argmax(histogram[midpoint:]) + midpoint
        
        # 設定窗口參數
        n_windows = 9
        margin = 100
        min_pix = 50
        window_height = int(binary_img.shape[0] / n_windows)
        
        # 找所有非零像素
        nonzero = binary_img.nonzero()
        nonzeroy = np.array(nonzero[0])
        nonzerox = np.array(nonzero[1])
        
        # 當前窗口位置
        leftx_current = leftx_base
        rightx_current = rightx_base
        
        # 儲存車道像素索引
        left_lane_inds = []
        right_lane_inds = []
        
        # 滑動窗口
        for window in range(n_windows):
            win_y_low = binary_img.shape[0] - (window + 1) * window_height
            win_y_high = binary_img.shape[0] - window * window_height
            
            win_xleft_low = leftx_current - margin
            win_xleft_high = leftx_current + margin
            win_xright_low = rightx_current - margin
            win_xright_high = rightx_current + margin
            
            # 找窗口內的像素
            good_left_inds = (
                (nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
                (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high)
            ).nonzero()[0]
            
            good_right_inds = (
                (nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
                (nonzerox >= win_xright_low) & (nonzerox < win_xright_high)
            ).nonzero()[0]
            
            left_lane_inds.append(good_left_inds)
            right_lane_inds.append(good_right_inds)
            
            # 重新定位窗口中心
            if len(good_left_inds) > min_pix:
                leftx_current = int(np.mean(nonzerox[good_left_inds]))
            if len(good_right_inds) > min_pix:
                rightx_current = int(np.mean(nonzerox[good_right_inds]))
        
        # 合併索引
        left_lane_inds = np.concatenate(left_lane_inds)
        right_lane_inds = np.concatenate(right_lane_inds)
        
        # 提取像素位置
        leftx = nonzerox[left_lane_inds]
        lefty = nonzeroy[left_lane_inds]
        rightx = nonzerox[right_lane_inds]
        righty = nonzeroy[right_lane_inds]
        
        # 擬合二次曲線
        if len(leftx) > 0 and len(rightx) > 0:
            left_fit = np.polyfit(lefty, leftx, 2)
            right_fit = np.polyfit(righty, rightx, 2)
            
            # 歷史平滑
            self.left_fit_history.append(left_fit)
            self.right_fit_history.append(right_fit)
            
            left_fit = np.mean(self.left_fit_history, axis=0)
            right_fit = np.mean(self.right_fit_history, axis=0)
            
            return left_fit, right_fit, len(leftx), len(rightx)
        
        return None, None, 0, 0
    
    def _calculate_offset(self, img, left_fit, right_fit):
        """計算車輛偏移量（公尺）"""
        xm_per_pix = 3.7 / 720  # 米/像素
        y_eval = img.shape[0]
        
        # 計算車道線底部 x 座標
        left_x = left_fit[0] * y_eval**2 + left_fit[1] * y_eval + left_fit[2]
        right_x = right_fit[0] * y_eval**2 + right_fit[1] * y_eval + right_fit[2]
        
        # 車道中心
        lane_center = (left_x + right_x) / 2
        
        # 車輛中心
        car_center = img.shape[1] / 2
        
        # 計算偏移
        offset = (car_center - lane_center) * xm_per_pix
        
        return offset
    
    def detect(self, frame, timestamp=None, **kwargs):
        """執行車道偵測"""
        if timestamp is None:
            timestamp = datetime.now()
        
        # 取得 GPIO 狀態
        left_turn_signal = kwargs.get('left_turn_signal', False)
        right_turn_signal = kwargs.get('right_turn_signal', False)
        
        try:
            # ROI 優化：只處理下半部
            h, w = frame.shape[:2]
            roi = frame[int(h*0.3):h, :]  # 只處理下 70%
            
            # 轉 RGB
            img = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
            
            # 去畸變（可選）
            img = self._undistort(img)
            
            # 透視變換
            warped, M = self._perspective_warp(img)
            
            # 影像處理
            binary = self._image_processing(warped)
            
            # 滑動窗口搜尋
            left_fit, right_fit, left_pixels, right_pixels = self._sliding_window(binary)
            
            # 檢查是否成功偵測
            if left_fit is None or right_fit is None:
                self.departure_frames = 0
                return {
                    'event_detected': False,
                    'rule_id': None,
                    'confidence': 0.0,
                    'detection_data': {
                        'status': 'no_lanes',
                        'left_pixels': left_pixels,
                        'right_pixels': right_pixels
                    },
                    'timestamp': timestamp
                }
            
            # 計算偏移量
            offset = self._calculate_offset(warped, left_fit, right_fit)
            
            # 歷史平滑
            self.offset_history.append(offset)
            offset_avg = np.mean(self.offset_history)
            
            # 判斷是否偏離
            is_departed = abs(offset_avg) > self.DEPARTURE_THRESHOLD
            
            if is_departed:
                if self.departure_start_time is None:
                    self.departure_start_time = timestamp
                self.departure_frames += 1
            else:
                self.departure_start_time = None
                self.departure_frames = 0
            
            # 判斷是否觸發事件
            event_detected = False
            confidence = 0.0
            
            # 核心邏輯：持續偏離 2 秒 + 沒打方向燈 = 觸發
            if self.departure_frames >= self.CONTINUOUS_FRAMES:
                if not (left_turn_signal or right_turn_signal):
                    event_detected = True
                    confidence = 0.85
                    
                    # 事件去重
                    if self.last_event_time:
                        time_diff = (timestamp - self.last_event_time).total_seconds()
                        if time_diff < self.event_cooldown:
                            event_detected = False
                    
                    if event_detected:
                        self.last_event_time = timestamp
                        duration = (timestamp - self.departure_start_time).total_seconds()
                        print(f"[{self.detector_name}] B01 車道偏離未打燈 (偏移: {offset_avg:.2f}m, 持續: {duration:.1f}s)")
            
            return {
                'event_detected': event_detected,
                'rule_id': 'B01' if event_detected else None,  # 統一用 B01
                'confidence': confidence,
                'detection_data': {
                    'offset': round(offset_avg, 3),
                    'is_departed': is_departed,
                    'departure_frames': self.departure_frames,
                    'left_turn_signal': left_turn_signal,
                    'right_turn_signal': right_turn_signal,
                    'left_pixels': left_pixels,
                    'right_pixels': right_pixels
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