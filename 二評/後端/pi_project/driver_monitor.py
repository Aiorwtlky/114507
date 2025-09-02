import cv2
import numpy as np
import time
import threading
from typing import Dict, Any, Optional, List
import mediapipe as mp
from utils import (
    calculate_ear_robust,
    setup_logging,
    get_performance_monitor,
    rotation_matrix_to_euler_angles
)
from config import config

class DriverMonitor:
    """基礎駕駛員監控系統"""
    
    def __init__(self, config_obj=None):
        self.config = config_obj or config
        self.logger = setup_logging()
        self.performance_monitor = get_performance_monitor('driver_monitor')
        
        # MediaPipe 初始化
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=self.config.ai.mp_max_num_faces,
            refine_landmarks=True,
            min_detection_confidence=self.config.ai.mp_detection_confidence,
            min_tracking_confidence=self.config.ai.mp_tracking_confidence
        )
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=self.config.ai.mp_max_num_hands,
            min_detection_confidence=self.config.ai.mp_detection_confidence,
            min_tracking_confidence=self.config.ai.mp_tracking_confidence
        )
        
        # 面部關鍵點索引
        self.LEFT_EYE_LANDMARKS = [33, 7, 163, 144, 145, 153]
        self.RIGHT_EYE_LANDMARKS = [362, 382, 381, 380, 374, 373]
        self.FACE_OVAL_LANDMARKS = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288]
        
        # 狀態追蹤
        self.eye_closed_start_time = None
        self.head_distraction_start_time = None
        self.phone_usage_start_time = None
        
        # 歷史資料
        self.ear_history = []
        self.head_pose_history = []
        
        # 執行緒安全
        self._lock = threading.Lock()
        
        self.logger.info("基礎駕駛員監控系統已初始化")
    
    def analyze_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        分析單幀影像
        
        Args:
            frame: 輸入影像
            
        Returns:
            Dict: 分析結果
        """
        self.performance_monitor.start_frame()
        current_time = time.time()
        
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 面部檢測
            face_results = self.face_mesh.process(rgb_frame)
            hand_results = self.hands.process(rgb_frame)
            
            alerts = []
            driver_state = {}
            
            if face_results.multi_face_landmarks:
                face_landmarks = face_results.multi_face_landmarks[0]
                landmarks = np.array([[lm.x * frame.shape[1], lm.y * frame.shape[0]] 
                                    for lm in face_landmarks.landmark])
                
                # 眼部狀態分析
                eye_state = self._analyze_eye_state(landmarks, current_time)
                driver_state.update(eye_state)
                
                # 頭部姿態分析
                head_pose = self._analyze_head_pose(landmarks, current_time)
                driver_state.update(head_pose)
                
                # 疲勞檢測
                fatigue_alerts = self._detect_fatigue(eye_state, current_time)
                alerts.extend(fatigue_alerts)
                
                # 分心檢測
                distraction_alerts = self._detect_distraction(head_pose, current_time)
                alerts.extend(distraction_alerts)
            
            # 手機使用檢測
            if hand_results.multi_hand_landmarks:
                phone_alerts = self._detect_phone_usage(hand_results, current_time)
                alerts.extend(phone_alerts)
            
            result = {
                'timestamp': current_time,
                'alerts': alerts,
                'driver_state': driver_state,
                'face_detected': face_results.multi_face_landmarks is not None,
                'hands_detected': hand_results.multi_hand_landmarks is not None
            }
            
            self.performance_monitor.end_frame()
            return result
            
        except Exception as e:
            self.logger.error(f"分析幀時發生錯誤: {e}")
            self.performance_monitor.end_frame()
            return {
                'timestamp': current_time,
                'alerts': [],
                'driver_state': {},
                'error': str(e)
            }
    
    def _analyze_eye_state(self, landmarks: np.ndarray, current_time: float) -> Dict[str, Any]:
        """分析眼部狀態"""
        try:
            # 提取眼部地標
            left_eye = landmarks[self.LEFT_EYE_LANDMARKS]
            right_eye = landmarks[self.RIGHT_EYE_LANDMARKS]
            
            # 計算 EAR
            left_ear = calculate_ear_robust(left_eye)
            right_ear = calculate_ear_robust(right_eye)
            avg_ear = (left_ear + right_ear) / 2.0
            
            # 更新歷史記錄
            with self._lock:
                self.ear_history.append({
                    'ear': avg_ear,
                    'timestamp': current_time
                })
                
                # 保持最近的記錄
                if len(self.ear_history) > self.config.ai.ear_history_size:
                    self.ear_history.pop(0)
            
            # 判斷眼睛是否閉合
            is_closed = avg_ear < self.config.ai.default_ear_threshold
            
            # 計算眼部不對稱性
            asymmetry = abs(left_ear - right_ear)
            
            return {
                'ear': avg_ear,
                'left_ear': left_ear,
                'right_ear': right_ear,
                'is_closed': is_closed,
                'asymmetry': asymmetry,
                'ear_threshold': self.config.ai.default_ear_threshold
            }
            
        except Exception as e:
            self.logger.error(f"眼部狀態分析錯誤: {e}")
            return {}
    
    def _analyze_head_pose(self, landmarks: np.ndarray, current_time: float) -> Dict[str, Any]:
        """分析頭部姿態"""
        try:
            # 使用面部地標估算頭部姿態
            # 簡化版本，使用關鍵點的相對位置
            
            # 鼻尖
            nose_tip = landmarks[1]  # 鼻尖點
            # 下巴
            chin = landmarks[18]     # 下巴點
            # 額頭中心
            forehead = landmarks[10] # 額頭點
            
            # 計算角度（簡化版本）
            # 實際應用中可能需要更複雜的 3D 姿態估算
            
            # 垂直角度（點頭）
            vertical_diff = nose_tip[1] - forehead[1]
            pitch = np.arctan2(vertical_diff, abs(nose_tip[0] - forehead[0])) * 180 / np.pi
            
            # 水平角度（搖頭）
            horizontal_diff = nose_tip[0] - (landmarks[33][0] + landmarks[362][0]) / 2
            yaw = np.arctan2(horizontal_diff, 100) * 180 / np.pi  # 假設距離
            
            # 傾斜角度
            left_eye_center = np.mean(landmarks[self.LEFT_EYE_LANDMARKS], axis=0)
            right_eye_center = np.mean(landmarks[self.RIGHT_EYE_LANDMARKS], axis=0)
            eye_diff = left_eye_center[1] - right_eye_center[1]
            roll = np.arctan2(eye_diff, abs(left_eye_center[0] - right_eye_center[0])) * 180 / np.pi
            
            # 更新歷史記錄
            pose_data = {
                'pitch': pitch,
                'yaw': yaw,
                'roll': roll,
                'timestamp': current_time
            }
            
            with self._lock:
                self.head_pose_history.append(pose_data)
                if len(self.head_pose_history) > 100:
                    self.head_pose_history.pop(0)
            
            return {
                'head_pitch': pitch,
                'head_yaw': yaw,
                'head_roll': roll,
                'head_pose_magnitude': np.sqrt(pitch**2 + yaw**2 + roll**2)
            }
            
        except Exception as e:
            self.logger.error(f"頭部姿態分析錯誤: {e}")
            return {}
    
    def _detect_fatigue(self, eye_state: Dict[str, Any], current_time: float) -> List[Dict[str, Any]]:
        """檢測疲勞狀態"""
        alerts = []
        
        try:
            if not eye_state or 'is_closed' not in eye_state:
                return alerts
            
            is_closed = eye_state['is_closed']
            
            if is_closed:
                # 開始計時或繼續計時
                if self.eye_closed_start_time is None:
                    self.eye_closed_start_time = current_time
                
                closed_duration = current_time - self.eye_closed_start_time
                
                # 重度疲勞駕駛 (閉眼超過3秒)
                if closed_duration >= self.config.time_thresholds['eye_closed_severe']:
                    alerts.append({
                        'code': 'A01',
                        'name': self.config.alert_scoring['A01']['name'],
                        'score': self.config.alert_scoring['A01']['score'],
                        'duration': closed_duration,
                        'confidence': self._calculate_alert_confidence('A01', eye_state),
                        'timestamp': current_time
                    })
                
                # 中度疲勞駕駛 (閉眼1-3秒)
                elif closed_duration >= self.config.time_thresholds['eye_closed_medium']:
                    alerts.append({
                        'code': 'A02',
                        'name': self.config.alert_scoring['A02']['name'],
                        'score': self.config.alert_scoring['A02']['score'],
                        'duration': closed_duration,
                        'confidence': self._calculate_alert_confidence('A02', eye_state),
                        'timestamp': current_time
                    })
            
            else:
                # 眼睛張開，重置計時器
                self.eye_closed_start_time = None
            
        except Exception as e:
            self.logger.error(f"疲勞檢測錯誤: {e}")
        
        return alerts
    
    def _detect_distraction(self, head_pose: Dict[str, Any], current_time: float) -> List[Dict[str, Any]]:
        """檢測分心狀態"""
        alerts = []
        
        try:
            if not head_pose or 'head_pose_magnitude' not in head_pose:
                return alerts
            
            # 設定分心閾值（角度）
            distraction_threshold = 30.0  # 度
            pose_magnitude = head_pose['head_pose_magnitude']
            
            is_distracted = pose_magnitude > distraction_threshold
            
            if is_distracted:
                # 開始計時或繼續計時
                if self.head_distraction_start_time is None:
                    self.head_distraction_start_time = current_time
                
                distraction_duration = current_time - self.head_distraction_start_time
                
                # 長時間分心 (低頭/轉頭超過5秒)
                if distraction_duration >= self.config.time_thresholds['head_distraction']:
                    alerts.append({
                        'code': 'A03',
                        'name': self.config.alert_scoring['A03']['name'],
                        'score': self.config.alert_scoring['A03']['score'],
                        'duration': distraction_duration,
                        'head_angle': pose_magnitude,
                        'confidence': self._calculate_alert_confidence('A03', head_pose),
                        'timestamp': current_time
                    })
            
            else:
                # 頭部回到正常位置，重置計時器
                self.head_distraction_start_time = None
        
        except Exception as e:
            self.logger.error(f"分心檢測錯誤: {e}")
        
        return alerts
    
    def _detect_phone_usage(self, hand_results, current_time: float) -> List[Dict[str, Any]]:
        """檢測手機使用"""
        alerts = []
        
        try:
            if not hand_results.multi_hand_landmarks:
                self.phone_usage_start_time = None
                return alerts
            
            # 簡化的手機檢測邏輯
            # 檢測手部是否在耳部附近或面部前方
            phone_gesture_detected = self._analyze_phone_gesture(hand_results)
            
            if phone_gesture_detected:
                if self.phone_usage_start_time is None:
                    self.phone_usage_start_time = current_time
                
                usage_duration = current_time - self.phone_usage_start_time
                
                # 駕駛中使用手機
                if usage_duration >= self.config.time_thresholds['phone_detection']:
                    alerts.append({
                        'code': 'A04',
                        'name': self.config.alert_scoring['A04']['name'],
                        'score': self.config.alert_scoring['A04']['score'],
                        'duration': usage_duration,
                        'confidence': 0.7,  # 簡化的信心度
                        'timestamp': current_time
                    })
            
            else:
                self.phone_usage_start_time = None
        
        except Exception as e:
            self.logger.error(f"手機使用檢測錯誤: {e}")
        
        return alerts
    
    def _analyze_phone_gesture(self, hand_results) -> bool:
        """分析手機使用手勢"""
        try:
            # 簡化的手機檢測邏輯
            # 檢查手部位置是否在可能使用手機的區域
            
            for hand_landmarks in hand_results.multi_hand_landmarks:
                # 檢查拇指和食指的相對位置
                thumb_tip = hand_landmarks.landmark[4]  # 拇指尖
                index_tip = hand_landmarks.landmark[8]  # 食指尖
                
                # 如果手指呈現握持姿態且位置在面部區域
                finger_distance = np.sqrt(
                    (thumb_tip.x - index_tip.x)**2 + 
                    (thumb_tip.y - index_tip.y)**2
                )
                
                # 手部在面部高度
                hand_height = (thumb_tip.y + index_tip.y) / 2
                
                # 簡化判斷：手指距離小且在面部高度
                if finger_distance < 0.1 and hand_height < 0.6:
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _calculate_alert_confidence(self, alert_code: str, state_data: Dict[str, Any]) -> float:
        """計算警報信心度"""
        try:
            if alert_code in ['A01', 'A02']:
                # 疲勞警報信心度基於 EAR 值
                if 'ear' in state_data and 'ear_threshold' in state_data:
                    ear = state_data['ear']
                    threshold = state_data['ear_threshold']
                    confidence = max(0.5, min(1.0, (threshold - ear) / threshold + 0.5))
                    return confidence
            
            elif alert_code == 'A03':
                # 分心警報信心度基於頭部角度
                if 'head_pose_magnitude' in state_data:
                    angle = state_data['head_pose_magnitude']
                    confidence = max(0.5, min(1.0, angle / 60.0))
                    return confidence
            
            return 0.7  # 預設信心度
            
        except Exception:
            return 0.5
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        try:
            with self._lock:
                ear_count = len(self.ear_history)
                pose_count = len(self.head_pose_history)
            
            performance_stats = self.performance_monitor.get_stats()
            
            return {
                'system_name': 'DriverMonitor',
                'status': 'running',
                'ear_history_count': ear_count,
                'pose_history_count': pose_count,
                'performance': performance_stats,
                'config': {
                    'ear_threshold': self.config.ai.default_ear_threshold,
                    'detection_confidence': self.config.ai.mp_detection_confidence
                }
            }
            
        except Exception as e:
            return {
                'system_name': 'DriverMonitor',
                'status': 'error',
                'error': str(e)
            }
    
    def reset_state(self):
        """重置監控狀態"""
        try:
            with self._lock:
                self.eye_closed_start_time = None
                self.head_distraction_start_time = None
                self.phone_usage_start_time = None
                self.ear_history.clear()
                self.head_pose_history.clear()
            
            self.logger.info("駕駛員監控狀態已重置")
            
        except Exception as e:
            self.logger.error(f"重置狀態時發生錯誤: {e}")
    
    def __del__(self):
        """清理資源"""
        try:
            if hasattr(self, 'face_mesh'):
                self.face_mesh.close()
            if hasattr(self, 'hands'):
                self.hands.close()
        except Exception:
            pass

# 如果直接執行此檔案，則進入測試模式
if __name__ == "__main__":
    import sys
    
    print("駕駛員監控測試模式")
    
    monitor = DriverMonitor()
    cap = cv2.VideoCapture(config.camera.internal_camera_index)
    
    if not cap.isOpened():
        print("無法開啟攝影機")
        sys.exit(1)
    
    print("開始監控，按 'q' 退出")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 分析幀
            result = monitor.analyze_frame(frame)
            
            # 顯示結果
            if result['alerts']:
                for alert in result['alerts']:
                    print(f"警報: {alert['code']} - {alert['name']} (信心度: {alert['confidence']:.2f})")
            
            # 顯示狀態
            if result['driver_state']:
                state = result['driver_state']
                if 'ear' in state:
                    cv2.putText(frame, f"EAR: {state['ear']:.3f}", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow('Driver Monitor Test', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("用戶中斷測試")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("測試結束")