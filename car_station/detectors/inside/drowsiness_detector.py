# detectors/inside/drowsiness_detector.py
"""
疲勞偵測器 (A01, A02)
使用 MediaPipe Face Mesh 計算 EAR (Eye Aspect Ratio)
"""

import cv2
import numpy as np
import mediapipe as mp
from scipy.spatial import distance
from datetime import datetime
from collections import deque
from detectors.base_detector import BaseDetector

class DrowsinessDetector(BaseDetector):
    """疲勞駕駛偵測器"""
    
    def __init__(self):
        super().__init__('DrowsinessDetector', 'inside')
        
        # MediaPipe Face Mesh
        self.mp_face_mesh = None
        self.face_mesh = None
        
        # 眼睛特徵點索引（MediaPipe 468 點）
        self.LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
        
        # EAR 閾值
        self.EAR_THRESHOLD = 0.20  # 眼睛閉合閾值
        self.baseline_ear = 0.30   # 基準值（可通過校準調整）
        
        # 狀態追蹤
        self.ear_history = deque(maxlen=30)  # 1秒歷史
        self.consecutive_closed_frames = 0
        self.fps = 30
        
        # 事件觸發閾值（幀數）
        self.MODERATE_THRESHOLD = 3 * self.fps   # 3秒 = 90幀
        self.SEVERE_THRESHOLD = 5 * self.fps     # 5秒 = 150幀
        
        # 事件去重
        self.last_event_time = None
        self.event_cooldown = 3.0  # 秒
    
    def initialize(self):
        """初始化 MediaPipe"""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        print(f"[{self.detector_name}] MediaPipe Face Mesh 已初始化")
    
    def _calculate_ear(self, landmarks, eye_indices, frame_width, frame_height):
        """
        計算 Eye Aspect Ratio
        
        EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
        """
        try:
            coords = []
            for idx in eye_indices:
                lm = landmarks[idx]
                x = min(int(lm.x * frame_width), frame_width - 1)
                y = min(int(lm.y * frame_height), frame_height - 1)
                coords.append((x, y))
            
            # 計算距離
            vertical1 = distance.euclidean(coords[1], coords[5])
            vertical2 = distance.euclidean(coords[2], coords[4])
            horizontal = distance.euclidean(coords[0], coords[3])
            
            if horizontal < 0.001:
                return 0.0
            
            ear = (vertical1 + vertical2) / (2.0 * horizontal)
            return ear if 0 <= ear <= 1.0 else 0.0
            
        except Exception as e:
            print(f"[{self.detector_name}] EAR 計算錯誤: {e}")
            return 0.0
    
    def detect(self, frame, timestamp=None, **kwargs):
        """執行疲勞偵測"""
        if timestamp is None:
            timestamp = datetime.now()
        
        h, w = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # MediaPipe 偵測
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            # 沒有偵測到臉部
            self.consecutive_closed_frames = 0
            return {
                'event_detected': False,
                'rule_id': None,
                'confidence': 0.0,
                'detection_data': {'status': 'no_face'},
                'timestamp': timestamp
            }
        
        # 取得臉部特徵點
        landmarks = results.multi_face_landmarks[0].landmark
        
        # 計算雙眼 EAR
        left_ear = self._calculate_ear(landmarks, self.LEFT_EYE_INDICES, w, h)
        right_ear = self._calculate_ear(landmarks, self.RIGHT_EYE_INDICES, w, h)
        avg_ear = (left_ear + right_ear) / 2.0
        
        if avg_ear <= 0:
            return {
                'event_detected': False,
                'rule_id': None,
                'confidence': 0.0,
                'detection_data': {'status': 'calculation_error'},
                'timestamp': timestamp
            }
        
        # 加入歷史記錄
        self.ear_history.append(avg_ear)
        
        # 判斷眼睛是否閉合
        is_closed = avg_ear < self.EAR_THRESHOLD
        
        if is_closed:
            self.consecutive_closed_frames += 1
        else:
            self.consecutive_closed_frames = 0
        
        # 事件判斷
        rule_id = None
        event_detected = False
        confidence = 0.0
        
        # A01: 重度疲勞（5秒+）
        if self.consecutive_closed_frames >= self.SEVERE_THRESHOLD:
            rule_id = 'A01'
            event_detected = True
            confidence = 0.95
            print(f"[{self.detector_name}] A01 重度疲勞觸發 ({self.consecutive_closed_frames/self.fps:.1f}秒)")
        
        # A02: 中度疲勞（3-5秒）
        elif self.consecutive_closed_frames >= self.MODERATE_THRESHOLD:
            rule_id = 'A02'
            event_detected = True
            confidence = 0.90
            print(f"[{self.detector_name}] A02 中度疲勞觸發 ({self.consecutive_closed_frames/self.fps:.1f}秒)")
        
        # 事件去重（同類事件 3 秒內只觸發一次）
        if event_detected and rule_id:
            if self.last_event_time:
                time_diff = (timestamp - self.last_event_time).total_seconds()
                if time_diff < self.event_cooldown:
                    event_detected = False
            
            if event_detected:
                self.last_event_time = timestamp
        
        return {
            'event_detected': event_detected,
            'rule_id': rule_id,
            'confidence': confidence,
            'detection_data': {
                'ear': round(avg_ear, 3),
                'left_ear': round(left_ear, 3),
                'right_ear': round(right_ear, 3),
                'threshold': self.EAR_THRESHOLD,
                'closed_frames': self.consecutive_closed_frames,
                'closed_seconds': round(self.consecutive_closed_frames / self.fps, 2)
            },
            'timestamp': timestamp
        }