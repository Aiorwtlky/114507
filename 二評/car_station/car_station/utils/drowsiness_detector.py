# utils/drowsiness_detector.py
"""
生產級疲勞駕駛偵測系統
- 使用 MediaPipe Face Mesh 進行精確的臉部特徵點追蹤
- 個體化校準系統：適應不同駕駛的眼睛大小、臉型
- 多指標綜合判斷：EAR + 眨眼頻率 + 頭部姿態
- 時間序列分析：避免瞬間誤判
"""

import cv2
import numpy as np
import mediapipe as mp
from scipy.spatial import distance
from collections import deque
from datetime import datetime, timedelta
import json
import os


class PersonalizedDrowsinessDetector:
    """個體化疲勞駕駛偵測器"""
    
    def __init__(self, driver_id=None):
        """
        初始化偵測器
        
        Args:
            driver_id: 駕駛員 ID（用於載入個人化校準數據）
        """
        self.driver_id = driver_id
        
        # MediaPipe Face Mesh 初始化
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # 眼睛關鍵點索引（MediaPipe 468 點模型）
        self.LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
        
        # 頭部姿態關鍵點
        self.NOSE_TIP = 1
        self.CHIN = 152
        self.LEFT_EYE_CORNER = 263
        self.RIGHT_EYE_CORNER = 33
        
        # 個體化基準值（會在首次使用時校準）
        self.baseline_ear = None  # 正常睜眼時的 EAR
        self.baseline_mar = None  # 正常閉嘴時的 MAR
        self.calibration_samples = []
        self.is_calibrated = False
        
        # 動態閾值（根據個人基準調整）
        self.ear_threshold_factor = 0.7  # 當 EAR < baseline * 0.7 視為閉眼
        self.drowsy_ear_threshold_factor = 0.5  # 極度疲勞
        
        # 時間序列緩衝區
        self.ear_history = deque(maxlen=30)  # 保留最近 30 幀（約 1 秒）
        self.blink_history = deque(maxlen=300)  # 保留最近 10 秒的眨眼記錄
        self.head_pose_history = deque(maxlen=30)
        
        # 狀態追蹤
        self.consecutive_closed_frames = 0
        self.total_blinks = 0
        self.last_blink_time = None
        self.drowsiness_level = 0  # 0-3 級別
        
        # 載入個人化校準數據（如果存在）
        self._load_calibration()
    
    def _load_calibration(self):
        """載入駕駛員的個人化校準數據"""
        if not self.driver_id:
            return
        
        calibration_file = f"calibrations/driver_{self.driver_id}.json"
        if os.path.exists(calibration_file):
            try:
                with open(calibration_file, 'r') as f:
                    data = json.load(f)
                    self.baseline_ear = data.get('baseline_ear')
                    self.baseline_mar = data.get('baseline_mar')
                    self.is_calibrated = True
                    print(f"✅ 載入駕駛員 {self.driver_id} 的校準數據")
            except Exception as e:
                print(f"⚠️ 載入校準數據失敗: {e}")
    
    def save_calibration(self):
        """儲存個人化校準數據"""
        if not self.driver_id or not self.is_calibrated:
            return
        
        os.makedirs("calibrations", exist_ok=True)
        calibration_file = f"calibrations/driver_{self.driver_id}.json"
        
        data = {
            'driver_id': self.driver_id,
            'baseline_ear': self.baseline_ear,
            'baseline_mar': self.baseline_mar,
            'calibrated_at': datetime.now().isoformat()
        }
        
        with open(calibration_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ 已儲存駕駛員 {self.driver_id} 的校準數據")
    
    def calibrate(self, frame):
        """
        個體化校準程序
        
        在行程開始時，收集駕駛員正常睜眼的 EAR 值
        建立個人化基準，適應不同眼睛大小
        
        Args:
            frame: 影像幀
            
        Returns:
            bool: 是否完成校準
        """
        if self.is_calibrated:
            return True
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            
            # 計算當前 EAR
            left_ear = self._calculate_ear(landmarks, self.LEFT_EYE_INDICES)
            right_ear = self._calculate_ear(landmarks, self.RIGHT_EYE_INDICES)
            avg_ear = (left_ear + right_ear) / 2.0
            
            # 只收集正常睜眼的樣本（排除眨眼）
            if avg_ear > 0.2:  # 基本閾值，排除明顯閉眼
                self.calibration_samples.append(avg_ear)
            
            # 收集 30 個有效樣本後完成校準
            if len(self.calibration_samples) >= 30:
                # 使用中位數作為基準（比平均值更穩健）
                self.baseline_ear = np.median(self.calibration_samples)
                self.is_calibrated = True
                
                print(f"✅ 校準完成！駕駛員基準 EAR: {self.baseline_ear:.3f}")
                self.save_calibration()
                return True
        
        # 顯示校準進度
        progress = len(self.calibration_samples)
        if progress % 5 == 0 and progress > 0:
            print(f"🔧 校準中... {progress}/30 樣本")
        
        return False
    
    def _calculate_ear(self, landmarks, eye_indices):
        """
        計算眼睛縱橫比 (Eye Aspect Ratio)
        
        EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
        p1-p4: 眼睛水平寬度
        p2-p6, p3-p5: 眼睛垂直高度
        
        正常睜眼: EAR ≈ 0.25-0.35
        閉眼: EAR < 0.15
        """
        points = []
        for idx in eye_indices:
            landmark = landmarks[idx]
            points.append([landmark.x, landmark.y])
        
        points = np.array(points)
        
        # 計算垂直距離
        vertical1 = distance.euclidean(points[1], points[5])
        vertical2 = distance.euclidean(points[2], points[4])
        
        # 計算水平距離
        horizontal = distance.euclidean(points[0], points[3])
        
        # EAR 公式
        if horizontal == 0:
            return 0
        
        ear = (vertical1 + vertical2) / (2.0 * horizontal)
        return ear
    
    def _calculate_head_pose(self, landmarks, frame_shape):
        """
        計算頭部姿態角度
        
        Returns:
            (pitch, yaw, roll): 俯仰角、偏航角、翻滾角（度）
        """
        h, w = frame_shape[:2]
        
        # 3D 模型關鍵點（標準臉部模型）
        model_points = np.array([
            (0.0, 0.0, 0.0),             # 鼻尖
            (0.0, -330.0, -65.0),        # 下巴
            (-225.0, 170.0, -135.0),     # 左眼角
            (225.0, 170.0, -135.0),      # 右眼角
            (-150.0, -150.0, -125.0),    # 左嘴角
            (150.0, -150.0, -125.0)      # 右嘴角
        ], dtype=np.float64)
        
        # 2D 影像關鍵點
        image_points = np.array([
            (landmarks[self.NOSE_TIP].x * w, landmarks[self.NOSE_TIP].y * h),
            (landmarks[self.CHIN].x * w, landmarks[self.CHIN].y * h),
            (landmarks[self.LEFT_EYE_CORNER].x * w, landmarks[self.LEFT_EYE_CORNER].y * h),
            (landmarks[self.RIGHT_EYE_CORNER].x * w, landmarks[self.RIGHT_EYE_CORNER].y * h),
            (landmarks[61].x * w, landmarks[61].y * h),  # 左嘴角
            (landmarks[291].x * w, landmarks[291].y * h)  # 右嘴角
        ], dtype=np.float64)
        
        # 相機內參矩陣
        focal_length = w
        center = (w / 2, h / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float64)
        
        # 畸變係數（假設無畸變）
        dist_coeffs = np.zeros((4, 1))
        
        # 求解 PnP 問題
        success, rotation_vector, translation_vector = cv2.solvePnP(
            model_points,
            image_points,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        if not success:
            return None, None, None
        
        # 將旋轉向量轉換為旋轉矩陣
        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        
        # 計算歐拉角
        sy = np.sqrt(rotation_matrix[0, 0] ** 2 + rotation_matrix[1, 0] ** 2)
        
        pitch = np.arctan2(-rotation_matrix[2, 0], sy) * 180 / np.pi
        yaw = np.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0]) * 180 / np.pi
        roll = np.arctan2(rotation_matrix[2, 1], rotation_matrix[2, 2]) * 180 / np.pi
        
        return pitch, yaw, roll
    
    def _analyze_blink_frequency(self):
        """
        分析眨眼頻率
        
        正常眨眼: 15-20 次/分鐘
        疲勞時: < 10 次/分鐘或過度頻繁（> 30 次/分鐘）
        
        Returns:
            str: 'normal', 'too_low', 'too_high'
        """
        if len(self.blink_history) < 100:
            return 'normal'
        
        # 計算最近 1 分鐘的眨眼次數
        recent_blinks = sum(1 for t in self.blink_history if t > datetime.now() - timedelta(seconds=60))
        
        if recent_blinks < 10:
            return 'too_low'  # 疲勞徵兆
        elif recent_blinks > 30:
            return 'too_high'  # 可能是眼睛疲勞或緊張
        else:
            return 'normal'
    
    def detect(self, frame):
        """
        主要偵測函數
        
        Args:
            frame: OpenCV 影像幀
            
        Returns:
            dict: 偵測結果，包含疲勞等級、EAR 值、建議等
        """
        # 檢查是否需要校準
        if not self.is_calibrated:
            self.calibrate(frame)
            return {
                'status': 'calibrating',
                'progress': len(self.calibration_samples),
                'required': 30
            }
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return {
                'status': 'no_face',
                'message': '未偵測到臉部'
            }
        
        landmarks = results.multi_face_landmarks[0].landmark
        
        # 1. 計算 EAR
        left_ear = self._calculate_ear(landmarks, self.LEFT_EYE_INDICES)
        right_ear = self._calculate_ear(landmarks, self.RIGHT_EYE_INDICES)
        avg_ear = (left_ear + right_ear) / 2.0
        
        self.ear_history.append(avg_ear)
        
        # 2. 計算頭部姿態
        pitch, yaw, roll = self._calculate_head_pose(landmarks, frame.shape)
        if pitch is not None:
            self.head_pose_history.append((pitch, yaw, roll))
        
        # 3. 判斷閉眼狀態（使用個人化閾值）
        ear_threshold = self.baseline_ear * self.ear_threshold_factor
        drowsy_threshold = self.baseline_ear * self.drowsy_ear_threshold_factor
        
        is_eyes_closed = avg_ear < ear_threshold
        
        if is_eyes_closed:
            self.consecutive_closed_frames += 1
        else:
            # 眨眼檢測（快速閉合後開啟）
            if self.consecutive_closed_frames > 2 and self.consecutive_closed_frames < 10:
                self.total_blinks += 1
                self.blink_history.append(datetime.now())
            
            self.consecutive_closed_frames = 0
        
        # 4. 疲勞等級判斷
        drowsiness_level = 0
        event_type = None
        duration = self.consecutive_closed_frames / 30.0  # 假設 30 FPS
        
        # 計算移動平均 EAR（更穩定）
        if len(self.ear_history) >= 5:
            moving_avg_ear = np.mean(list(self.ear_history)[-5:])
        else:
            moving_avg_ear = avg_ear
        
        # 多層判斷邏輯
        if self.consecutive_closed_frames >= 90:  # 持續閉眼 3 秒以上
            drowsiness_level = 3
            event_type = 'drowsy_severe'
        elif self.consecutive_closed_frames >= 30:  # 持續閉眼 1-3 秒
            drowsiness_level = 2
            event_type = 'drowsy_moderate'
        elif moving_avg_ear < drowsy_threshold:  # EAR 持續偏低
            drowsiness_level = 1
            event_type = 'drowsy_mild'
        
        # 5. 眨眼頻率分析
        blink_status = self._analyze_blink_frequency()
        if blink_status == 'too_low' and drowsiness_level < 2:
            drowsiness_level = max(drowsiness_level, 1)
        
        # 6. 頭部姿態分析（低頭可能是打瞌睡）
        if len(self.head_pose_history) >= 10:
            recent_pitch = [p[0] for p in list(self.head_pose_history)[-10:]]
            avg_pitch = np.mean(recent_pitch)
            
            # 頭部持續低垂（低頭超過 20 度）
            if avg_pitch < -20 and drowsiness_level < 2:
                drowsiness_level = max(drowsiness_level, 1)
                event_type = event_type or 'drowsy_head_drop'
        
        # 7. 建構返回結果
        result = {
            'status': 'detected',
            'drowsiness_level': drowsiness_level,
            'event_type': event_type,
            'metrics': {
                'ear': round(avg_ear, 3),
                'baseline_ear': round(self.baseline_ear, 3),
                'ear_threshold': round(ear_threshold, 3),
                'closed_duration': round(duration, 2),
                'total_blinks': self.total_blinks,
                'blink_frequency': blink_status,
                'head_pose': {
                    'pitch': round(pitch, 1) if pitch else None,
                    'yaw': round(yaw, 1) if yaw else None,
                    'roll': round(roll, 1) if roll else None
                }
            },
            'confidence': self._calculate_confidence(drowsiness_level, avg_ear, ear_threshold)
        }
        
        return result
    
    def _calculate_confidence(self, level, ear, threshold):
        """
        計算偵測信心度
        
        考慮因素：
        - EAR 與閾值的差距
        - 時間序列穩定性
        - 是否已完成校準
        """
        if level == 0:
            return 0.0
        
        # 基礎信心度：根據 EAR 與閾值的比例
        ear_ratio = 1.0 - (ear / threshold) if ear < threshold else 0.0
        base_confidence = min(ear_ratio * 1.5, 1.0)
        
        # 時間序列穩定性加成
        if len(self.ear_history) >= 10:
            recent_ears = list(self.ear_history)[-10:]
            ear_std = np.std(recent_ears)
            stability_factor = 1.0 - min(ear_std / 0.05, 0.3)  # 穩定性最多加 30%
        else:
            stability_factor = 0.7
        
        # 校準完成加成
        calibration_factor = 1.0 if self.is_calibrated else 0.8
        
        confidence = base_confidence * stability_factor * calibration_factor
        
        return round(min(confidence, 0.99), 2)


# 全域單例
_drowsiness_detector = None

def get_drowsiness_detector(driver_id=None):
    """取得疲勞偵測器的單例"""
    global _drowsiness_detector
    if _drowsiness_detector is None or (driver_id and _drowsiness_detector.driver_id != driver_id):
        _drowsiness_detector = PersonalizedDrowsinessDetector(driver_id)
    return _drowsiness_detector