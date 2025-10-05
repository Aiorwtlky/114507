# detectors/inside/phone_detector.py
"""
手機使用偵測器 (A03)
使用 MediaPipe Hands 偵測手部靠近臉部
"""

import cv2
import numpy as np
import mediapipe as mp
from datetime import datetime
from collections import deque
from detectors.base_detector import BaseDetector

class PhoneDetector(BaseDetector):
    """手機使用偵測器"""
    
    def __init__(self):
        super().__init__('PhoneDetector', 'inside')
        
        # MediaPipe Hands + Face Mesh
        self.mp_hands = None
        self.hands = None
        self.mp_face_mesh = None
        self.face_mesh = None
        
        # 狀態追蹤
        self.hand_near_face_frames = 0
        self.fps = 30
        self.DETECTION_THRESHOLD = 3 * self.fps  # 3秒
        
        # 距離閾值（手與臉的距離）
        self.DISTANCE_THRESHOLD = 0.15  # 相對於影像寬度
        
        # 事件去重
        self.last_event_time = None
        self.event_cooldown = 5.0  # 秒
    
    def initialize(self):
        """初始化 MediaPipe"""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        print(f"[{self.detector_name}] MediaPipe Hands + Face Mesh 已初始化")
    
    def _get_face_center(self, face_landmarks):
        """取得臉部中心點"""
        # 使用鼻尖作為參考點（索引 1）
        nose_tip = face_landmarks.landmark[1]
        return (nose_tip.x, nose_tip.y)
    
    def _get_hand_position(self, hand_landmarks):
        """取得手部中心位置"""
        # 使用手腕作為參考點（索引 0）
        wrist = hand_landmarks.landmark[0]
        return (wrist.x, wrist.y)
    
    def _calculate_distance(self, point1, point2):
        """計算兩點距離"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def detect(self, frame, timestamp=None, **kwargs):
        """執行手機偵測"""
        if timestamp is None:
            timestamp = datetime.now()
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 偵測臉部
        face_results = self.face_mesh.process(rgb_frame)
        
        # 偵測手部
        hand_results = self.hands.process(rgb_frame)
        
        # 需要同時偵測到臉和手
        if not face_results.multi_face_landmarks or not hand_results.multi_hand_landmarks:
            self.hand_near_face_frames = 0
            return {
                'event_detected': False,
                'rule_id': None,
                'confidence': 0.0,
                'detection_data': {'status': 'no_detection'},
                'timestamp': timestamp
            }
        
        # 取得臉部中心
        face_center = self._get_face_center(face_results.multi_face_landmarks[0])
        
        # 檢查每隻手是否靠近臉部
        hand_near_face = False
        min_distance = float('inf')
        
        for hand_landmarks in hand_results.multi_hand_landmarks:
            hand_pos = self._get_hand_position(hand_landmarks)
            distance = self._calculate_distance(face_center, hand_pos)
            
            if distance < min_distance:
                min_distance = distance
            
            if distance < self.DISTANCE_THRESHOLD:
                hand_near_face = True
                break
        
        # 更新計數器
        if hand_near_face:
            self.hand_near_face_frames += 1
        else:
            self.hand_near_face_frames = 0
        
        # 事件判斷
        event_detected = False
        confidence = 0.0
        
        if self.hand_near_face_frames >= self.DETECTION_THRESHOLD:
            event_detected = True
            confidence = 0.75  # 相對較低，因為可能是摸臉等動作
            print(f"[{self.detector_name}] A03 使用手機觸發 ({self.hand_near_face_frames/self.fps:.1f}秒)")
        
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
            'rule_id': 'A03' if event_detected else None,
            'confidence': confidence,
            'detection_data': {
                'hand_detected': True,
                'face_detected': True,
                'min_distance': round(min_distance, 3),
                'threshold': self.DISTANCE_THRESHOLD,
                'near_face_frames': self.hand_near_face_frames,
                'near_face_seconds': round(self.hand_near_face_frames / self.fps, 2)
            },
            'timestamp': timestamp
        }