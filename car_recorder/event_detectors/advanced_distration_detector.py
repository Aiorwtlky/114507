# event_detectors/advanced_distraction_detector.py
"""
進階分心行為偵測器
參考專案：
- https://github.com/SusmithKrishnan/distraction-detection
- https://github.com/roboflow/supervision
- https://github.com/CMU-Perceptual-Computing-Lab/openpose
"""

import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import time
from scipy.spatial import distance
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM

class DistractionDetector:
    def __init__(self, fps=30):
        # MediaPipe 初始化
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.FPS = fps
        
        # === 行為分析器 ===
        self.phone_detector = PhoneUsageDetector(fps)
        self.attention_analyzer = AttentionAnalyzer(fps)
        self.gesture_recognizer = GestureRecognizer()
        self.posture_analyzer = PostureAnalyzer()
        
        # === 異常行為偵測 (使用 One-Class SVM) ===
        self.anomaly_detector = AnomalyDetector()
        
        # === 分心行為模式 ===
        self.distraction_patterns = {
            'phone_call': {'score': 0, 'threshold': 0.7},
            'texting': {'score': 0, 'threshold': 0.8},
            'looking_away': {'score': 0, 'threshold': 0.6}
        }
        
        # === 時間閾值 ===
        self.PHONE_USE_TIME = 2.0      # 使用手機 (A03)
        self.FACE_AWAY_TIME = 2.0      # 臉部離開 (A04)
        self.LOOKING_AWAY_TIME = 3.0   # 視線偏離
        
        # === 歷史記錄 ===
        self.face_history = deque(maxlen=fps * 5)
        self.hand_history = deque(maxlen=fps * 5)
        self.pose_history = deque(maxlen=fps * 5)
        self.attention_history = deque(maxlen=fps * 10)
        
        # === 計時器 ===
        self.phone_use_start = None
        self.face_away_start = None
        self.looking_away_start = None
        
        # === 統計資料 ===
        self.stats = {
            'phone_uses': 0,
            'face_aways': 0,
            'looking_aways': 0,
            'total_distractions': 0,
            'attention_score': 100
        }
        
        # === 事件管理 ===
        self.event_cooldown = {}
        self.distraction_level = 0  # 0-100
        
        # 校準狀態
        self.calibrated = False
        self.calibration_data = []

    def calibrate_normal_behavior(self, features):
        """校準正常駕駛行為"""
        self.calibration_data.append(features)
        
        if len(self.calibration_data) > self.FPS * 5:  # 5秒校準
            # 訓練異常偵測模型
            self.anomaly_detector.train(self.calibration_data)
            self.calibrated = True
            print("分心偵測器校準完成")

    def extract_features(self, face_results, hand_results, pose_results, frame_shape):
        """提取多模態特徵向量"""
        features = []
        
        # 臉部特徵
        if face_results.multi_face_landmarks:
            face_lms = face_results.multi_face_landmarks[0].landmark
            # 提取關鍵點位置
            face_features = []
            for lm in face_lms[:10]:  # 使用前10個關鍵點
                face_features.extend([lm.x, lm.y])
            features.extend(face_features)
        
        # 手部特徵
        if hand_results.multi_hand_landmarks:
            for hand_lms in hand_results.multi_hand_landmarks:
                hand_features = []
                for lm in hand_lms.landmark[:5]:  # 使用前5個關鍵點
                    hand_features.extend([lm.x, lm.y])
                features.extend(hand_features)
        
        # 姿勢特徵
        if pose_results.pose_landmarks:
            pose_lms = pose_results.pose_landmarks.landmark
            pose_features = []
            for lm in pose_lms[11:13]:  # 肩膀點
                pose_features.extend([lm.x, lm.y])
            features.extend(pose_features)
        
        return features if features else None

    def estimate_gaze(self, face_landmarks):
        """估算視線方向 (簡化版本)"""
        landmarks = face_landmarks.landmark
        
        left_eye_center = np.mean([landmarks[i] for i in [33, 133]], axis=0)
        right_eye_center = np.mean([landmarks[i] for i in [362, 263]], axis=0)
        
        eye_center = (left_eye_center + right_eye_center) / 2
        nose = landmarks[1]
        
        gaze_vector = nose - eye_center
        gaze_angle = np.arctan2(gaze_vector.y, gaze_vector.x) * 180 / np.pi
        
        return gaze_angle

    def is_looking_at_road(self, gaze_direction):
        """判斷是否看向前方道路"""
        # 假設正常視線角度在 -30 到 30 度之間
        return -30 < gaze_direction < 30

    def is_dangerous_reach(self, hand_landmarks, pose_results):
        """檢測危險伸手動作"""
        if not pose_results.pose_landmarks:
            return False
        
        wrist = hand_landmarks.landmark[0]
        shoulder = pose_results.pose_landmarks.landmark[11 if wrist.x < 0.5 else 12]
        
        dist = distance.euclidean([wrist.x, wrist.y], [shoulder.x, shoulder.y])
        
        return dist > 0.4  # 手伸太遠

    def calculate_distraction_level(self):
        """計算整體分心程度"""
        level = 0
        weights = {
            'phone_call': 40,
            'texting': 30,
            'looking_away': 30
        }
        
        # 計算加權分數
        for pattern, config in self.distraction_patterns.items():
            if pattern in weights:
                level += config['score'] * weights[pattern]
        
        # 考慮注意力分數
        if self.stats['attention_score'] < 50:
            level += (100 - self.stats['attention_score']) * 0.5
        
        return min(100, level)

    def analyze_frame(self, frame, frame_count):
        display_frame = frame.copy()
        events = []
        h, w = frame.shape[:2]
        current_time = time.time()
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # === 多模態偵測 ===
        face_results = self.face_mesh.process(frame_rgb)
        hand_results = self.hands.process(frame_rgb)
        pose_results = self.pose.process(frame_rgb)
        
        # 特徵提取
        features = self.extract_features(face_results, hand_results, pose_results, frame.shape)
        
        # 校準正常行為
        if not self.calibrated and features:
            self.calibrate_normal_behavior(features)
        
        # === 臉部分析 ===
        if face_results.multi_face_landmarks:
            face_landmarks = face_results.multi_face_landmarks[0]
            
            # 重置臉部離開計時
            self.face_away_start = None
            
            # 注意力分析
            attention_score = self.attention_analyzer.analyze(face_landmarks, frame.shape)
            self.attention_history.append(attention_score)
            
            # 視線追蹤
            gaze_direction = self.estimate_gaze(face_landmarks)
            
            # 檢查是否在看路
            if not self.is_looking_at_road(gaze_direction):
                if self.looking_away_start is None:
                    self.looking_away_start = current_time
                elif current_time - self.looking_away_start > self.LOOKING_AWAY_TIME:
                    events.append("A04: 視線長時間偏離道路")
                    self.stats['looking_aways'] += 1
                    self.looking_away_start = None
            else:
                self.looking_away_start = None
            
            # === 手部分析 ===
            if hand_results.multi_hand_landmarks:
                for hand_idx, hand_landmarks in enumerate(hand_results.multi_hand_landmarks):
                    # 手勢識別
                    gesture = self.gesture_recognizer.recognize(hand_landmarks)
                    
                    # 手機使用偵測 (A03)
                    phone_score = self.phone_detector.detect(
                        hand_landmarks, face_landmarks, gesture
                    )
                    
                    self.distraction_patterns['phone_call']['score'] = phone_score
                    
                    # 檢查是否在使用手機
                    if phone_score > 0.7:
                        if self.phone_use_start is None:
                            self.phone_use_start = current_time
                        elif current_time - self.phone_use_start > self.PHONE_USE_TIME:
                            events.append(f"A03: 偵測到使用手機 (信心度: {phone_score:.0%})")
                            self.stats['phone_uses'] += 1
                            self.phone_use_start = None
                    else:
                        self.phone_use_start = None
                    
                    # 危險伸手動作偵測 (整合到 A04 分心)
                    if self.is_dangerous_reach(hand_landmarks, pose_results):
                        events.append("A04: 危險的伸手動作")
                        self.stats['face_aways'] += 1  # 借用統計
                    
                    # 繪製手部
                    self.mp_drawing.draw_landmarks(
                        display_frame, hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS
                    )
            
            # === 姿勢分析 ===
            if pose_results.pose_landmarks:
                posture_score = self.posture_analyzer.analyze(pose_results.pose_landmarks)
                
                if posture_score < 0.5:
                    events.append("A04: 不正確的駕駛姿勢")
            
            # === 異常行為偵測 ===
            if self.calibrated and features is not None:
                is_anomaly = self.anomaly_detector.detect(features)
                if is_anomaly:
                    events.append("A04: 偵測到異常駕駛行為")
        
        else:
            # 臉部未偵測到 (A04)
            if self.face_away_start is None:
                self.face_away_start = current_time
            
            away_duration = current_time - self.face_away_start
            
            if away_duration > self.FACE_AWAY_TIME:
                events.append(f"A04: 臉部離開偵測區域 ({away_duration:.1f}秒)")
                self.stats['face_aways'] += 1
        
        # === 計算整體分心程度 ===
        self.distraction_level = self.calculate_distraction_level()
        
        # 根據分心程度生成警告 (限 A03/A04)
        if self.distraction_level > 70:
            events.append(f"A04: 高度分心狀態 (分心度: {self.distraction_level:.0f}%)")
        elif self.distraction_level > 50:
            events.append(f"A04: 中度分心 (分心度: {self.distraction_level:.0f}%)")
        
        # === 視覺化 ===
        self.visualize_results(display_frame, features)
        
        # 更新統計
        self.stats['total_distractions'] = sum([
            self.stats['phone_uses'],
            self.stats['face_aways'],
            self.stats['looking_aways']
        ])
        
        if self.attention_history:
            self.stats['attention_score'] = np.mean(list(self.attention_history)[-30:])
        
        # 返回最重要的事件 (只限 A03/A04)
        event = events[0] if events else None
        return event, display_frame

    def visualize_results(self, frame, features):
        """視覺化偵測結果"""
        h, w = frame.shape[:2]
        
        # === 資訊面板 ===
        panel_height = 200
        cv2.rectangle(frame, (5, 5), (400, panel_height), (0, 0, 0), -1)
        cv2.rectangle(frame, (5, 5), (400, panel_height), (255, 255, 255), 1)
        
        y = 25
        
        # 標題
        cv2.putText(frame, "DISTRACTION MONITOR", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        y += 30
        
        # 分心程度
        color = (0, 255, 0) if self.distraction_level < 30 else \
                (0, 165, 255) if self.distraction_level < 60 else (0, 0, 255)
        cv2.putText(frame, f"Distraction Level: {self.distraction_level:.0f}%", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        y += 25
        
        # 注意力分數
        attention_color = (0, 255, 0) if self.stats['attention_score'] > 70 else \
                         (0, 165, 255) if self.stats['attention_score'] > 40 else (0, 0, 255)
        cv2.putText(frame, f"Attention: {self.stats['attention_score']:.0f}%", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, attention_color, 2)
        y += 25
        
        # 分心行為指標
        cv2.putText(frame, "Behaviors:", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y += 20
        
        for pattern, config in self.distraction_patterns.items():
            if config['score'] > 0.3:
                indicator_color = (0, 255, 0) if config['score'] < config['threshold'] else (0, 0, 255)
                cv2.putText(frame, f"  {pattern}: {config['score']:.0%}", (10, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, indicator_color, 1)
                y += 18
        
        # === 分心程度條 ===
        bar_x = w - 200
        bar_y = 20
        bar_width = 180
        bar_height = 25
        
        cv2.rectangle(frame, (bar_x-5, bar_y-5),
                     (bar_x + bar_width + 5, bar_y + bar_height + 5),
                     (0, 0, 0), -1)
        
        cv2.rectangle(frame, (bar_x, bar_y),
                     (bar_x + bar_width, bar_y + bar_height),
                     (100, 100, 100), -1)
        
        fill_width = int(bar_width * (self.distraction_level / 100))
        cv2.rectangle(frame, (bar_x, bar_y),
                     (bar_x + fill_width, bar_y + bar_height),
                     color, -1)
        
        cv2.putText(frame, "DISTRACTION", (bar_x + 50, bar_y - 8),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # === 統計資訊 ===
        stats_y = h - 30
        stats_text = f"Phone: {self.stats['phone_uses']} | " \
                    f"Look Away: {self.stats['looking_aways']} | " \
                    f"Face Away: {self.stats['face_aways']}"
        
        cv2.putText(frame, stats_text, (10, stats_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


class PhoneUsageDetector:
    """手機使用偵測器"""
    def __init__(self, fps):
        self.fps = fps
        self.phone_pose_history = deque(maxlen=fps)
        
    def detect(self, hand_landmarks, face_landmarks, gesture):
        """偵測手機使用行為"""
        score = 0
        
        # 手的位置
        wrist = hand_landmarks.landmark[0]
        
        # 臉部參考點
        nose = face_landmarks.landmark[1]
        left_ear = face_landmarks.landmark[234]
        right_ear = face_landmarks.landmark[454]
        
        # 特徵1: 手在耳朵附近（打電話）
        dist_to_left_ear = distance.euclidean(
            [wrist.x, wrist.y], [left_ear.x, left_ear.y]
        )
        dist_to_right_ear = distance.euclidean(
            [wrist.x, wrist.y], [right_ear.x, right_ear.y]
        )
        
        if min(dist_to_left_ear, dist_to_right_ear) < 0.15:
            score += 0.4
        
        # 特徵2: 手在臉前方（看手機）
        if wrist.y > nose.y and abs(wrist.x - nose.x) < 0.2:
            score += 0.3
        
        # 特徵3: 特定手勢（握持姿勢）
        if gesture in ['holding', 'pinch']:
            score += 0.2
        
        # 特徵4: 手的穩定性（使用手機時手會相對穩定）
        self.phone_pose_history.append([wrist.x, wrist.y])
        if len(self.phone_pose_history) > 10:
            positions = np.array(list(self.phone_pose_history)[-10:])
            stability = 1 - np.std(positions)
            if stability > 0.8:
                score += 0.1
        
        return min(1.0, score)


class AttentionAnalyzer:
    """注意力分析器"""
    def __init__(self, fps):
        self.fps = fps
        self.attention_history = deque(maxlen=fps * 10)
        
    def analyze(self, face_landmarks, frame_shape):
        """分析駕駛注意力"""
        h, w = frame_shape[:2]
        landmarks = face_landmarks.landmark
        
        # 計算頭部朝向
        nose = landmarks[1]
        left_eye = landmarks[33]
        right_eye = landmarks[133]
        
        # 頭部中心
        head_center_x = (left_eye.x + right_eye.x) / 2
        head_center_y = (left_eye.y + right_eye.y) / 2
        
        # 計算偏移
        x_offset = abs(nose.x - 0.5)  # 偏離畫面中心
        y_offset = abs(nose.y - 0.5)
        
        # 注意力分數（0-100）
        attention = 100 * (1 - (x_offset + y_offset))
        attention = max(0, min(100, attention))
        
        self.attention_history.append(attention)
        
        # 返回平滑後的注意力分數
        if len(self.attention_history) > 5:
            return np.mean(list(self.attention_history)[-5:])
        
        return attention


class GestureRecognizer:
    """手勢識別器"""
    def recognize(self, hand_landmarks):
        """識別手勢"""
        landmarks = hand_landmarks.landmark
        
        # 簡化的手勢識別
        # 計算手指彎曲程度
        fingers_up = self.count_fingers_up(landmarks)
        
        # 識別常見手勢
        if fingers_up == 0:
            return 'fist'
        elif fingers_up == 1:
            return 'pointing'
        elif fingers_up == 2:
            return 'peace'
        elif fingers_up == 5:
            return 'open'
        else:
            # 檢查握持姿勢
            if self.is_holding_pose(landmarks):
                return 'holding'
            
        return 'unknown'
    
    def count_fingers_up(self, landmarks):
        """計算豎起的手指數"""
        count = 0
        
        # 簡化判斷：比較指尖和指根的Y座標
        finger_tips = [4, 8, 12, 16, 20]  # 指尖索引
        finger_bases = [2, 5, 9, 13, 17]  # 指根索引
        
        for tip, base in zip(finger_tips, finger_bases):
            if landmarks[tip].y < landmarks[base].y:
                count += 1
        
        return count
    
    def is_holding_pose(self, landmarks):
        """檢測握持姿勢"""
        # 檢查手指是否彎曲（模擬握持）
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        
        # 計算手指間距離
        dist = distance.euclidean(
            [thumb_tip.x, thumb_tip.y],
            [index_tip.x, index_tip.y]
        )
        
        return dist < 0.1


class PostureAnalyzer:
    """姿勢分析器"""
    def analyze(self, pose_landmarks):
        """分析駕駛姿勢"""
        landmarks = pose_landmarks.landmark
        
        # 肩膀位置
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        
        # 檢查肩膀是否平衡
        shoulder_diff = abs(left_shoulder.y - right_shoulder.y)
        
        # 檢查身體是否前傾
        nose = landmarks[0]
        body_lean = nose.y - (left_shoulder.y + right_shoulder.y) / 2
        
        # 計算姿勢分數
        score = 1.0
        
        if shoulder_diff > 0.05:
            score -= 0.3  # 肩膀不平
        
        if body_lean < -0.1:
            score -= 0.3  # 過度前傾
        
        return max(0, score)


class AnomalyDetector:
    """異常行為偵測器"""
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def train(self, normal_data):
        """訓練異常偵測模型"""
        if len(normal_data) < 50:
            return
        
        # 正規化數據
        X = self.scaler.fit_transform(normal_data)
        
        # 訓練 One-Class SVM
        self.model = OneClassSVM(gamma='auto', nu=0.1)
        self.model.fit(X)
        
        self.is_trained = True
        
    def detect(self, features):
        """偵測異常行為"""
        if not self.is_trained or self.model is None:
            return False
        
        # 正規化特徵
        X = self.scaler.transform([features])
        
        # 預測（-1 表示異常）
        prediction = self.model.predict(X)
        
        return prediction[0] == -1