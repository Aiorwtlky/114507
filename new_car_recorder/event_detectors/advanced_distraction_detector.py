# event_detectors/advanced_distraction_detector.py
import cv2
import mediapipe as mp
import numpy as np
import time
from scipy.spatial import distance
from collections import deque

class DistractionDetector:
    def __init__(self, fps=30):
        self.DEBUG_MODE = True

        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.6, min_tracking_confidence=0.6)

        self.PHONE_USE_TIME = 2.0
        self.LOOKING_AWAY_TIME = 2.5
        self.FACE_AWAY_TIME = 3.0
        self.YAW_THRESHOLD = 35
        self.PITCH_THRESHOLD = 25
        self.HAND_FACE_PROXIMITY = 0.18

        self.phone_use_start_time = None
        self.looking_away_start_time = None
        self.face_away_start_time = None
        
        self.phone_detection_history = deque(maxlen=int(fps / 2))

    def estimate_head_pose(self, face_landmarks, frame_shape):
        h, w = frame_shape
        face_3d = np.array([
            (0.0, 0.0, 0.0), 
            (0.0, -330.0, -65.0), 
            (-225.0, 170.0, -135.0), 
            (225.0, 170.0, -135.0), 
            (-150.0, -150.0, -125.0), 
            (150.0, -150.0, -125.0)
        ], dtype=np.float64)
        
        face_2d = np.array([
            (face_landmarks[1].x * w, face_landmarks[1].y * h), 
            (face_landmarks[152].x * w, face_landmarks[152].y * h), 
            (face_landmarks[263].x * w, face_landmarks[263].y * h), 
            (face_landmarks[33].x * w, face_landmarks[33].y * h), 
            (face_landmarks[287].x * w, face_landmarks[287].y * h), 
            (face_landmarks[57].x * w, face_landmarks[57].y * h)
        ], dtype=np.float64)
        
        cam_matrix = np.array([[w, 0, w/2], [0, w, h/2], [0, 0, 1]])
        success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, np.zeros((4, 1)))
        
        if not success: 
            return None
            
        rmat, _ = cv2.Rodrigues(rot_vec)
        pitch = -np.arcsin(rmat[1, 2]) * 180 / np.pi
        yaw = np.arctan2(rmat[0, 2], rmat[2, 2]) * 180 / np.pi
        return {'pitch': pitch, 'yaw': yaw}

    def is_holding_gesture(self, hand_lms):
        tip_y = [hand_lms.landmark[i].y for i in [8, 12, 16, 20]]
        mcp_y = [hand_lms.landmark[i].y for i in [5, 9, 13, 17]]
        bent_fingers = sum(1 for tip, mcp in zip(tip_y, mcp_y) if tip > mcp)
        return bent_fingers >= 3

    def detect_phone_use(self, hand_landmarks, face_landmarks):
        left_ear = face_landmarks[234]
        right_ear = face_landmarks[454]
        mouth_center = face_landmarks[13]
        
        for hand_lms in hand_landmarks:
            score = 0
            debug_info = []
            wrist = hand_lms.landmark[0]
            
            # 靠近耳朵
            dist_to_ear = min(
                distance.euclidean([wrist.x, wrist.y], [left_ear.x, left_ear.y]), 
                distance.euclidean([wrist.x, wrist.y], [right_ear.x, right_ear.y])
            )
            if dist_to_ear < self.HAND_FACE_PROXIMITY: 
                score += 60
                debug_info.append("NearEar")

            # 靠近嘴巴
            dist_to_mouth = distance.euclidean([wrist.x, wrist.y], [mouth_center.x, mouth_center.y])
            if dist_to_mouth < self.HAND_FACE_PROXIMITY * 1.5 and wrist.y > mouth_center.y: 
                score += 30
                debug_info.append("NearMouth")
            
            # 握持姿勢
            if self.is_holding_gesture(hand_lms): 
                score += 25
                debug_info.append("Holding")
            
            # 打字區域
            if wrist.y > 0.6 and 0.2 < wrist.x < 0.8: 
                score += 25
                debug_info.append("TextingZone")

            timer_duration = (time.time() - self.phone_use_start_time) if self.phone_use_start_time else 0
            
            if self.DEBUG_MODE:
                history_ratio = sum(self.phone_detection_history) / len(self.phone_detection_history) if self.phone_detection_history else 0
                print(f"\r[PHONE DEBUG] Score: {score:3d} | Timer: {timer_duration:.2f}s | History: {history_ratio:.2f} | Cond: {'-'.join(debug_info) if debug_info else 'None'}", end="")

            if score >= 59:
                return True
        
        if self.DEBUG_MODE:
            history_ratio = sum(self.phone_detection_history) / len(self.phone_detection_history) if self.phone_detection_history else 0
            print(f"\r[PHONE DEBUG] Score:   0 | Timer: 0.00s | History: {history_ratio:.2f} | Cond: No Hand or No Match ", end="")
        
        return False

    def analyze_frame(self, frame):
        events = []
        head_pose_data = None
        h, w, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        face_results = self.face_mesh.process(frame_rgb)
        hand_results = self.hands.process(frame_rgb)

        if face_results.multi_face_landmarks:
            # 有偵測到臉，重置臉部離開計時器
            self.face_away_start_time = None
            
            face_lms = face_results.multi_face_landmarks[0].landmark
            head_pose_data = self.estimate_head_pose(face_lms, (h, w))
            
            if head_pose_data:
                yaw = head_pose_data['yaw']
                pitch = head_pose_data['pitch']
                
                # ✅ A05: 視線長時間偏離（扣5分）
                if abs(yaw) > self.YAW_THRESHOLD or abs(pitch) > self.PITCH_THRESHOLD:
                    if self.looking_away_start_time is None: 
                        self.looking_away_start_time = time.time()
                    elif time.time() - self.looking_away_start_time > self.LOOKING_AWAY_TIME: 
                        events.append("A05: 視線長時間偏離")
                else: 
                    self.looking_away_start_time = None
                
                self.visualize(frame, head_pose_data)
            
            # A03: 偵測手機使用
            phone_detected_this_frame = False
            if hand_results.multi_hand_landmarks:
                phone_detected_this_frame = self.detect_phone_use(hand_results.multi_hand_landmarks, face_lms)
            
            self.phone_detection_history.append(phone_detected_this_frame)
            
            is_stably_detected = (sum(self.phone_detection_history) / len(self.phone_detection_history)) > 0.4 if self.phone_detection_history else False
            
            if is_stably_detected:
                if self.phone_use_start_time is None: 
                    self.phone_use_start_time = time.time()
                elif time.time() - self.phone_use_start_time > self.PHONE_USE_TIME: 
                    events.append("A03: 偵測到手持通話或操作手機")
            else:
                self.phone_use_start_time = None
        
        else:
            # 沒有偵測到臉
            self.looking_away_start_time = None
            self.phone_use_start_time = None
            
            # ✅ A04: 臉部離開偵測區域（扣40分）
            if self.face_away_start_time is None: 
                self.face_away_start_time = time.time()
            elif time.time() - self.face_away_start_time > self.FACE_AWAY_TIME: 
                events.append("A04: 臉部離開偵測區域")

        return list(set(events)), frame, head_pose_data

    def visualize(self, frame, head_pose):
        yaw = head_pose.get('yaw', 0)
        pitch = head_pose.get('pitch', 0)
        
        status = "Normal"
        color = (0, 255, 0)
        
        if abs(yaw) > self.YAW_THRESHOLD or abs(pitch) > self.PITCH_THRESHOLD:
            status = "Looking Away"
            color = (0, 0, 255)
        
        cv2.putText(frame, f"Gaze: {status}", (frame.shape[1] - 180, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)