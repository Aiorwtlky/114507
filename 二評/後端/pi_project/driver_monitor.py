import cv2
import mediapipe as mp
import numpy as np
import logging
import time
from typing import Dict, List, Optional, Tuple
from collections import deque
import json
import os

logger = logging.getLogger(__name__)

class EyeSizeAdaptiveMonitor:
    """眼睛大小自適應的駕駛員監控系統"""
    
    def __init__(self, config, driver_profile_path: str = None):
        self.config = config
        self.driver_profile_path = driver_profile_path or "data/driver_profiles.json"
        
        # MediaPipe 初始化
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=config.mediapipe_min_detection_confidence,
            min_tracking_confidence=config.mediapipe_min_tracking_confidence
        )
        
        # 眼部特徵點索引 (MediaPipe Face Mesh)
        self.LEFT_EYE_INDICES = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        self.RIGHT_EYE_INDICES = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        
        # 更精確的 EAR 計算點
        self.LEFT_EAR_POINTS = [145, 159, 33, 133, 153, 144]  # 上下左右關鍵點
        self.RIGHT_EAR_POINTS = [374, 386, 362, 263, 380, 373]
        
        # 動態追蹤參數
        self.ear_history = deque(maxlen=30)  # 30 frame 歷史
        self.blink_history = deque(maxlen=10)  # 眨眼歷史
        self.eye_openness_baseline = deque(maxlen=100)  # 基準線
        
        # 個人化參數
        self.driver_profile = None
        self.is_calibrated = False
        self.calibration_frames = 0
        self.calibration_data = {
            'normal_ear_values': [],
            'blink_ear_values': [],
            'eye_size_metrics': [],
            'head_pose_range': []
        }
        
        # 警報狀態
        self.consecutive_closed_frames = 0
        self.consecutive_drowsy_frames = 0
        self.consecutive_distraction_frames = 0
        self.last_blink_time = time.time()
        self.blink_rate_history = deque(maxlen=20)
        
    def load_driver_profile(self, driver_id: str) -> bool:
        """載入駕駛員個人檔案"""
        try:
            if os.path.exists(self.driver_profile_path):
                with open(self.driver_profile_path, 'r', encoding='utf-8') as f:
                    profiles = json.load(f)
                    
                if driver_id in profiles:
                    self.driver_profile = profiles[driver_id]
                    self.is_calibrated = True
                    logger.info(f"載入駕駛員檔案: {driver_id}")
                    logger.info(f"駕駛員: {self.driver_profile.get('driver_name', 'Unknown')}")
                    logger.info(f"眼睛類型: {self.driver_profile.get('eye_size_category', 'Unknown')}")
                    return True
            
            logger.warning(f"找不到駕駛員檔案: {driver_id}")
            return False
            
        except Exception as e:
            logger.error(f"載入駕駛員檔案失敗: {e}")
            return False
    
    def calculate_adaptive_ear(self, landmarks, eye_indices) -> float:
        """計算自適應 EAR (Eye Aspect Ratio)"""
        try:
            # 取得眼部關鍵點
            eye_points = []
            for idx in eye_indices:
                point = landmarks[idx]
                eye_points.append([point.x, point.y])
            
            eye_points = np.array(eye_points)
            
            # 計算多個垂直距離 (更準確)
            vertical_distances = []
            
            # 上下眼瞼距離 (多個測量點)
            if len(eye_indices) >= 6:
                # 外側垂直距離
                v1 = np.linalg.norm(eye_points[1] - eye_points[5])
                # 中間垂直距離
                v2 = np.linalg.norm(eye_points[2] - eye_points[4])
                # 內側垂直距離  
                v3 = np.linalg.norm(eye_points[0] - eye_points[3])
                
                vertical_distances = [v1, v2, v3]
            
            # 水平距離
            horizontal_distance = np.linalg.norm(eye_points[0] - eye_points[3])
            
            # 加權平均垂直距離
            avg_vertical = np.mean(vertical_distances) if vertical_distances else 0
            
            # 避免除零
            if horizontal_distance < 1e-6:
                return 0.0
            
            ear = avg_vertical / horizontal_distance
            return ear
            
        except Exception as e:
            logger.error(f"EAR 計算錯誤: {e}")
            return 0.0
    
    def calculate_eye_size_metrics(self, landmarks) -> Dict:
        """計算眼睛大小相關指標"""
        try:
            # 左眼範圍
            left_eye_points = np.array([[landmarks[i].x, landmarks[i].y] for i in self.LEFT_EYE_INDICES])
            right_eye_points = np.array([[landmarks[i].x, landmarks[i].y] for i in self.RIGHT_EYE_INDICES])
            
            # 眼睛寬度 (水平範圍)
            left_eye_width = np.max(left_eye_points[:, 0]) - np.min(left_eye_points[:, 0])
            right_eye_width = np.max(right_eye_points[:, 0]) - np.min(right_eye_points[:, 0])
            
            # 眼睛高度 (垂直範圍)
            left_eye_height = np.max(left_eye_points[:, 1]) - np.min(left_eye_points[:, 1])
            right_eye_height = np.max(right_eye_points[:, 1]) - np.min(right_eye_points[:, 1])
            
            # 眼睛面積 (近似)
            left_eye_area = left_eye_width * left_eye_height
            right_eye_area = right_eye_width * right_eye_height
            
            # 眼睛形狀比例
            left_aspect_ratio = left_eye_width / (left_eye_height + 1e-6)
            right_aspect_ratio = right_eye_width / (right_eye_height + 1e-6)
            
            return {
                'left_eye_width': left_eye_width,
                'right_eye_width': right_eye_width,
                'left_eye_height': left_eye_height,
                'right_eye_height': right_eye_height,
                'left_eye_area': left_eye_area,
                'right_eye_area': right_eye_area,
                'left_aspect_ratio': left_aspect_ratio,
                'right_aspect_ratio': right_aspect_ratio,
                'avg_eye_width': (left_eye_width + right_eye_width) / 2,
                'avg_eye_height': (left_eye_height + right_eye_height) / 2,
                'avg_eye_area': (left_eye_area + right_eye_area) / 2
            }
            
        except Exception as e:
            logger.error(f"眼睛大小計算錯誤: {e}")
            return {}
    
    def detect_head_pose(self, landmarks) -> Dict:
        """檢測頭部姿態"""
        try:
            # 關鍵臉部特徵點
            nose_tip = landmarks[1]
            chin = landmarks[152]
            left_eye_corner = landmarks[33]
            right_eye_corner = landmarks[263]
            left_mouth = landmarks[61]
            right_mouth = landmarks[291]
            
            # 計算頭部傾斜
            eye_center_x = (left_eye_corner.x + right_eye_corner.x) / 2
            eye_center_y = (left_eye_corner.y + right_eye_corner.y) / 2
            
            mouth_center_x = (left_mouth.x + right_mouth.x) / 2
            mouth_center_y = (left_mouth.y + right_mouth.y) / 2
            
            # 垂直方向 (點頭/抬頭)
            vertical_ratio = (nose_tip.y - eye_center_y) / (chin.y - eye_center_y + 1e-6)
            
            # 水平方向 (左右轉頭)
            horizontal_ratio = (nose_tip.x - eye_center_x) / (right_eye_corner.x - left_eye_corner.x + 1e-6)
            
            # 判斷狀態
            looking_down = vertical_ratio > 0.6  # 低頭
            looking_up = vertical_ratio < 0.3    # 抬頭
            looking_left = horizontal_ratio < -0.3  # 左轉
            looking_right = horizontal_ratio > 0.3   # 右轉
            
            distracted = looking_down or looking_up or looking_left or looking_right
            
            return {
                'vertical_ratio': vertical_ratio,
                'horizontal_ratio': horizontal_ratio,
                'looking_down': looking_down,
                'looking_up': looking_up,
                'looking_left': looking_left,
                'looking_right': looking_right,
                'distracted': distracted
            }
            
        except Exception as e:
            logger.error(f"頭部姿態檢測錯誤: {e}")
            return {'distracted': False}
    
    def get_adaptive_thresholds(self, eye_metrics: Dict) -> Dict:
        """根據眼睛大小動態調整閾值"""
        if not self.is_calibrated or not self.driver_profile:
            # 使用動態基準線
            if len(self.eye_openness_baseline) > 10:
                baseline_ear = np.mean(list(self.eye_openness_baseline))
                baseline_std = np.std(list(self.eye_openness_baseline))
                
                # 根據基準線動態調整
                if baseline_ear < 0.2:  # 小眼睛
                    closed_threshold = max(0.08, baseline_ear - 2.0 * baseline_std)
                    drowsy_threshold = max(closed_threshold + 0.02, baseline_ear - 1.0 * baseline_std)
                elif baseline_ear > 0.35:  # 大眼睛
                    closed_threshold = max(0.15, baseline_ear - 2.5 * baseline_std)
                    drowsy_threshold = max(closed_threshold + 0.03, baseline_ear - 1.2 * baseline_std)
                else:  # 中等眼睛
                    closed_threshold = max(0.12, baseline_ear - 2.2 * baseline_std)
                    drowsy_threshold = max(closed_threshold + 0.025, baseline_ear - 1.1 * baseline_std)
            else:
                # 預設值
                closed_threshold = 0.15
                drowsy_threshold = 0.22
        else:
            # 使用校準的個人化閾值
            profile = self.driver_profile
            closed_threshold = profile.get('closed_threshold', 0.15)
            drowsy_threshold = profile.get('drowsy_threshold', 0.22)
        
        return {
            'closed_threshold': closed_threshold,
            'drowsy_threshold': drowsy_threshold,
            'blink_threshold': drowsy_threshold * 0.9
        }
    
    def analyze_frame(self, frame) -> Dict:
        """分析影像框架"""
        result = {
            'face_detected': False,
            'left_ear': 0.0,
            'right_ear': 0.0,
            'avg_ear': 0.0,
            'eye_state': 'unknown',
            'head_pose': {},
            'alerts': [],
            'eye_metrics': {},
            'thresholds': {},
            'debug_info': {}
        }
        
        try:
            # 轉換為 RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                result['face_detected'] = True
                
                # 計算 EAR
                left_ear = self.calculate_adaptive_ear(face_landmarks.landmark, self.LEFT_EAR_POINTS)
                right_ear = self.calculate_adaptive_ear(face_landmarks.landmark, self.RIGHT_EAR_POINTS)
                avg_ear = (left_ear + right_ear) / 2
                
                result['left_ear'] = left_ear
                result['right_ear'] = right_ear
                result['avg_ear'] = avg_ear
                
                # 計算眼睛大小指標
                eye_metrics = self.calculate_eye_size_metrics(face_landmarks.landmark)
                result['eye_metrics'] = eye_metrics
                
                # 檢測頭部姿態
                head_pose = self.detect_head_pose(face_landmarks.landmark)
                result['head_pose'] = head_pose
                
                # 更新基準線
                if avg_ear > 0.1:  # 有效的 EAR 值
                    self.eye_openness_baseline.append(avg_ear)
                
                # 取得自適應閾值
                thresholds = self.get_adaptive_thresholds(eye_metrics)
                result['thresholds'] = thresholds
                
                # 眼睛狀態和頭部姿態判斷
                eye_state, alerts = self.determine_driver_state(avg_ear, head_pose, thresholds)
                result['eye_state'] = eye_state
                result['alerts'] = alerts
                
                # 調試資訊
                result['debug_info'] = {
                    'baseline_ear': np.mean(list(self.eye_openness_baseline)) if self.eye_openness_baseline else 0,
                    'calibrated': self.is_calibrated,
                    'consecutive_closed': self.consecutive_closed_frames,
                    'consecutive_drowsy': self.consecutive_drowsy_frames,
                    'consecutive_distraction': self.consecutive_distraction_frames,
                    'baseline_samples': len(self.eye_openness_baseline)
                }
                
        except Exception as e:
            logger.error(f"影像分析錯誤: {e}")
        
        return result
    
    def determine_driver_state(self, avg_ear: float, head_pose: Dict, thresholds: Dict) -> Tuple[str, List]:
        """判斷駕駛員狀態並產生警報"""
        alerts = []
        
        closed_threshold = thresholds['closed_threshold']
        drowsy_threshold = thresholds['drowsy_threshold']
        
        # 眼睛狀態判斷
        if avg_ear < closed_threshold:
            # 閉眼狀態
            self.consecutive_closed_frames += 1
            self.consecutive_drowsy_frames = 0
            
            if self.consecutive_closed_frames >= self.config.eye_closed_frames_threshold:
                # 重度疲勞 (閉眼超過3秒)
                alerts.append({
                    'code': 'A01',
                    'name': '重度疲勞駕駛',
                    'score': 25,
                    'description': f'閉眼超過 {self.consecutive_closed_frames/self.config.internal_camera_fps:.1f} 秒'
                })
                eye_state = 'severely_drowsy'
            elif self.consecutive_closed_frames >= self.config.drowsy_frames_threshold:
                # 中度疲勞 (閉眼1-3秒)
                alerts.append({
                    'code': 'A02',
                    'name': '中度疲勞駕駛',
                    'score': 15,
                    'description': f'閉眼 {self.consecutive_closed_frames/self.config.internal_camera_fps:.1f} 秒'
                })
                eye_state = 'drowsy'
            else:
                eye_state = 'closed'
                
        elif avg_ear < drowsy_threshold:
            # 微閉眼/疲勞狀態
            self.consecutive_drowsy_frames += 1
            self.consecutive_closed_frames = 0
            
            if self.consecutive_drowsy_frames >= self.config.drowsy_frames_threshold * 2:
                alerts.append({
                    'code': 'A02',
                    'name': '輕度疲勞駕駛',
                    'score': 10,
                    'description': '持續微閉眼狀態'
                })
            
            eye_state = 'drowsy'
            
        else:
            # 正常狀態
            if self.consecutive_closed_frames > 0 or self.consecutive_drowsy_frames > 0:
                # 記錄一次眨眼
                current_time = time.time()
                blink_interval = current_time - self.last_blink_time
                self.blink_rate_history.append(blink_interval)
                self.last_blink_time = current_time
            
            self.consecutive_closed_frames = 0
            self.consecutive_drowsy_frames = 0
            eye_state = 'open'
        
        # 頭部姿態判斷 (分心檢測)
        if head_pose.get('distracted', False):
            self.consecutive_distraction_frames += 1
            
            if self.consecutive_distraction_frames >= self.config.distraction_frames_threshold:
                alerts.append({
                    'code': 'A03',
                    'name': '長時間分心',
                    'score': 20,
                    'description': f'分心超過 {self.consecutive_distraction_frames/self.config.internal_camera_fps:.1f} 秒'
                })
        else:
            self.consecutive_distraction_frames = 0
        
        return eye_state, alerts
    
    def start_calibration(self, driver_name: str):
        """開始個人化校準"""
        self.calibration_frames = 0
        self.calibration_data = {
            'driver_name': driver_name,
            'normal_ear_values': [],
            'blink_ear_values': [],
            'eye_size_metrics': [],
            'head_pose_range': []
        }
        logger.info(f"開始校準駕駛員: {driver_name}")
    
    def add_calibration_frame(self, frame, calibration_type: str = 'normal'):
        """添加校準框架"""
        result = self.analyze_frame(frame)
        
        if result['face_detected']:
            if calibration_type == 'normal':
                self.calibration_data['normal_ear_values'].append(result['avg_ear'])
                self.calibration_data['eye_size_metrics'].append(result['eye_metrics'])
            elif calibration_type == 'blink':
                self.calibration_data['blink_ear_values'].append(result['avg_ear'])
            
            self.calibration_frames += 1
    
    def finish_calibration(self) -> bool:
        """完成校準並儲存個人檔案"""
        try:
            if len(self.calibration_data['normal_ear_values']) < 30:
                logger.error("校準資料不足，需要至少30個有效框架")
                return False
            
            # 計算個人化閾值
            normal_ears = np.array(self.calibration_data['normal_ear_values'])
            normal_ear_mean = np.mean(normal_ears)
            normal_ear_std = np.std(normal_ears)
            
            # 根據個人眼睛特徵調整閾值
            if normal_ear_mean < 0.2:  # 小眼睛
                closed_threshold = max(0.08, normal_ear_mean - 2.0 * normal_ear_std)
                drowsy_threshold = max(closed_threshold + 0.02, normal_ear_mean - 1.0 * normal_ear_std)
                eye_size_category = 'small'
            elif normal_ear_mean > 0.35:  # 大眼睛
                closed_threshold = max(0.15, normal_ear_mean - 2.5 * normal_ear_std)
                drowsy_threshold = max(closed_threshold + 0.03, normal_ear_mean - 1.2 * normal_ear_std)
                eye_size_category = 'large'
            else:  # 一般眼睛
                closed_threshold = max(0.12, normal_ear_mean - 2.2 * normal_ear_std)
                drowsy_threshold = max(closed_threshold + 0.025, normal_ear_mean - 1.1 * normal_ear_std)
                eye_size_category = 'medium'
            
            # 安全範圍限制
            closed_threshold = max(0.08, min(0.25, closed_threshold))
            drowsy_threshold = max(closed_threshold + 0.02, min(0.35, drowsy_threshold))
            
            # 建立個人檔案
            driver_profile = {
                'driver_name': self.calibration_data['driver_name'],
                'calibration_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'normal_ear_mean': float(normal_ear_mean),
                'normal_ear_std': float(normal_ear_std),
                'closed_threshold': float(closed_threshold),
                'drowsy_threshold': float(drowsy_threshold),
                'eye_size_category': eye_size_category,
                'calibration_frames': self.calibration_frames,
                'calibration_quality': self._calculate_calibration_quality(normal_ears)
            }
            
            # 儲存到檔案
            driver_id = self.save_driver_profile(driver_profile)
            self.driver_profile = driver_profile
            self.is_calibrated = True
            
            logger.info(f"校準完成 - 駕駛員ID: {driver_id}")
            logger.info(f"眼睛類型: {eye_size_category}")
            logger.info(f"閾值 - 閉眼: {closed_threshold:.3f}, 疲勞: {drowsy_threshold:.3f}")
            logger.info(f"校準品質: {driver_profile['calibration_quality']:.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"校準失敗: {e}")
            return False
    
    def _calculate_calibration_quality(self, ear_values: np.ndarray) -> float:
        """計算校準品質分數 (0-1)"""
        try:
            # 基於標準差和樣本數量的品質評分
            std_score = max(0, 1 - (np.std(ear_values) / np.mean(ear_values)))
            sample_score = min(1, len(ear_values) / 100)  # 100個樣本為滿分
            
            # 檢查數值範圍合理性
            mean_val = np.mean(ear_values)
            range_score = 1.0 if 0.1 <= mean_val <= 0.6 else 0.5
            
            quality = (std_score * 0.4 + sample_score * 0.4 + range_score * 0.2)
            return quality
            
        except:
            return 0.5
    
    def save_driver_profile(self, profile: Dict) -> str:
        """儲存駕駛員檔案並返回駕駛員ID"""
        try:
            profiles = {}
            if os.path.exists(self.driver_profile_path):
                with open(self.driver_profile_path, 'r', encoding='utf-8') as f:
                    profiles = json.load(f)
            
            driver_id = f"driver_{int(time.time())}"
            profiles[driver_id] = profile
            
            with open(self.driver_profile_path, 'w', encoding='utf-8') as f:
                json.dump(profiles, f, ensure_ascii=False, indent=2)
            
            logger.info(f"駕駛員檔案已儲存: {driver_id}")
            return driver_id
            
        except Exception as e:
            logger.error(f"儲存駕駛員檔案失敗: {e}")
            return ""
    
    def list_driver_profiles(self) -> Dict:
        """列出所有駕駛員檔案"""
        try:
            if os.path.exists(self.driver_profile_path):
                with open(self.driver_profile_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"讀取駕駛員檔案失敗: {e}")
            return {}