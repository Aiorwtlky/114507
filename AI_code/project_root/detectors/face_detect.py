# detectors/face_detect.py
import time
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.python.solutions.drawing_utils import _normalized_to_pixel_coordinates as denormalize_coordinates

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

COLOR_RED = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)

class VideoFrameHandler:
    def __init__(self):
        # Mediapipe FaceMesh 初始化
        self.facemesh_model = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        # 眼睛關鍵點索引（6點EAR計算用）
        self.eye_idxs = {
            "left": [362, 385, 387, 263, 373, 380],
            "right": [33, 160, 158, 133, 153, 144],
        }
        self.color = COLOR_GREEN
        self.state_tracker = {
            "start_time": time.perf_counter(),
            "drowsy_time": 0.0,
            "play_alarm": False,
            "color": COLOR_GREEN,
        }

    def distance(self, p1, p2):
        """計算兩點間歐氏距離"""
        return np.linalg.norm(np.array(p1) - np.array(p2))

    def get_ear(self, landmarks, refer_idxs, frame_width, frame_height):
        """計算指定眼睛關鍵點的EAR"""
        coords_points = []
        for i in refer_idxs:
            lm = landmarks[i]
            coord = denormalize_coordinates(lm.x, lm.y, frame_width, frame_height)
            coords_points.append(coord)

        if None in coords_points:
            return 0.0, None

        P2_P6 = self.distance(coords_points[1], coords_points[5])
        P3_P5 = self.distance(coords_points[2], coords_points[4])
        P1_P4 = self.distance(coords_points[0], coords_points[3])

        ear = (P2_P6 + P3_P5) / (2.0 * P1_P4)
        return ear, coords_points

    def calculate_avg_ear(self, landmarks, frame_w, frame_h):
        """計算左右眼EAR平均"""
        left_ear, left_coords = self.get_ear(landmarks, self.eye_idxs["left"], frame_w, frame_h)
        right_ear, right_coords = self.get_ear(landmarks, self.eye_idxs["right"], frame_w, frame_h)
        avg_ear = (left_ear + right_ear) / 2.0
        return avg_ear, (left_coords, right_coords)

    def plot_eye_landmarks(self, frame, left_coords, right_coords, color):
        """畫出眼睛關鍵點"""
        for coords in [left_coords, right_coords]:
            if coords:
                for pt in coords:
                    cv2.circle(frame, pt, 2, color, -1)
        return frame

    def plot_text(self, image, text, origin, color, font=cv2.FONT_HERSHEY_SIMPLEX, fntScale=0.8, thickness=2):
        """在影像上顯示文字"""
        return cv2.putText(image, text, origin, font, fntScale, color, thickness)

    def process(self, frame, thresholds):
        """
        主要疲勞偵測流程：
        - thresholds: dict, 包含 "EAR_THRESH" (眼睛閉合閾值) 與 "WAIT_TIME" (持續閉眼秒數)
        回傳：處理後frame與是否觸發警示布林值
        """
        frame.flags.writeable = False  # 偵測前設唯讀，提升效能
        frame_h, frame_w, _ = frame.shape

        drowsy_txt_pos = (10, int(frame_h * 0.85))
        ear_text_pos = (10, 40)  # EAR 文字往下移避免和FPS重疊

        results = self.facemesh_model.process(frame)
        frame.flags.writeable = True   # 偵測後恢復可寫

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            avg_ear, coords = self.calculate_avg_ear(landmarks, frame_w, frame_h)
            frame = self.plot_eye_landmarks(frame, coords[0], coords[1], self.state_tracker["color"])

            if avg_ear < thresholds["EAR_THRESH"]:
                now = time.perf_counter()
                self.state_tracker["drowsy_time"] += now - self.state_tracker["start_time"]
                self.state_tracker["start_time"] = now
                self.state_tracker["color"] = COLOR_RED

                if self.state_tracker["drowsy_time"] >= thresholds["WAIT_TIME"]:
                    self.state_tracker["play_alarm"] = True
                    frame = self.plot_text(frame, "WAKE UP! WAKE UP!", drowsy_txt_pos, COLOR_RED)
            else:
                self.state_tracker["start_time"] = time.perf_counter()
                self.state_tracker["drowsy_time"] = 0.0
                self.state_tracker["color"] = COLOR_GREEN
                self.state_tracker["play_alarm"] = False

            ear_text = f"EAR: {avg_ear:.2f}"
            drowsy_text = f"Drowsy Time: {self.state_tracker['drowsy_time']:.2f}s"
            frame = self.plot_text(frame, ear_text, ear_text_pos, self.state_tracker["color"])
            frame = self.plot_text(frame, drowsy_text, drowsy_txt_pos, self.state_tracker["color"])
        else:
            # 沒有偵測到臉部，重置所有狀態
            self.state_tracker["start_time"] = time.perf_counter()
            self.state_tracker["drowsy_time"] = 0.0
            self.state_tracker["color"] = COLOR_GREEN
            self.state_tracker["play_alarm"] = False

        return frame, self.state_tracker["play_alarm"]
