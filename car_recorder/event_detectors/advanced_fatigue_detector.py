# event_detectors/advanced_fatigue_detector.py
import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import time
from scipy.spatial import distance

class FatigueDetector:
    def __init__(self, fps=30):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.LEFT_EYE_POINTS = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE_POINTS = [33, 160, 158, 133, 153, 144]

        self.FPS = fps
        self.calibration_samples = deque(maxlen=fps * 10)
        self.calibration_complete = False
        self.ear_baseline = None

        self.EAR_CLOSED_THRESHOLD_RATIO = 0.70
        self.CLOSED_TIME_A02, self.CLOSED_TIME_A01 = 3.0, 5.0
        self.ABSOLUTE_MIN_CLOSED_THRESHOLD = 0.10

        self.perclos_window = deque(maxlen=fps * 60)
        self.PERCLOS_THRESHOLD = 0.20

        self.eye_closed_start_time = None
        self.last_perclos_event_time = 0

        # <<< 新增：睜眼狀態的寬容期計數器 >>>
        self.eye_open_grace_counter = 0

    def calculate_ear(self, eye_landmarks, frame_shape):
        h, w = frame_shape
        coords = np.array([(lm.x * w, lm.y * h) for lm in eye_landmarks])
        p2_p6, p3_p5 = distance.euclidean(coords[1], coords[5]), distance.euclidean(coords[2], coords[4])
        p1_p4 = distance.euclidean(coords[0], coords[3])
        return (p2_p6 + p3_p5) / (2.0 * p1_p4) if p1_p4 != 0 else 0.25
    
    def auto_calibrate(self, ear):
        self.calibration_samples.append(ear)
        if len(self.calibration_samples) == self.calibration_samples.maxlen:
            valid_samples = [s for s in self.calibration_samples if s > 0.1]
            if not valid_samples:
                self.calibration_samples.clear(); return

            self.ear_baseline = np.median(valid_samples)
            self.calibration_complete = True
            
            if self.ear_baseline < 0.23:
                self.EAR_CLOSED_THRESHOLD_RATIO = 0.65
                print(f"[INFO] 偵測到可能的小眼型用戶，已自動調整偵測靈敏度。")

            self.last_perclos_event_time = time.time()
            print(f"[INFO] 疲勞偵測器校準完成: EAR基準線 = {self.ear_baseline:.3f}, 閉眼比例 = {self.EAR_CLOSED_THRESHOLD_RATIO:.2f}")

    def calculate_perclos(self):
        if not self.perclos_window: return 0.0
        return sum(self.perclos_window) / len(self.perclos_window)

    def analyze_frame(self, frame, head_pose_data):
        events, h, w, _ = [], *frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0].landmark
            left_eye_lms, right_eye_lms = [face_landmarks[i] for i in self.LEFT_EYE_POINTS], [face_landmarks[i] for i in self.RIGHT_EYE_POINTS]
            avg_ear = (self.calculate_ear(left_eye_lms, (h, w)) + self.calculate_ear(right_eye_lms, (h, w))) / 2.0

            if not self.calibration_complete:
                self.auto_calibrate(avg_ear)
            else:
                calculated_thresh = self.ear_baseline * self.EAR_CLOSED_THRESHOLD_RATIO
                closed_threshold = max(calculated_thresh, self.ABSOLUTE_MIN_CLOSED_THRESHOLD)
                is_closed = 1 if avg_ear < closed_threshold else 0
                self.perclos_window.append(is_closed)
                
                # <<< 修改重點：引入寬容期來穩定計時器 >>>
                if is_closed:
                    self.eye_open_grace_counter = 0 # 只要是閉著的，就重置寬容計數
                    if self.eye_closed_start_time is None: self.eye_closed_start_time = time.time()
                    
                    closed_duration = time.time() - self.eye_closed_start_time
                    print(f"\rDEBUG: Eye Closed! EAR={avg_ear:.3f} vs Thresh={closed_threshold:.3f} | Duration: {closed_duration:.2f}s", end="")

                    if closed_duration >= self.CLOSED_TIME_A01: events.append("A01: 重度疲勞 (閉眼超過5秒)")
                    elif closed_duration >= self.CLOSED_TIME_A02: events.append("A02: 中度疲勞 (閉眼超過3秒)")
                else:
                    self.eye_open_grace_counter += 1 # 開始計算"睜眼"的影格數
                    # 只有當連續 3 幀都偵測為睜眼時，才真正重置計時器
                    if self.eye_open_grace_counter > 3:
                        if self.eye_closed_start_time is not None: print()
                        self.eye_closed_start_time = None
                    # 如果只是短暫的抖動，計時器會繼續保留，等待下一次閉眼訊號
                    elif self.eye_closed_start_time is not None:
                        # 即使睜開一兩幀，也印出計時器狀態，方便觀察
                        closed_duration = time.time() - self.eye_closed_start_time
                        print(f"\rDEBUG: Eye Open (Grace)! EAR={avg_ear:.3f} vs Thresh={closed_threshold:.3f} | Duration: {closed_duration:.2f}s", end="")

                if not events:
                    current_perclos = self.calculate_perclos()
                    if current_perclos > self.PERCLOS_THRESHOLD and (time.time() - self.last_perclos_event_time > 30):
                        events.append(f"A02: 中度疲勞 (眼部閉合時間過長)")
                        self.last_perclos_event_time = time.time()
                
                self.visualize(frame, avg_ear, closed_threshold)
        
        return list(set(events)), frame

    def visualize(self, frame, ear, closed_threshold):
        if self.calibration_complete:
            perclos_val = self.calculate_perclos()
            cv2.putText(frame, f"EAR: {ear:.2f} (Thresh: {closed_threshold:.2f})", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(frame, f"PERCLOS: {perclos_val:.2%}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        else:
            progress = len(self.calibration_samples) / self.calibration_samples.maxlen
            cv2.putText(frame, f"Calibrating... {int(progress * 100)}%", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)