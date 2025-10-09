# event_detectors/advanced_fatigue_detector.py
"""
智能自適應疲勞偵測器
參考專案：
- https://github.com/Guarouba/driver-drowsiness-detection
- https://github.com/akshaybahadur21/Drowsiness_Detection
- https://github.com/commaai/openpilot
"""

import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import time
from scipy.spatial import distance
from scipy import signal
import json
import os

class FatigueDetector:
    def __init__(self, fps=30):
        # MediaPipe 初始化
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # 精確的眼部關鍵點索引（MediaPipe 468點模型）
        # 參考：https://github.com/google/mediapipe/blob/master/mediapipe/modules/face_geometry/data/canonical_face_model_uv_visualization.png
        self.LEFT_EYE_POINTS = {
            'upper': [159, 158, 157, 153, 145, 144],
            'lower': [163, 7, 33, 133, 155, 154],
            'corners': [33, 133]  # 內外眼角
        }
        
        self.RIGHT_EYE_POINTS = {
            'upper': [386, 387, 388, 466, 374, 380],
            'lower': [390, 249, 263, 362, 382, 381],
            'corners': [362, 263]  # 內外眼角
        }
        
        # 嘴部關鍵點（用於打哈欠偵測）
        self.MOUTH_POINTS = {
            'upper': [13, 14, 269, 270, 267],
            'lower': [17, 18, 175, 321, 375],
            'corners': [61, 291]
        }
        
        self.FPS = fps
        
        # === 自適應校準系統 ===
        self.calibration_mode = "AUTO"  # AUTO, ASIAN, WESTERN, CUSTOM
        self.calibration_samples = deque(maxlen=fps * 5)  # 5秒校準樣本
        self.calibration_complete = False
        self.calibration_start_time = None
        
        # 用戶檔案（儲存個人化設定）
        self.user_profile_path = "user_profiles/"
        self.current_user_profile = None
        
        # === 動態閾值系統 ===
        self.ear_baseline = None
        self.ear_std_dev = None
        self.mar_baseline = None  # Mouth Aspect Ratio for yawning
        
        # 預設閾值（會被自動校準覆蓋）
        self.ear_thresholds = {
            'blink': 0.85,      # baseline * 0.85 = 眨眼
            'drowsy': 0.75,     # baseline * 0.75 = 疲憊
            'closed': 0.65,     # baseline * 0.65 = 閉眼
            'min_ear': 0.15,    # 最小合理 EAR 值
            'max_ear': 0.40     # 最大合理 EAR 值
        }
        
        # PERCLOS (Percentage of Eye Closure) - 業界標準
        self.perclos_window = deque(maxlen=fps * 60)  # 60秒窗口
        self.perclos_threshold = 0.15  # 15% 閉眼時間表示疲勞
        
        # 眨眼模式分析
        self.blink_detector = BlinkPatternAnalyzer(fps)
        
        # 頭部姿態分析
        self.head_pose_analyzer = HeadPoseAnalyzer()
        
        # === 時間閾值 ===
        self.MICROSLEEP_TIME = 0.5      # 微睡眠
        self.DROWSY_TIME = 1.5          # 疲憊
        self.CLOSED_TIME_WARNING = 2.0  # 警告
        self.CLOSED_TIME_A02 = 3.0      # 中度疲勞
        self.CLOSED_TIME_A01 = 5.0      # 重度疲勞
        self.YAWN_TIME = 2.0            # 打哈欠時間
        
        # 計時器
        self.eye_closed_start_time = None
        self.yawn_start_time = None
        self.last_blink_time = None
        
        # 歷史記錄
        self.ear_history = deque(maxlen=fps * 2)  # 2秒歷史
        self.mar_history = deque(maxlen=fps * 2)
        
        # 事件管理
        self.event_cooldown = {}
        self.fatigue_score = 0  # 0-100 綜合疲勞分數
        
        # 統計資料
        self.stats = {
            'total_blinks': 0,
            'long_closures': 0,
            'yawns': 0,
            'head_nods': 0,
            'calibration_quality': 0
        }

    def load_or_create_profile(self, user_id="default"):
        """載入或創建用戶檔案"""
        if not os.path.exists(self.user_profile_path):
            os.makedirs(self.user_profile_path)
        
        profile_file = f"{self.user_profile_path}{user_id}.json"
        
        if os.path.exists(profile_file):
            with open(profile_file, 'r') as f:
                self.current_user_profile = json.load(f)
                print(f"載入用戶檔案: {user_id}")
                # 套用已儲存的設定
                self.ear_baseline = self.current_user_profile.get('ear_baseline')
                self.ear_std_dev = self.current_user_profile.get('ear_std_dev')
                self.calibration_mode = self.current_user_profile.get('eye_type', 'AUTO')
        else:
            self.current_user_profile = {
                'user_id': user_id,
                'eye_type': 'AUTO',
                'ear_baseline': None,
                'ear_std_dev': None,
                'created': time.time()
            }
            print(f"創建新用戶檔案: {user_id}")

    def save_profile(self):
        """儲存用戶檔案"""
        if self.current_user_profile:
            self.current_user_profile.update({
                'ear_baseline': self.ear_baseline,
                'ear_std_dev': self.ear_std_dev,
                'eye_type': self.calibration_mode,
                'last_updated': time.time()
            })
            
            user_id = self.current_user_profile.get('user_id', 'default')
            profile_file = f"{self.user_profile_path}{user_id}.json"
            
            with open(profile_file, 'w') as f:
                json.dump(self.current_user_profile, f, indent=2)

    def calculate_ear_advanced(self, eye_points):
        """
        進階 EAR 計算 - 使用更多點位和加權平均
        參考：Real-Time Eye Blink Detection using Facial Landmarks (Soukupová and Čech, 2016)
        """
        if len(eye_points['upper']) < 3 or len(eye_points['lower']) < 3:
            return 0.25
        
        # 計算多個垂直距離
        vertical_distances = []
        for i in range(min(len(eye_points['upper']), len(eye_points['lower']))):
            dist = distance.euclidean(eye_points['upper'][i], eye_points['lower'][i])
            vertical_distances.append(dist)
        
        # 計算水平距離（眼角距離）
        if len(eye_points['corners']) >= 2:
            horizontal_dist = distance.euclidean(eye_points['corners'][0], eye_points['corners'][1])
        else:
            horizontal_dist = 1.0
        
        if horizontal_dist == 0:
            return 0.25
        
        # 加權平均（中間的點權重更高）
        weights = np.array([1.0, 1.5, 2.0, 2.0, 1.5, 1.0])[:len(vertical_distances)]
        weights = weights / weights.sum()
        
        weighted_vertical = np.average(vertical_distances, weights=weights)
        ear = weighted_vertical / horizontal_dist
        
        return ear

    def calculate_mar(self, mouth_points):
        """計算嘴部縱橫比（用於打哈欠偵測）"""
        if len(mouth_points['upper']) < 3 or len(mouth_points['lower']) < 3:
            return 0.0
        
        # 計算嘴部垂直距離
        vertical_dist = np.mean([
            distance.euclidean(mouth_points['upper'][i], mouth_points['lower'][i])
            for i in range(min(3, len(mouth_points['upper']), len(mouth_points['lower'])))
        ])
        
        # 計算嘴角水平距離
        if len(mouth_points['corners']) >= 2:
            horizontal_dist = distance.euclidean(mouth_points['corners'][0], mouth_points['corners'][1])
        else:
            return 0.0
        
        if horizontal_dist == 0:
            return 0.0
        
        mar = vertical_dist / horizontal_dist
        return mar

    def auto_calibrate(self, ear_value):
        """
        自動校準系統 - 智能識別用戶眼型
        基於統計分析自動調整閾值
        """
        current_time = time.time()
        
        # 開始校準
        if self.calibration_start_time is None:
            self.calibration_start_time = current_time
            print("開始自動校準...")
        
        # 收集校準樣本
        if ear_value > 0.10 and ear_value < 0.45:  # 合理範圍
            self.calibration_samples.append(ear_value)
        
        # 校準時間檢查
        calibration_duration = current_time - self.calibration_start_time
        
        if calibration_duration > 3.0 and len(self.calibration_samples) > self.FPS * 2:
            # 進行統計分析
            samples = np.array(self.calibration_samples)
            
            # 去除異常值（使用 IQR 方法）
            q1, q3 = np.percentile(samples, [25, 75])
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            filtered_samples = samples[(samples >= lower_bound) & (samples <= upper_bound)]
            
            if len(filtered_samples) > 10:
                # 計算基準線和標準差
                self.ear_baseline = np.median(filtered_samples)
                self.ear_std_dev = np.std(filtered_samples)
                
                # 自動判斷眼型
                if self.ear_baseline < 0.22:
                    self.calibration_mode = "ASIAN"
                    print(f"檢測到亞洲眼型特徵 (基準 EAR: {self.ear_baseline:.3f})")
                elif self.ear_baseline > 0.28:
                    self.calibration_mode = "WESTERN"
                    print(f"檢測到西方眼型特徵 (基準 EAR: {self.ear_baseline:.3f})")
                else:
                    self.calibration_mode = "MIXED"
                    print(f"檢測到混合眼型特徵 (基準 EAR: {self.ear_baseline:.3f})")
                
                # 設定個人化閾值
                self.update_thresholds()
                self.calibration_complete = True
                
                # 儲存檔案
                self.save_profile()
                
                print(f"校準完成！")
                print(f"  基準 EAR: {self.ear_baseline:.3f}")
                print(f"  標準差: {self.ear_std_dev:.3f}")
                print(f"  眨眼閾值: {self.ear_baseline * self.ear_thresholds['blink']:.3f}")
                print(f"  疲憊閾值: {self.ear_baseline * self.ear_thresholds['drowsy']:.3f}")
                print(f"  閉眼閾值: {self.ear_baseline * self.ear_thresholds['closed']:.3f}")
                
                # 計算校準品質
                self.stats['calibration_quality'] = min(100, 
                    (len(filtered_samples) / len(samples)) * 100)

    def update_thresholds(self):
        """根據眼型更新閾值"""
        if self.calibration_mode == "ASIAN":
            # 亞洲眼型調整
            self.ear_thresholds['blink'] = 0.88
            self.ear_thresholds['drowsy'] = 0.78
            self.ear_thresholds['closed'] = 0.68
        elif self.calibration_mode == "WESTERN":
            # 西方眼型調整
            self.ear_thresholds['blink'] = 0.85
            self.ear_thresholds['drowsy'] = 0.75
            self.ear_thresholds['closed'] = 0.65
        else:
            # 混合或預設
            self.ear_thresholds['blink'] = 0.86
            self.ear_thresholds['drowsy'] = 0.76
            self.ear_thresholds['closed'] = 0.66

    def calculate_perclos(self):
        """計算 PERCLOS (Percentage of Eye Closure)"""
        if len(self.perclos_window) < self.FPS * 10:  # 至少需要10秒數據
            return 0.0
        
        closed_frames = sum(1 for x in self.perclos_window if x)
        total_frames = len(self.perclos_window)
        
        return closed_frames / total_frames if total_frames > 0 else 0.0

    def calculate_fatigue_score(self):
        """
        計算綜合疲勞分數 (0-100)
        基於多個指標的加權平均
        """
        score = 0
        
        # PERCLOS 貢獻 (40%)
        perclos = self.calculate_perclos()
        score += min(40, perclos * 400)  # PERCLOS 0.1 = 40分
        
        # 眨眼頻率貢獻 (20%)
        if hasattr(self, 'blink_detector'):
            blink_score = self.blink_detector.get_fatigue_score()
            score += blink_score * 0.2
        
        # 長時間閉眼貢獻 (20%)
        if self.eye_closed_start_time:
            closed_duration = time.time() - self.eye_closed_start_time
            score += min(20, closed_duration * 4)  # 5秒 = 20分
        
        # 打哈欠貢獻 (10%)
        recent_yawns = self.stats.get('yawns', 0)
        score += min(10, recent_yawns * 5)  # 2次哈欠 = 10分
        
        # 頭部動作貢獻 (10%)
        head_nods = self.stats.get('head_nods', 0)
        score += min(10, head_nods * 5)
        
        self.fatigue_score = min(100, score)
        return self.fatigue_score

    def analyze_frame(self, frame, frame_count):
        display_frame = frame.copy()
        event = None
        h, w = frame.shape[:2]
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)
        
        current_time = time.time()
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            landmarks = np.array([(lm.x * w, lm.y * h) for lm in face_landmarks.landmark])
            
            # === 眼部分析 ===
            # 左眼
            left_eye = {
                'upper': landmarks[self.LEFT_EYE_POINTS['upper']],
                'lower': landmarks[self.LEFT_EYE_POINTS['lower']],
                'corners': landmarks[self.LEFT_EYE_POINTS['corners']]
            }
            
            # 右眼
            right_eye = {
                'upper': landmarks[self.RIGHT_EYE_POINTS['upper']],
                'lower': landmarks[self.RIGHT_EYE_POINTS['lower']],
                'corners': landmarks[self.RIGHT_EYE_POINTS['corners']]
            }
            
            # 計算 EAR
            left_ear = self.calculate_ear_advanced(left_eye)
            right_ear = self.calculate_ear_advanced(right_eye)
            ear = (left_ear + right_ear) / 2.0
            
            # 平滑處理
            self.ear_history.append(ear)
            if len(self.ear_history) > 3:
                # 使用中值濾波減少雜訊
                smoothed_ear = np.median(list(self.ear_history)[-5:])
            else:
                smoothed_ear = ear
            
            # === 嘴部分析（打哈欠）===
            mouth = {
                'upper': landmarks[self.MOUTH_POINTS['upper']],
                'lower': landmarks[self.MOUTH_POINTS['lower']],
                'corners': landmarks[self.MOUTH_POINTS['corners']]
            }
            mar = self.calculate_mar(mouth)
            self.mar_history.append(mar)
            
            # === 頭部姿態分析 ===
            head_pose = self.head_pose_analyzer.analyze(landmarks)
            
            # === 自動校準 ===
            if not self.calibration_complete:
                self.auto_calibrate(smoothed_ear)
            
            # === 疲勞偵測邏輯 ===
            if self.calibration_complete and self.ear_baseline:
                # 計算動態閾值
                blink_threshold = self.ear_baseline * self.ear_thresholds['blink']
                drowsy_threshold = self.ear_baseline * self.ear_thresholds['drowsy']
                closed_threshold = self.ear_baseline * self.ear_thresholds['closed']
                
                # 眨眼偵測
                self.blink_detector.update(smoothed_ear, blink_threshold)
                
                # PERCLOS 更新
                self.perclos_window.append(smoothed_ear < closed_threshold)
                
                # 判斷眼睛狀態
                if smoothed_ear < closed_threshold:
                    # 眼睛閉合
                    if self.eye_closed_start_time is None:
                        self.eye_closed_start_time = current_time
                    
                    closed_duration = current_time - self.eye_closed_start_time
                    
                    # 檢查不同等級的疲勞
                    if closed_duration >= self.CLOSED_TIME_A01:
                        # ############# 修改處 #############
                        event = "A01 重度疲勞(閉眼5秒以上), 每次扣區間分數40分"
                        self.stats['long_closures'] += 1
                    elif closed_duration >= self.CLOSED_TIME_A02:
                        # ############# 修改處 #############
                        event = "A02 中度疲勞(閉眼3-5秒), 每次扣區間分數30分"
                    elif closed_duration >= self.MICROSLEEP_TIME:
                        # 微睡眠檢測
                        if self.blink_detector.is_microsleep():
                            event = "A02.5: 偵測到微睡眠"
                
                elif smoothed_ear < drowsy_threshold:
                    # 疲憊狀態
                    if self.eye_closed_start_time:
                        # 減緩計時但不重置
                        self.eye_closed_start_time += (current_time - self.eye_closed_start_time) * 0.3
                else:
                    # 眼睛張開
                    self.eye_closed_start_time = None
                
                # 打哈欠偵測
                if self.mar_baseline and mar > self.mar_baseline * 1.5:
                    if self.yawn_start_time is None:
                        self.yawn_start_time = current_time
                    elif current_time - self.yawn_start_time > self.YAWN_TIME:
                        self.stats['yawns'] += 1
                        if self.stats['yawns'] > 2:
                            event = "A05: 頻繁打哈欠（疲勞徵兆）"
                        self.yawn_start_time = None
                else:
                    self.yawn_start_time = None
                
                # 頭部點頭偵測
                if head_pose['nodding']:
                    self.stats['head_nods'] += 1
                    if self.stats['head_nods'] > 3:
                        event = "A06: 頻繁點頭（瞌睡徵兆）"
                
                # 計算綜合疲勞分數
                fatigue_score = self.calculate_fatigue_score()
                
                # 基於疲勞分數的警告
                if not event:
                    if fatigue_score > 70:
                        event = "A01: 高度疲勞風險"
                    elif fatigue_score > 50:
                        event = "A02: 中度疲勞警告"
                    elif fatigue_score > 30:
                        event = "A07: 輕度疲勞提醒"
            
            # === 視覺化 ===
            # 繪製眼部輪廓
            self._draw_eye_contours(display_frame, left_eye, right_eye, smoothed_ear)
            
            # 顯示資訊面板
            self._draw_info_panel(display_frame, smoothed_ear, mar, head_pose)
            
            # 顯示疲勞指標
            self._draw_fatigue_meter(display_frame)
        
        else:
            # 臉部未偵測到
            cv2.putText(display_frame, "NO FACE DETECTED", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        return event, display_frame

    def _draw_eye_contours(self, frame, left_eye, right_eye, ear):
        """繪製眼部輪廓"""
        # 根據 EAR 值決定顏色
        if self.ear_baseline:
            if ear < self.ear_baseline * self.ear_thresholds['closed']:
                color = (0, 0, 255)  # 紅色
            elif ear < self.ear_baseline * self.ear_thresholds['drowsy']:
                color = (0, 165, 255)  # 橙色
            else:
                color = (0, 255, 0)  # 綠色
        else:
            color = (255, 255, 0)  # 黃色（校準中）
        
        # 繪製眼部多邊形
        left_points = np.vstack([left_eye['upper'], left_eye['lower'][::-1]])
        right_points = np.vstack([right_eye['upper'], right_eye['lower'][::-1]])
        
        cv2.polylines(frame, [np.int32(left_points)], True, color, 2)
        cv2.polylines(frame, [np.int32(right_points)], True, color, 2)

    def _draw_info_panel(self, frame, ear, mar, head_pose):
        """繪製資訊面板"""
        h, w = frame.shape[:2]
        
        # 背景
        cv2.rectangle(frame, (5, 5), (350, 180), (0, 0, 0), -1)
        cv2.rectangle(frame, (5, 5), (350, 180), (255, 255, 255), 1)
        
        y = 25
        
        # 校準狀態
        if not self.calibration_complete:
            cv2.putText(frame, "CALIBRATING...", (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            y += 25
            if len(self.calibration_samples) > 0:
                progress = min(100, len(self.calibration_samples) / (self.FPS * 3) * 100)
                cv2.putText(frame, f"Progress: {progress:.0f}%", (10, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
        else:
            cv2.putText(frame, f"Mode: {self.calibration_mode}", (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        y += 30
        
        # EAR 值
        cv2.putText(frame, f"EAR: {ear:.3f}", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        if self.ear_baseline:
            cv2.putText(frame, f" (Base: {self.ear_baseline:.3f})", (120, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        y += 25
        
        # PERCLOS
        perclos = self.calculate_perclos()
        color = (0, 255, 0) if perclos < 0.1 else (0, 165, 255) if perclos < 0.15 else (0, 0, 255)
        cv2.putText(frame, f"PERCLOS: {perclos:.1%}", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        y += 25
        
        # 眨眼統計
        if hasattr(self, 'blink_detector'):
            blink_rate = self.blink_detector.get_blink_rate()
            cv2.putText(frame, f"Blink Rate: {blink_rate:.1f}/min", (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            y += 25
        
        # 疲勞分數
        cv2.putText(frame, f"Fatigue Score: {self.fatigue_score:.0f}/100", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    def _draw_fatigue_meter(self, frame):
        """繪製疲勞儀表"""
        h, w = frame.shape[:2]
        
        # 位置和大小
        meter_x = w - 150
        meter_y = 20
        meter_width = 130
        meter_height = 20
        
        # 背景
        cv2.rectangle(frame, (meter_x-5, meter_y-5), 
                     (meter_x + meter_width + 5, meter_y + meter_height + 30),
                     (0, 0, 0), -1)
        
        # 標題
        cv2.putText(frame, "FATIGUE LEVEL", (meter_x, meter_y-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # 進度條背景
        cv2.rectangle(frame, (meter_x, meter_y), 
                     (meter_x + meter_width, meter_y + meter_height),
                     (100, 100, 100), -1)
        
        # 進度條填充
        fill_width = int(meter_width * (self.fatigue_score / 100))
        if self.fatigue_score < 30:
            color = (0, 255, 0)  # 綠色
        elif self.fatigue_score < 60:
            color = (0, 165, 255)  # 橙色
        else:
            color = (0, 0, 255)  # 紅色
        
        cv2.rectangle(frame, (meter_x, meter_y),
                     (meter_x + fill_width, meter_y + meter_height),
                     color, -1)
        
        # 數值
        cv2.putText(frame, f"{self.fatigue_score:.0f}%", 
                   (meter_x + meter_width//2 - 15, meter_y + meter_height + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)


class BlinkPatternAnalyzer:
    """眨眼模式分析器"""
    def __init__(self, fps):
        self.fps = fps
        self.blink_history = deque(maxlen=fps * 60)  # 60秒歷史
        self.blink_times = deque(maxlen=20)  # 最近20次眨眼時間
        self.is_blinking = False
        self.blink_start_time = None
        self.last_ear = None
        
    def update(self, ear, threshold):
        """更新眨眼狀態"""
        current_time = time.time()
        
        if ear < threshold and not self.is_blinking:
            # 開始眨眼
            self.is_blinking = True
            self.blink_start_time = current_time
            
        elif ear >= threshold and self.is_blinking:
            # 結束眨眼
            self.is_blinking = False
            if self.blink_start_time:
                blink_duration = current_time - self.blink_start_time
                
                # 正常眨眼時間 0.1-0.4 秒
                if 0.05 < blink_duration < 0.5:
                    self.blink_times.append(current_time)
                    self.blink_history.append(1)
                else:
                    self.blink_history.append(0)
        else:
            self.blink_history.append(0)
        
        self.last_ear = ear
    
    def get_blink_rate(self):
        """獲取眨眼頻率（次/分鐘）"""
        if len(self.blink_times) < 2:
            return 0
        
        current_time = time.time()
        recent_blinks = [t for t in self.blink_times if current_time - t < 60]
        
        return len(recent_blinks)
    
    def is_microsleep(self):
        """檢測微睡眠（快速連續閉眼）"""
        if len(self.blink_times) < 3:
            return False
        
        # 檢查最近3次眨眼的間隔
        recent_intervals = []
        for i in range(1, min(3, len(self.blink_times))):
            interval = self.blink_times[-i] - self.blink_times[-i-1]
            recent_intervals.append(interval)
        
        # 如果間隔都很短（< 2秒），可能是微睡眠
        return all(interval < 2.0 for interval in recent_intervals)
    
    def get_fatigue_score(self):
        """基於眨眼模式計算疲勞分數"""
        blink_rate = self.get_blink_rate()
        
        # 正常眨眼頻率：15-20次/分鐘
        # 疲勞時：< 10次/分鐘 或 > 30次/分鐘
        if blink_rate < 10:
            return 50  # 眨眼過少
        elif blink_rate > 30:
            return 70  # 眨眼過多
        else:
            return max(0, 30 - abs(blink_rate - 17.5) * 2)


class HeadPoseAnalyzer:
    """頭部姿態分析器"""
    def __init__(self):
        self.pitch_history = deque(maxlen=30)
        self.yaw_history = deque(maxlen=30)
        self.nod_threshold = 15  # 度
        
    def analyze(self, landmarks):
        """分析頭部姿態"""
        # 簡化的頭部姿態估算
        # 使用鼻尖和臉部中心的關係
        
        nose_tip = landmarks[1]  # 鼻尖
        face_center_x = np.mean(landmarks[:, 0])
        face_center_y = np.mean(landmarks[:, 1])
        
        # 估算偏航角（左右轉頭）
        yaw = (nose_tip[0] - face_center_x) * 100
        
        # 估算俯仰角（點頭）
        pitch = (nose_tip[1] - face_center_y) * 100
        
        self.pitch_history.append(pitch)
        self.yaw_history.append(yaw)
        
        # 檢測點頭
        nodding = False
        if len(self.pitch_history) > 10:
            pitch_variance = np.var(self.pitch_history)
            if pitch_variance > self.nod_threshold:
                nodding = True
        
        return {
            'pitch': pitch,
            'yaw': yaw,
            'nodding': nodding
        }