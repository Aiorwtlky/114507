# detectors/inside/attention_detector.py
"""
注意力分散偵測器 (A04)
偵測臉部離開畫面
"""

import cv2
import mediapipe as mp
from datetime import datetime
from detectors.base_detector import BaseDetector

class AttentionDetector(BaseDetector):
    """注意力分散偵測器"""
    
    def __init__(self):
        super().__init__('AttentionDetector', 'inside')
        
        # MediaPipe Face Mesh
        self.mp_face_mesh = None
        self.face_mesh = None
        
        # 狀態追蹤
        self.no_face_frames = 0
        self.fps = 30
        self.DETECTION_THRESHOLD = 5 * self.fps  # 5秒
        
        # 事件去重
        self.last_event_time = None
        self.event_cooldown = 5.0  # 秒
    
    def initialize(self):
        """初始化 MediaPipe"""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        print(f"[{self.detector_name}] MediaPipe Face Mesh 已初始化")
    
    def detect(self, frame, timestamp=None, **kwargs):
        """執行注意力偵測"""
        if timestamp is None:
            timestamp = datetime.now()
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # MediaPipe 偵測
        results = self.face_mesh.process(rgb_frame)
        
        # 判斷是否偵測到臉部
        face_detected = results.multi_face_landmarks is not None
        
        if not face_detected:
            self.no_face_frames += 1
        else:
            self.no_face_frames = 0
        
        # 事件判斷
        event_detected = False
        confidence = 0.0
        
        if self.no_face_frames >= self.DETECTION_THRESHOLD:
            event_detected = True
            confidence = 0.95
            print(f"[{self.detector_name}] A04 注意力分散觸發 ({self.no_face_frames/self.fps:.1f}秒)")
        
        # 事件去重
        if event_detected:
            if self.last_event_time:
                time_diff = (timestamp - self.last_event_time).total_seconds()
                if time_diff < self.event_cooldown:
                    event_detected = False
            
            if event_detected:
                self.last_event_time = timestamp
        
        return {
            'event_detected': event_detected,
            'rule_id': 'A04' if event_detected else None,
            'confidence': confidence,
            'detection_data': {
                'face_detected': face_detected,
                'no_face_frames': self.no_face_frames,
                'no_face_seconds': round(self.no_face_frames / self.fps, 2)
            },
            'timestamp': timestamp
        }