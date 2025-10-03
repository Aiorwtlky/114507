# utils/lane_departure_detector.py

import cv2
import numpy as np
from collections import deque

class LaneDepartureDetector:
    """
    車道偏離偵測器（支援影片/攝影機）
    """
    
    def __init__(self, skip_undistort=True, departure_threshold=0.15):
        self.skip_undistort = skip_undistort
        self.departure_threshold = departure_threshold
        
        # 相機參數（使用 GitHub 原始參數）
        self.K = np.array([
            [1.15422732e+03, 0.00000000e+00, 6.71627794e+02],
            [0.00000000e+00, 1.14818221e+03, 3.86046312e+02],
            [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]
        ])
        self.d = np.array([
            -2.42565104e-01, -4.77893070e-02, -1.31388084e-03,
            -8.79107779e-05, 2.20573263e-02
        ])
        
        # 滑動平均
        self.offset_history = deque(maxlen=10)
        self.left_fit_history = deque(maxlen=10)
        self.right_fit_history = deque(maxlen=10)
        
    def undistort(self, img):
        """去畸變"""
        if self.skip_undistort:
            return img
        h, w = img.shape[:2]
        newcameramatrix, roi = cv2.getOptimalNewCameraMatrix(
            self.K, self.d, (w, h), 0, (w, h)
        )
        dst = cv2.undistort(img, self.K, self.d, None, newcameramatrix)
        return dst
    
    def perspective_warp(self, img):
        """透視變換"""
        h, w = img.shape[:2]
        pts_src = np.float32([
            [550, 460],
            [740, 460],
            [1280, 720],
            [128, 720]
        ])
        pts_dst = np.float32([
            [0, 0],
            [w, 0],
            [w, h],
            [0, h]
        ])
        M = cv2.getPerspectiveTransform(pts_src, pts_dst)
        warped = cv2.warpPerspective(img, M, (w, h))
        return warped, M
    
    def inv_perspective_warp(self, img, M):
        """反透視變換"""
        h, w = img.shape[:2]
        M_inv = np.linalg.inv(M)
        unwarped = cv2.warpPerspective(img, M_inv, (w, h))
        return unwarped
    
    def image_processing(self, img, s_thresh=(100, 255), sx_thresh=(15, 255)):
        """影像處理"""
        hls = cv2.cvtColor(img, cv2.COLOR_RGB2HLS).astype(float)
        h, l, s = cv2.split(hls)
        
        sobel_x = cv2.Sobel(l, cv2.CV_64F, 1, 0)
        abs_sobel = np.absolute(sobel_x)
        scaled_sobel = np.uint8(255 * abs_sobel / np.max(abs_sobel))
        
        sx_binary = np.zeros_like(scaled_sobel)
        sx_binary[(scaled_sobel >= sx_thresh[0]) & (scaled_sobel <= sx_thresh[1])] = 1
        
        s_binary = np.zeros_like(s)
        s_binary[(s >= s_thresh[0]) & (s <= s_thresh[1])] = 1
        
        combined = np.zeros_like(sx_binary)
        combined[(s_binary == 1) | (sx_binary == 1)] = 1
        
        return combined
    
    def get_histogram(self, img):
        """計算直方圖"""
        histogram = np.sum(img[img.shape[0]//2:, :], axis=0)
        return histogram
    
    def sliding_window_search(self, binary_img, n_windows=9, margin=100, min_pix=50):
        """滑動窗口搜尋"""
        histogram = self.get_histogram(binary_img)
        midpoint = int(histogram.shape[0] / 2)
        
        leftx_base = np.argmax(histogram[:midpoint])
        rightx_base = np.argmax(histogram[midpoint:]) + midpoint
        
        window_height = int(binary_img.shape[0] / n_windows)
        
        nonzero = binary_img.nonzero()
        nonzeroy = np.array(nonzero[0])
        nonzerox = np.array(nonzero[1])
        
        leftx_current = leftx_base
        rightx_current = rightx_base
        
        left_lane_inds = []
        right_lane_inds = []
        
        for window in range(n_windows):
            win_y_low = binary_img.shape[0] - (window + 1) * window_height
            win_y_high = binary_img.shape[0] - window * window_height
            
            win_xleft_low = leftx_current - margin
            win_xleft_high = leftx_current + margin
            win_xright_low = rightx_current - margin
            win_xright_high = rightx_current + margin
            
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
            
            if len(good_left_inds) > min_pix:
                leftx_current = int(np.mean(nonzerox[good_left_inds]))
            if len(good_right_inds) > min_pix:
                rightx_current = int(np.mean(nonzerox[good_right_inds]))
        
        left_lane_inds = np.concatenate(left_lane_inds)
        right_lane_inds = np.concatenate(right_lane_inds)
        
        leftx = nonzerox[left_lane_inds]
        lefty = nonzeroy[left_lane_inds]
        rightx = nonzerox[right_lane_inds]
        righty = nonzeroy[right_lane_inds]
        
        if len(leftx) > 0 and len(rightx) > 0:
            left_fit = np.polyfit(lefty, leftx, 2)
            right_fit = np.polyfit(righty, rightx, 2)
            
            self.left_fit_history.append(left_fit)
            self.right_fit_history.append(right_fit)
            
            left_fit = np.mean(self.left_fit_history, axis=0)
            right_fit = np.mean(self.right_fit_history, axis=0)
        else:
            return None, None
        
        return left_fit, right_fit
    
    def calculate_offset(self, img, left_fit, right_fit):
        """計算偏移量"""
        xm_per_pix = 3.7 / 720
        y_eval = img.shape[0]
        
        left_x = left_fit[0] * y_eval**2 + left_fit[1] * y_eval + left_fit[2]
        right_x = right_fit[0] * y_eval**2 + right_fit[1] * y_eval + right_fit[2]
        
        lane_center = (left_x + right_x) / 2
        car_center = img.shape[1] / 2
        
        offset = (car_center - lane_center) * xm_per_pix
        
        return offset
    
    def detect(self, frame, draw_visualization=False):
        """主偵測函數"""
        try:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = self.undistort(img)
            
            warped, M = self.perspective_warp(img)
            binary = self.image_processing(warped)
            
            left_fit, right_fit = self.sliding_window_search(binary)
            
            if left_fit is None or right_fit is None:
                return {
                    'departed': False,
                    'offset': 0.0,
                    'direction': 'unknown',
                    'confidence': 0.0,
                    'left_fit': None,
                    'right_fit': None,
                    'binary': binary if draw_visualization else None,
                    'visualization': frame if draw_visualization else None
                }
            
            offset = self.calculate_offset(img, left_fit, right_fit)
            self.offset_history.append(offset)
            offset_avg = np.mean(self.offset_history)
            
            departed = abs(offset_avg) > self.departure_threshold
            
            if offset_avg > 0.10:
                direction = 'right'
            elif offset_avg < -0.10:
                direction = 'left'
            else:
                direction = 'center'
            
            result = {
                'departed': departed,
                'offset': offset_avg,
                'direction': direction,
                'confidence': 1.0 if len(self.offset_history) >= 5 else 0.5,
                'left_fit': left_fit,
                'right_fit': right_fit,
                'binary': binary if draw_visualization else None,
                'visualization': None
            }
            
            if draw_visualization:
                result['visualization'] = self._draw_lanes(
                    frame, binary, left_fit, right_fit, offset_avg, departed, M
                )
            
            return result
            
        except Exception as e:
            print(f"[Lane Detection Error] {e}")
            return {
                'departed': False,
                'offset': 0.0,
                'direction': 'unknown',
                'confidence': 0.0,
                'left_fit': None,
                'right_fit': None,
                'binary': None,
                'visualization': frame if draw_visualization else None
            }
    
    def _draw_lanes(self, frame, binary, left_fit, right_fit, offset, departed, M):
        """繪製車道線"""
        ploty = np.linspace(0, frame.shape[0]-1, frame.shape[0])
        
        left_fitx = left_fit[0]*ploty**2 + left_fit[1]*ploty + left_fit[2]
        right_fitx = right_fit[0]*ploty**2 + right_fit[1]*ploty + right_fit[2]
        
        warp_zero = np.zeros_like(binary).astype(np.uint8)
        color_warp = np.dstack((warp_zero, warp_zero, warp_zero))
        
        pts_left = np.array([np.transpose(np.vstack([left_fitx, ploty]))])
        pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fitx, ploty])))])
        pts = np.hstack((pts_left, pts_right))
        
        color = (0, 255, 0) if not departed else (0, 0, 255)
        cv2.fillPoly(color_warp, np.int_([pts]), color)
        
        # 反透視變換
        newwarp = self.inv_perspective_warp(color_warp, M)
        result = cv2.addWeighted(frame, 1, newwarp, 0.3, 0)
        
        # 繪製資訊
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(result, f'Offset: {offset:.2f}m', (50, 50), font, 1, (255, 255, 255), 2)
        
        status_color = (0, 0, 255) if departed else (0, 255, 0)
        status_text = 'DEPARTED!' if departed else 'Normal'
        cv2.putText(result, status_text, (50, 100), font, 1, status_color, 2)
        
        return result