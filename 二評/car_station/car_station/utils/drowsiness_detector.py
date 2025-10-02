# utils/drowsiness_detector.py - 最終優化版
"""
生產級疲勞駕駛偵測系統 - 最終版
- 個體化校準
- 動態閾值適應
- 相對變化判斷
- 完整異常處理
"""

import cv2
import numpy as np
import mediapipe as mp
from scipy.spatial import distance
from collections import deque
from datetime import datetime, timedelta
import json
import os


def denormalize_coordinates(x, y, frame_width, frame_height):
    """將 MediaPipe 正規化座標轉換為像素座標"""
    x_px = min(int(x * frame_width), frame_width - 1)
    y_px = min(int(y * frame_height), frame_height - 1)
    return (x_px, y_px)


class PersonalizedDrowsinessDetector:
    """個體化疲勞駕駛偵測器 - 最終優化版"""
    
    def __init__(self, driver_id=None):
        self.driver_id = driver_id
        
        # MediaPipe Face Mesh 初始化
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # 眼睛關鍵點索引
        self.LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
        
        # 個體化基準值
        self.baseline_ear = None
        self.calibration_samples = []
        self.is_calibrated = False
        
        # 時間序列緩衝區
        self.ear_history = deque(maxlen=30)
        self.blink_history = deque(maxlen=300)
        
        # 狀態追蹤
        self.consecutive_closed_frames = 0
        self.total_blinks = 0
        self.last_detection_time = datetime.now()
        
        # 視覺化顏色
        self.COLOR_GREEN = (0, 255, 0)
        self.COLOR_RED = (0, 0, 255)
        self.COLOR_YELLOW = (0, 255, 255)
        
        # 載入校準數據
        self._load_calibration()
    
    def get_adaptive_threshold_factor(self):
        """
        根據 baseline_ear 動態調整閾值因子
        baseline 越小（眼睛越小），閾值因子越高（更寬鬆）
        """
        if not self.baseline_ear:
            return 0.75
        
        if self.baseline_ear >= 0.30:
            return 0.72  # 大眼睛：更嚴格
        elif self.baseline_ear >= 0.25:
            return 0.75  # 中等眼睛：標準
        elif self.baseline_ear >= 0.20:
            return 0.78  # 小眼睛：稍寬鬆
        else:
            return 0.82  # 極小眼睛：明顯寬鬆
    
    def _load_calibration(self):
        """載入駕駛員的個人化校準數據"""
        if not self.driver_id:
            return
        
        calibration_file = f"calibrations/driver_{self.driver_id}.json"
        if os.path.exists(calibration_file):
            try:
                with open(calibration_file, 'r') as f:
                    data = json.load(f)
                    
                    calibrated_at_str = data.get('calibrated_at')
                    if calibrated_at_str:
                        calibrated_at = datetime.fromisoformat(calibrated_at_str)
                        days_old = (datetime.now() - calibrated_at).days
                        
                        if days_old > 30:
                            print(f"⚠️ 校準數據已過期（{days_old} 天前），將重新校準")
                            return
                    
                    self.baseline_ear = data.get('baseline_ear')
                    
                    if self.baseline_ear and 0.15 <= self.baseline_ear <= 0.45:
                        self.is_calibrated = True
                        threshold_factor = self.get_adaptive_threshold_factor()
                        print(f"✅ 載入駕駛員 {self.driver_id} 的校準數據")
                        print(f"   基準 EAR: {self.baseline_ear:.3f}")
                        print(f"   閾值因子: {threshold_factor:.2f} (動態調整)")
                        print(f"   閉眼閾值: {self.baseline_ear * threshold_factor:.3f}")
                    else:
                        print(f"⚠️ 校準數據異常: EAR={self.baseline_ear}，將重新校準")
                        self.baseline_ear = None
                        
            except Exception as e:
                print(f"⚠️ 載入校準數據失敗: {e}")
    
    def save_calibration(self):
        """儲存個人化校準數據"""
        if not self.driver_id or not self.is_calibrated:
            return
        
        try:
            os.makedirs("calibrations", exist_ok=True)
            calibration_file = f"calibrations/driver_{self.driver_id}.json"
            
            threshold_factor = self.get_adaptive_threshold_factor()
            
            data = {
                'driver_id': self.driver_id,
                'baseline_ear': float(self.baseline_ear),
                'threshold_factor': float(threshold_factor),
                'calibrated_at': datetime.now().isoformat()
            }
            
            with open(calibration_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ 已儲存駕駛員 {self.driver_id} 的校準數據")
        except Exception as e:
            print(f"⚠️ 儲存校準數據失敗: {e}")
    
    def calibrate(self, frame):
        """個體化校準程序"""
        if self.is_calibrated:
            return True
        
        try:
            if frame is None or frame.size == 0:
                return False
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark
                h, w = frame.shape[:2]
                
                left_ear, _ = self._calculate_ear_with_coords(landmarks, self.LEFT_EYE_INDICES, w, h)
                right_ear, _ = self._calculate_ear_with_coords(landmarks, self.RIGHT_EYE_INDICES, w, h)
                avg_ear = (left_ear + right_ear) / 2.0
                
                if 0.15 < avg_ear < 0.5:  # 放寬範圍
                    self.calibration_samples.append(avg_ear)
                
                if len(self.calibration_samples) >= 30:
                    self.baseline_ear = np.median(self.calibration_samples)
                    
                    if 0.15 <= self.baseline_ear <= 0.45:
                        self.is_calibrated = True
                        threshold_factor = self.get_adaptive_threshold_factor()
                        
                        print(f"✅ 校準完成！駕駛員基準 EAR: {self.baseline_ear:.3f}")
                        print(f"   閾值因子: {threshold_factor:.2f} (動態調整)")
                        print(f"   閉眼閾值: {self.baseline_ear * threshold_factor:.3f}")
                        
                        # 警告：極小眼睛
                        if self.baseline_ear < 0.20:
                            print(f"⚠️ 警告：基準 EAR 較低 ({self.baseline_ear:.3f})")
                            print(f"   系統已自動調整為更寬鬆的閾值因子 ({threshold_factor:.2f})")
                        
                        self.save_calibration()
                        return True
                    else:
                        print(f"⚠️ 校準結果異常: EAR={self.baseline_ear:.3f}")
                        self.calibration_samples.clear()
                        return False
            
            progress = len(self.calibration_samples)
            if progress % 10 == 0 and progress > 0:
                print(f"🔧 校準中... {progress}/30 樣本")
            
        except Exception as e:
            print(f"⚠️ 校準過程發生錯誤: {e}")
            return False
        
        return False
    
    def _calculate_ear_with_coords(self, landmarks, eye_indices, frame_width, frame_height):
        """計算 EAR 並返回座標點"""
        try:
            coords_points = []
            for idx in eye_indices:
                if idx < len(landmarks):
                    lm = landmarks[idx]
                    coord = denormalize_coordinates(lm.x, lm.y, frame_width, frame_height)
                    coords_points.append(coord)
                else:
                    return 0.0, None
            
            P2_P6 = distance.euclidean(coords_points[1], coords_points[5])
            P3_P5 = distance.euclidean(coords_points[2], coords_points[4])
            P1_P4 = distance.euclidean(coords_points[0], coords_points[3])
            
            if P1_P4 < 0.001:
                return 0.0, None
            
            ear = (P2_P6 + P3_P5) / (2.0 * P1_P4)
            
            return (ear if 0 <= ear <= 1.0 else 0.0), coords_points
            
        except Exception as e:
            return 0.0, None
    
    def _draw_eye_landmarks(self, frame, left_coords, right_coords, color):
        """在畫面上繪製眼睛標記點"""
        if frame is None:
            return frame
        
        frame_copy = frame.copy()
        
        for coords in [left_coords, right_coords]:
            if coords:
                for coord in coords:
                    if coord:
                        cv2.circle(frame_copy, coord, 2, color, -1)
        
        return frame_copy
    
    def _draw_info_text(self, frame, ear, closed_frames, event_text=None):
        """在畫面上繪製資訊文字"""
        if frame is None:
            return frame
        
        h, w = frame.shape[:2]
        frame_copy = frame.copy()
        
        color = self.COLOR_GREEN if closed_frames == 0 else self.COLOR_RED
        cv2.putText(frame_copy, f"EAR: {ear:.3f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        if closed_frames > 0:
            cv2.putText(frame_copy, f"Closed: {closed_frames} frames", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.COLOR_YELLOW, 2)
        
        if event_text:
            cv2.rectangle(frame_copy, (0, h-80), (w, h), self.COLOR_RED, -1)
            cv2.putText(frame_copy, f"WARNING: {event_text}", (10, h-40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3)
        
        return frame_copy
    
    def _analyze_blink_frequency(self):
        """分析眨眼頻率"""
        if len(self.blink_history) < 100:
            return 'normal'
        
        try:
            recent_blinks = sum(1 for t in self.blink_history 
                              if t > datetime.now() - timedelta(seconds=60))
            
            if recent_blinks < 10:
                return 'too_low'
            elif recent_blinks > 30:
                return 'too_high'
            else:
                return 'normal'
        except:
            return 'normal'
    
    def detect(self, frame, draw_landmarks=False):
        """
        主要偵測函數
        
        使用雙重判斷機制：
        1. 絕對閾值判斷（動態閾值因子）
        2. 相對變化判斷（EAR 下降率）
        """
        output_frame = frame
        
        try:
            if frame is None or frame.size == 0:
                return {'status': 'error', 'message': '無效的影像幀'}, output_frame
            
            if not self.is_calibrated:
                self.calibrate(frame)
                return {
                    'status': 'calibrating',
                    'progress': len(self.calibration_samples),
                    'required': 30
                }, output_frame
            
            h, w = frame.shape[:2]
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            if not results.multi_face_landmarks:
                return {'status': 'no_face', 'message': '未偵測到臉部'}, output_frame
            
            landmarks = results.multi_face_landmarks[0].landmark
            
            # 計算 EAR
            left_ear, left_coords = self._calculate_ear_with_coords(landmarks, self.LEFT_EYE_INDICES, w, h)
            right_ear, right_coords = self._calculate_ear_with_coords(landmarks, self.RIGHT_EYE_INDICES, w, h)
            avg_ear = (left_ear + right_ear) / 2.0
            
            if avg_ear <= 0:
                return {'status': 'error', 'message': 'EAR 計算失敗'}, output_frame
            
            self.ear_history.append(avg_ear)
            
            # 動態閾值
            threshold_factor = self.get_adaptive_threshold_factor()
            ear_threshold = self.baseline_ear * threshold_factor
            
            # 雙重判斷機制
            # 方法1：絕對閾值
            is_closed_absolute = avg_ear < ear_threshold
            
            # 方法2：相對變化（EAR 下降率）
            ear_drop_ratio = (self.baseline_ear - avg_ear) / self.baseline_ear
            is_closed_relative = ear_drop_ratio > 0.25  # 下降超過 25%
            
            # 綜合判斷（兩者滿足其一即判定為閉眼）
            is_eyes_closed = is_closed_absolute or is_closed_relative
            
            if is_eyes_closed:
                self.consecutive_closed_frames += 1
            else:
                if 2 < self.consecutive_closed_frames < 10:
                    self.total_blinks += 1
                    self.blink_history.append(datetime.now())
                self.consecutive_closed_frames = 0
            
            # 疲勞等級判斷（只在剛達到時觸發）
            drowsiness_level = 0
            event_type = None
            duration = self.consecutive_closed_frames / 30.0
            
            if self.consecutive_closed_frames == 90:  # 剛達到 3 秒
                drowsiness_level = 3
                event_type = 'drowsy_severe'
                self.last_detection_time = datetime.now()
            elif self.consecutive_closed_frames == 30:  # 剛達到 1 秒
                drowsiness_level = 2
                event_type = 'drowsy_moderate'
                self.last_detection_time = datetime.now()
            
            # 眨眼頻率分析
            blink_status = self._analyze_blink_frequency()
            
            # 視覺化繪製
            if draw_landmarks:
                color = self.COLOR_GREEN if not is_eyes_closed else self.COLOR_RED
                output_frame = self._draw_eye_landmarks(frame, left_coords, right_coords, color)
                
                event_text = None
                if event_type:
                    event_map = {
                        'drowsy_severe': 'A01 - 重度疲勞',
                        'drowsy_moderate': 'A02 - 中度疲勞'
                    }
                    event_text = event_map.get(event_type)
                
                output_frame = self._draw_info_text(output_frame, avg_ear, 
                                                    self.consecutive_closed_frames, 
                                                    event_text)
            
            # 建構返回結果
            result = {
                'status': 'detected',
                'drowsiness_level': drowsiness_level,
                'event_type': event_type,
                'metrics': {
                    'ear': round(avg_ear, 3),
                    'baseline_ear': round(self.baseline_ear, 3),
                    'ear_threshold': round(ear_threshold, 3),
                    'ear_drop_ratio': round(ear_drop_ratio, 3),
                    'closed_duration': round(duration, 2),
                    'closed_frames': self.consecutive_closed_frames,
                    'total_blinks': self.total_blinks,
                    'blink_frequency': blink_status,
                    'threshold_factor': round(threshold_factor, 2)
                },
                'confidence': self._calculate_confidence(drowsiness_level, avg_ear, ear_threshold)
            }
            
            return result, output_frame
            
        except Exception as e:
            print(f"⚠️ 偵測過程發生錯誤: {e}")
            import traceback
            traceback.print_exc()
            return {'status': 'error', 'message': str(e)}, output_frame
    
    def _calculate_confidence(self, level, ear, threshold):
        """計算偵測信心度"""
        if level == 0:
            return 0.0
        
        try:
            ear_ratio = 1.0 - (ear / threshold) if ear < threshold else 0.0
            base_confidence = min(ear_ratio * 1.5, 1.0)
            
            if len(self.ear_history) >= 10:
                recent_ears = list(self.ear_history)[-10:]
                ear_std = np.std(recent_ears)
                stability_factor = 1.0 - min(ear_std / 0.05, 0.3)
            else:
                stability_factor = 0.7
            
            calibration_factor = 1.0 if self.is_calibrated else 0.8
            confidence = base_confidence * stability_factor * calibration_factor
            
            return round(min(max(confidence, 0.0), 0.99), 2)
        except:
            return 0.75  # 固定值避免計算失敗


# 全域單例
_drowsiness_detector = None

def get_drowsiness_detector(driver_id=None):
    """取得疲勞偵測器的單例"""
    global _drowsiness_detector
    if _drowsiness_detector is None or (driver_id and _drowsiness_detector.driver_id != driver_id):
        _drowsiness_detector = PersonalizedDrowsinessDetector(driver_id)
    return _drowsiness_detector