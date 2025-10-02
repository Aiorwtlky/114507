# utils/drowsiness_detector.py - 修正誤判版
"""
生產級疲勞駕駛偵測系統
A01: 閉眼 ≥ 3 秒
A02: 閉眼 1-3 秒
A04: 無臉部 ≥ 5 秒
"""

import cv2
import numpy as np
import mediapipe as mp
from scipy.spatial import distance
from collections import deque
from datetime import datetime
import json
import os


def denormalize_coordinates(x, y, frame_width, frame_height):
    x_px = min(int(x * frame_width), frame_width - 1)
    y_px = min(int(y * frame_height), frame_height - 1)
    return (x_px, y_px)


class PersonalizedDrowsinessDetector:
    
    def __init__(self, driver_id=None):
        self.driver_id = driver_id
        
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
        
        self.baseline_ear = None
        self.calibration_samples = []
        self.is_calibrated = False
        
        self.ear_history = deque(maxlen=30)
        
        self.consecutive_closed_frames = 0
        self.consecutive_no_face_frames = 0
        self.total_blinks = 0
        
        self.COLOR_GREEN = (0, 255, 0)
        self.COLOR_RED = (0, 0, 255)
        
        self._load_calibration()
    
    def get_adaptive_threshold_factor(self):
        """更嚴格的閾值"""
        if not self.baseline_ear:
            return 0.70
        if self.baseline_ear >= 0.30:
            return 0.65
        elif self.baseline_ear >= 0.25:
            return 0.68
        elif self.baseline_ear >= 0.20:
            return 0.70
        else:
            return 0.72
    
    def _load_calibration(self):
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
                        if (datetime.now() - calibrated_at).days > 30:
                            return
                    
                    self.baseline_ear = data.get('baseline_ear')
                    
                    if self.baseline_ear and 0.15 <= self.baseline_ear <= 0.45:
                        self.is_calibrated = True
            except:
                pass
    
    def save_calibration(self):
        if not self.driver_id or not self.is_calibrated:
            return
        
        try:
            os.makedirs("calibrations", exist_ok=True)
            data = {
                'driver_id': self.driver_id,
                'baseline_ear': float(self.baseline_ear),
                'calibrated_at': datetime.now().isoformat()
            }
            with open(f"calibrations/driver_{self.driver_id}.json", 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass
    
    def calibrate(self, frame):
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
                
                if 0.15 < avg_ear < 0.5:
                    self.calibration_samples.append(avg_ear)
                
                if len(self.calibration_samples) >= 30:
                    self.baseline_ear = np.median(self.calibration_samples)
                    
                    if 0.15 <= self.baseline_ear <= 0.45:
                        self.is_calibrated = True
                        threshold_factor = self.get_adaptive_threshold_factor()
                        threshold = self.baseline_ear * threshold_factor
                        print(f"校準完成")
                        print(f"  基準 EAR: {self.baseline_ear:.3f}")
                        print(f"  閾值因子: {threshold_factor:.2f}")
                        print(f"  閉眼閾值: {threshold:.3f}")
                        self.save_calibration()
                        return True
                    else:
                        self.calibration_samples.clear()
                        return False
            
            progress = len(self.calibration_samples)
            if progress % 10 == 0 and progress > 0:
                print(f"校準 {progress}/30")
            
        except:
            return False
        
        return False
    
    def _calculate_ear_with_coords(self, landmarks, eye_indices, frame_width, frame_height):
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
            
        except:
            return 0.0, None
    
    def _draw_landmarks(self, frame, left_coords, right_coords, color):
        if frame is None:
            return frame
        
        frame_copy = frame.copy()
        
        for coords in [left_coords, right_coords]:
            if coords:
                for coord in coords:
                    if coord:
                        cv2.circle(frame_copy, coord, 2, color, -1)
        
        return frame_copy
    
    def _draw_info(self, frame, ear, threshold, closed_frames, no_face_frames, event_text=None):
        if frame is None:
            return frame
        
        h, w = frame.shape[:2]
        frame_copy = frame.copy()
        
        color = self.COLOR_GREEN if closed_frames == 0 else self.COLOR_RED
        cv2.putText(frame_copy, f"EAR: {ear:.3f} (threshold: {threshold:.3f})", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.putText(frame_copy, f"Closed: {closed_frames}f ({closed_frames/30:.1f}s)", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        if no_face_frames > 0:
            cv2.putText(frame_copy, f"No Face: {no_face_frames}f ({no_face_frames/30:.1f}s)", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
        
        if event_text:
            cv2.rectangle(frame_copy, (0, h-80), (w, h), self.COLOR_RED, -1)
            cv2.putText(frame_copy, event_text, (10, h-40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        
        return frame_copy
    
    def detect(self, frame, draw_landmarks=False):
        output_frame = frame
        
        try:
            if frame is None or frame.size == 0:
                return {'status': 'error', 'message': '無效幀'}, output_frame
            
            if not self.is_calibrated:
                is_done = self.calibrate(frame)
                if not is_done:
                    return {
                        'status': 'calibrating',
                        'progress': len(self.calibration_samples),
                        'required': 30
                    }, output_frame
            
            h, w = frame.shape[:2]
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            # A04: 無臉部偵測
            if not results.multi_face_landmarks:
                self.consecutive_no_face_frames += 1
                
                if draw_landmarks:
                    output_frame = self._draw_info(frame, 0, 0, 0, self.consecutive_no_face_frames, None)
                
                if self.consecutive_no_face_frames == 150:
                    print(f">>> A04 觸發 (無臉部 5.0秒)")
                    return {
                        'status': 'detected',
                        'drowsiness_level': 2,
                        'event_type': 'no_face_detected',
                        'metrics': {
                            'no_face_duration': 5.0,
                            'no_face_frames': self.consecutive_no_face_frames
                        },
                        'confidence': 0.95
                    }, output_frame
                
                return {'status': 'no_face', 'message': '未偵測到臉部'}, output_frame
            
            self.consecutive_no_face_frames = 0
            
            landmarks = results.multi_face_landmarks[0].landmark
            
            left_ear, left_coords = self._calculate_ear_with_coords(landmarks, self.LEFT_EYE_INDICES, w, h)
            right_ear, right_coords = self._calculate_ear_with_coords(landmarks, self.RIGHT_EYE_INDICES, w, h)
            avg_ear = (left_ear + right_ear) / 2.0
            
            if avg_ear <= 0:
                return {'status': 'error', 'message': 'EAR 失敗'}, output_frame
            
            self.ear_history.append(avg_ear)
            
            threshold_factor = self.get_adaptive_threshold_factor()
            ear_threshold = self.baseline_ear * threshold_factor
            
            # 只用絕對閾值（移除相對判斷）
            is_eyes_closed = avg_ear < ear_threshold
            
            if is_eyes_closed:
                self.consecutive_closed_frames += 1
            else:
                if 2 < self.consecutive_closed_frames < 10:
                    self.total_blinks += 1
                self.consecutive_closed_frames = 0
            
            # 事件判斷
            drowsiness_level = 0
            event_type = None
            
            if self.consecutive_closed_frames == 150:
                drowsiness_level = 2
                event_type = 'drowsy_severe'
                print(f">>> A02 觸發 (閉眼 5.0秒, EAR={avg_ear:.3f}, 閾值={ear_threshold:.3f})")
            
            elif self.consecutive_closed_frames == 30:
                drowsiness_level = 3
                event_type = 'drowsy_moderate'
                print(f">>> A01 觸發 (閉眼 3.0秒, EAR={avg_ear:.3f}, 閾值={ear_threshold:.3f})")
            
            # 視覺化
            if draw_landmarks:
                color = self.COLOR_GREEN if self.consecutive_closed_frames == 0 else self.COLOR_RED
                output_frame = self._draw_landmarks(frame, left_coords, right_coords, color)
                
                event_text = None
                if event_type:
                    event_map = {
                        'drowsy_severe': 'A01 - 重度疲勞',
                        'drowsy_moderate': 'A02 - 中度疲勞',
                        'no_face_detected': 'A04 - 無臉部'
                    }
                    event_text = event_map.get(event_type)
                
                output_frame = self._draw_info(output_frame, avg_ear, ear_threshold,
                                              self.consecutive_closed_frames,
                                              self.consecutive_no_face_frames,
                                              event_text)
            
            result = {
                'status': 'detected',
                'drowsiness_level': drowsiness_level,
                'event_type': event_type,
                'metrics': {
                    'ear': round(avg_ear, 3),
                    'baseline_ear': round(self.baseline_ear, 3),
                    'ear_threshold': round(ear_threshold, 3),
                    'closed_frames': self.consecutive_closed_frames,
                    'total_blinks': self.total_blinks
                },
                'confidence': 0.85 if event_type else 0.0
            }
            
            return result, output_frame
            
        except Exception as e:
            print(f"偵測錯誤: {e}")
            import traceback
            traceback.print_exc()
            return {'status': 'error', 'message': str(e)}, output_frame


_drowsiness_detector = None

def get_drowsiness_detector(driver_id=None):
    global _drowsiness_detector
    if _drowsiness_detector is None or (driver_id and _drowsiness_detector.driver_id != driver_id):
        _drowsiness_detector = PersonalizedDrowsinessDetector(driver_id)
    return _drowsiness_detector