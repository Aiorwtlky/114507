import cv2
import numpy as np
import time
import threading
from typing import Dict, Any, Optional, List
from driver_monitor import DriverMonitor
from driver_calibration import DriverCalibration, DriverProfile
from utils import (
    calculate_ear_robust,
    setup_logging,
    get_performance_monitor
)
from config import config

class AdaptiveDriverMonitor(DriverMonitor):
    """適應性駕駛員監控系統（個人化版本）"""
    
    def __init__(self, config_obj=None, driver_id: Optional[str] = None):
        super().__init__(config_obj)
        
        self.driver_id = driver_id
        self.driver_profile = None
        self.calibration_system = DriverCalibration(self.config)
        
        # 動態閾值系統
        self.dynamic_threshold = self.config.ai.default_ear_threshold
        self.threshold_adaptation_active = True
        self.adaptation_samples = []
        
        # 個人化參數
        self.personalized_thresholds = {}
        
        # 載入駕駛員檔案
        if driver_id:
            self._load_driver_profile(driver_id)
        
        # 效能監控
        self.performance_monitor = get_performance_monitor('adaptive_driver_monitor')
        
        self.logger.info(f"適應性駕駛員監控系統已初始化 (Driver ID: {driver_id})")
    
    def _load_driver_profile(self, driver_id: str) -> bool:
        """載入駕駛員個人檔案"""
        try:
            self.driver_profile = self.calibration_system.load_driver_profile(driver_id)
            
            if self.driver_profile:
                # 設定個人化閾值
                self.dynamic_threshold = self.driver_profile.eye_closure_threshold
                self.personalized_thresholds = {
                    'eye_closure': self.driver_profile.eye_closure_threshold,
                    'blink': self.driver_profile.blink_ear_threshold,
                    'baseline_ear': self.driver_profile.baseline_ear,
                    'ear_std': self.driver_profile.ear_std
                }
                
                # 設定頭部姿態基準
                if self.driver_profile.head_pose_baseline:
                    self.head_pose_baseline = self.driver_profile.head_pose_baseline
                else:
                    self.head_pose_baseline = {'pitch': 0, 'yaw': 0, 'roll': 0}
                
                self.logger.info(f"已載入駕駛員檔案: {self.driver_profile.name}")
                self.logger.info(f"個人化閾值: {self.driver_profile.eye_closure_threshold:.3f}")
                
                return True
            
            else:
                self.logger.warning(f"找不到駕駛員檔案: {driver_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"載入駕駛員檔案失敗: {e}")
            return False
    
    def analyze_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        分析單幀影像（個人化版本）
        
        Args:
            frame: 輸入影像
            
        Returns:
            Dict: 分析結果
        """
        self.performance_monitor.start_frame()
        current_time = time.time()
        
        try:
            # 基礎分析
            result = super().analyze_frame(frame)
            
            # 個人化處理
            if result['driver_state'] and self.driver_profile:
                enhanced_state = self._enhance_with_personalization(
                    result['driver_state'], current_time
                )
                result['driver_state'].update(enhanced_state)
                
                # 重新評估警報
                result['alerts'] = self._reassess_alerts_with_personalization(
                    result['driver_state'], current_time
                )
            
            # 動態閾值更新
            if result['driver_state'] and 'ear' in result['driver_state']:
                self._update_dynamic_threshold(result['driver_state']['ear'])
            
            # 添加個人化資訊
            result['personalization'] = {
                'driver_id': self.driver_id,
                'profile_loaded': self.driver_profile is not None,
                'dynamic_threshold': self.dynamic_threshold,
                'adaptation_active': self.threshold_adaptation_active
            }
            
            if self.driver_profile:
                result['personalization']['driver_name'] = self.driver_profile.name
                result['personalization']['confidence_score'] = self.driver_profile.confidence_score
            
            self.performance_monitor.end_frame()
            return result
            
        except Exception as e:
            self.logger.error(f"個人化分析幀時發生錯誤: {e}")
            self.performance_monitor.end_frame()
            return super().analyze_frame(frame)  # 回退到基礎版本
    
    def _enhance_with_personalization(self, driver_state: Dict[str, Any], current_time: float) -> Dict[str, Any]:
        """使用個人化資料增強駕駛狀態分析"""
        enhanced = {}
        
        try:
            if 'ear' in driver_state:
                ear = driver_state['ear']
                
                # 個人化眼部狀態評估
                personalized_eye_state = self._analyze_personalized_eye_state(ear)
                enhanced.update(personalized_eye_state)
                
                # 疲勞程度評估
                fatigue_level = self._calculate_fatigue_level(ear)
                enhanced['fatigue_level'] = fatigue_level
                
                # 與基準的偏差
                if 'baseline_ear' in self.personalized_thresholds:
                    baseline_deviation = abs(ear - self.personalized_thresholds['baseline_ear'])
                    enhanced['baseline_deviation'] = baseline_deviation
            
            # 個人化頭部姿態分析
            if all(key in driver_state for key in ['head_pitch', 'head_yaw', 'head_roll']):
                personalized_pose = self._analyze_personalized_head_pose(driver_state)
                enhanced.update(personalized_pose)
        
        except Exception as e:
            self.logger.error(f"個人化增強處理錯誤: {e}")
        
        return enhanced
    
    def _analyze_personalized_eye_state(self, ear: float) -> Dict[str, Any]:
        """個人化眼部狀態分析"""
        result = {}
        
        try:
            # 使用個人化閾值
            personal_threshold = self.personalized_thresholds.get('eye_closure', self.dynamic_threshold)
            result['is_closed_personalized'] = ear < personal_threshold
            result['closure_confidence'] = self._calculate_closure_confidence(ear, personal_threshold)
            
            # 眨眼檢測
            blink_threshold = self.personalized_thresholds.get('blink', 0.2)
            result['is_blinking'] = ear < blink_threshold
            
            # 相對於個人基準的狀態
            if 'baseline_ear' in self.personalized_thresholds:
                baseline = self.personalized_thresholds['baseline_ear']
                ear_std = self.personalized_thresholds.get('ear_std', 0.05)
                
                # 標準化分數
                z_score = (ear - baseline) / ear_std if ear_std > 0 else 0
                result['ear_z_score'] = z_score
                result['alertness_score'] = max(0, min(1, (z_score + 3) / 6))  # 0-1 scale
            
        except Exception as e:
            self.logger.error(f"個人化眼部分析錯誤: {e}")
        
        return result
    
    def _analyze_personalized_head_pose(self, driver_state: Dict[str, Any]) -> Dict[str, Any]:
        """個人化頭部姿態分析"""
        result = {}
        
        try:
            current_pitch = driver_state['head_pitch']
            current_yaw = driver_state['head_yaw']
            current_roll = driver_state['head_roll']
            
            # 與個人基準的偏差
            baseline_pitch = self.head_pose_baseline.get('pitch', 0)
            baseline_yaw = self.head_pose_baseline.get('yaw', 0)
            baseline_roll = self.head_pose_baseline.get('roll', 0)
            
            pitch_deviation = abs(current_pitch - baseline_pitch)
            yaw_deviation = abs(current_yaw - baseline_yaw)
            roll_deviation = abs(current_roll - baseline_roll)
            
            result['head_pitch_deviation'] = pitch_deviation
            result['head_yaw_deviation'] = yaw_deviation
            result['head_roll_deviation'] = roll_deviation
            
            # 總體偏差分數
            total_deviation = np.sqrt(pitch_deviation**2 + yaw_deviation**2 + roll_deviation**2)
            result['head_pose_deviation_total'] = total_deviation
            
            # 分心程度評估
            distraction_threshold = 25.0  # 可調整
            result['is_distracted_personalized'] = total_deviation > distraction_threshold
            result['distraction_confidence'] = min(1.0, total_deviation / 45.0)
            
        except Exception as e:
            self.logger.error(f"個人化頭部姿態分析錯誤: {e}")
        
        return result
    
    def _calculate_closure_confidence(self, ear: float, threshold: float) -> float:
        """計算眼睛閉合的信心度"""
        try:
            if ear >= threshold:
                return 0.0  # 眼睛張開
            
            # 計算相對於閾值的信心度
            max_diff = threshold * 0.5  # 假設最大差異為閾值的50%
            actual_diff = threshold - ear
            confidence = min(1.0, actual_diff / max_diff)
            
            return confidence
            
        except Exception:
            return 0.5
    
    def _calculate_fatigue_level(self, ear: float) -> str:
        """計算疲勞程度"""
        try:
            threshold = self.personalized_thresholds.get('eye_closure', self.dynamic_threshold)
            baseline = self.personalized_thresholds.get('baseline_ear', 0.3)
            
            if ear >= baseline * 0.9:
                return "alert"
            elif ear >= threshold * 1.2:
                return "mild_drowsy"
            elif ear >= threshold:
                return "moderate_drowsy"
            else:
                return "severe_drowsy"
                
        except Exception:
            return "unknown"
    
    def _update_dynamic_threshold(self, current_ear: float):
        """更新動態閾值"""
        try:
            if not self.threshold_adaptation_active or self.driver_profile:
                return  # 有個人檔案時不使用動態適應
            
            # 添加樣本到適應集合
            with self._lock:
                self.adaptation_samples.append({
                    'ear': current_ear,
                    'timestamp': time.time()
                })
                
                # 保持最近的樣本
                if len(self.adaptation_samples) > 1000:
                    self.adaptation_samples.pop(0)
                
                # 每100個樣本更新一次閾值
                if len(self.adaptation_samples) >= 100 and len(self.adaptation_samples) % 100 == 0:
                    self._recalculate_dynamic_threshold()
        
        except Exception as e:
            self.logger.error(f"動態閾值更新錯誤: {e}")
    
    def _recalculate_dynamic_threshold(self):
        """重新計算動態閾值"""
        try:
            if len(self.adaptation_samples) < 50:
                return
            
            # 提取最近的EAR值
            recent_ears = [sample['ear'] for sample in self.adaptation_samples[-200:]]
            
            # 過濾異常值
            q25, q75 = np.percentile(recent_ears, [25, 75])
            iqr = q75 - q25
            lower_bound = q25 - 1.5 * iqr
            upper_bound = q75 + 1.5 * iqr
            
            filtered_ears = [ear for ear in recent_ears if lower_bound <= ear <= upper_bound]
            
            if len(filtered_ears) < 20:
                return
            
            # 計算新閾值
            mean_ear = np.mean(filtered_ears)
            std_ear = np.std(filtered_ears)
            
            # 新閾值 = 平均值 - 1.5個標準差
            new_threshold = mean_ear - 1.5 * std_ear
            
            # 限制閾值範圍
            new_threshold = max(0.15, min(0.35, new_threshold))
            
            # 平滑更新
            alpha = 0.1  # 學習率
            self.dynamic_threshold = alpha * new_threshold + (1 - alpha) * self.dynamic_threshold
            
            self.logger.debug(f"動態閾值更新為: {self.dynamic_threshold:.3f}")
            
        except Exception as e:
            self.logger.error(f"重新計算動態閾值錯誤: {e}")
    
    def _reassess_alerts_with_personalization(self, driver_state: Dict[str, Any], current_time: float) -> List[Dict[str, Any]]:
        """使用個人化資料重新評估警報"""
        alerts = []
        
        try:
            # 個人化疲勞檢測
            if 'is_closed_personalized' in driver_state:
                fatigue_alerts = self._detect_personalized_fatigue(driver_state, current_time)
                alerts.extend(fatigue_alerts)
            
            # 個人化分心檢測
            if 'is_distracted_personalized' in driver_state:
                distraction_alerts = self._detect_personalized_distraction(driver_state, current_time)
                alerts.extend(distraction_alerts)
            
            # 手機使用檢測（保持原有邏輯）
            # 這部分不需要個人化
            
        except Exception as e:
            self.logger.error(f"個人化警報評估錯誤: {e}")
        
        return alerts
    
    def _detect_personalized_fatigue(self, driver_state: Dict[str, Any], current_time: float) -> List[Dict[str, Any]]:
        """個人化疲勞檢測"""
        alerts = []
        
        try:
            is_closed = driver_state.get('is_closed_personalized', False)
            confidence = driver_state.get('closure_confidence', 0.5)
            
            # 只有在高信心度時才觸發警報
            if is_closed and confidence > 0.6:
                if self.eye_closed_start_time is None:
                    self.eye_closed_start_time = current_time
                
                closed_duration = current_time - self.eye_closed_start_time
                
                # 重度疲勞
                if closed_duration >= self.config.time_thresholds['eye_closed_severe']:
                    alerts.append({
                        'code': 'A01',
                        'name': self.config.alert_scoring['A01']['name'],
                        'score': self.config.alert_scoring['A01']['score'],
                        'duration': closed_duration,
                        'confidence': confidence,
                        'personalized': True,
                        'threshold_used': self.dynamic_threshold,
                        'timestamp': current_time
                    })
                
                # 中度疲勞
                elif closed_duration >= self.config.time_thresholds['eye_closed_medium']:
                    alerts.append({
                        'code': 'A02',
                        'name': self.config.alert_scoring['A02']['name'],
                        'score': self.config.alert_scoring['A02']['score'],
                        'duration': closed_duration,
                        'confidence': confidence,
                        'personalized': True,
                        'threshold_used': self.dynamic_threshold,
                        'timestamp': current_time
                    })
            
            else:
                self.eye_closed_start_time = None
        
        except Exception as e:
            self.logger.error(f"個人化疲勞檢測錯誤: {e}")
        
        return alerts
    
    def _detect_personalized_distraction(self, driver_state: Dict[str, Any], current_time: float) -> List[Dict[str, Any]]:
        """個人化分心檢測"""
        alerts = []
        
        try:
            is_distracted = driver_state.get('is_distracted_personalized', False)
            confidence = driver_state.get('distraction_confidence', 0.5)
            deviation = driver_state.get('head_pose_deviation_total', 0)
            
            if is_distracted and confidence > 0.6:
                if self.head_distraction_start_time is None:
                    self.head_distraction_start_time = current_time
                
                distraction_duration = current_time - self.head_distraction_start_time
                
                # 長時間分心
                if distraction_duration >= self.config.time_thresholds['head_distraction']:
                    alerts.append({
                        'code': 'A03',
                        'name': self.config.alert_scoring['A03']['name'],
                        'score': self.config.alert_scoring['A03']['score'],
                        'duration': distraction_duration,
                        'head_deviation': deviation,
                        'confidence': confidence,
                        'personalized': True,
                        'timestamp': current_time
                    })
            
            else:
                self.head_distraction_start_time = None
        
        except Exception as e:
            self.logger.error(f"個人化分心檢測錯誤: {e}")
        
        return alerts
    
    def set_driver(self, driver_id: str) -> bool:
        """切換駕駛員"""
        try:
            self.reset_state()  # 重置狀態
            self.driver_id = driver_id
            
            if self._load_driver_profile(driver_id):
                self.logger.info(f"已切換到駕駛員: {driver_id}")
                return True
            else:
                self.logger.warning(f"切換駕駛員失敗: {driver_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"設定駕駛員時發生錯誤: {e}")
            return False
    
    def get_personalization_status(self) -> Dict[str, Any]:
        """獲取個人化狀態"""
        try:
            status = {
                'driver_id': self.driver_id,
                'profile_loaded': self.driver_profile is not None,
                'dynamic_threshold': self.dynamic_threshold,
                'adaptation_active': self.threshold_adaptation_active,
                'adaptation_samples_count': len(self.adaptation_samples)
            }
            
            if self.driver_profile:
                status.update({
                    'driver_name': self.driver_profile.name,
                    'calibration_date': self.driver_profile.calibration_date,
                    'confidence_score': self.driver_profile.confidence_score,
                    'personalized_threshold': self.driver_profile.eye_closure_threshold,
                    'baseline_ear': self.driver_profile.baseline_ear
                })
            
            return status
            
        except Exception as e:
            return {'error': str(e)}
    
    def disable_adaptation(self):
        """停用動態適應"""
        self.threshold_adaptation_active = False
        self.logger.info("動態閾值適應已停用")
    
    def enable_adaptation(self):
        """啟用動態適應"""
        if not self.driver_profile:  # 只有在沒有個人檔案時才啟用
            self.threshold_adaptation_active = True
            self.logger.info("動態閾值適應已啟用")

# 如果直接執行此檔案，則進入測試模式
if __name__ == "__main__":
    import sys
    
    print("適應性駕駛員監控測試模式")
    
    # 列出可用的駕駛員檔案
    calibration = DriverCalibration(config)
    profiles = calibration.list_driver_profiles()
    
    if profiles:
        print("可用的駕駛員檔案:")
        for i, profile in enumerate(profiles):
            print(f"{i+1}. {profile['name']} (ID: {profile['driver_id']})")
        
        choice = input("選擇駕駛員編號 (Enter 使用預設): ")
        
        if choice.isdigit() and 1 <= int(choice) <= len(profiles):
            driver_id = profiles[int(choice)-1]['driver_id']
        else:
            driver_id = None
    else:
        print("沒有可用的駕駛員檔案，使用動態適應模式")
        driver_id = None
    
    monitor = AdaptiveDriverMonitor(driver_id=driver_id)
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
                    personalized = " (個人化)" if alert.get('personalized', False) else ""
                    print(f"警報{personalized}: {alert['code']} - {alert['name']}")
            
            # 顯示狀態
            if result['driver_state']:
                state = result['driver_state']
                if 'ear' in state:
                    threshold = result['personalization']['dynamic_threshold']
                    cv2.putText(frame, f"EAR: {state['ear']:.3f} | Threshold: {threshold:.3f}", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                if 'fatigue_level' in state:
                    cv2.putText(frame, f"Fatigue: {state['fatigue_level']}", 
                               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # 顯示個人化資訊
            if result['personalization']['profile_loaded']:
                cv2.putText(frame, f"Driver: {result['personalization']['driver_name']}", 
                           (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            cv2.imshow('Adaptive Driver Monitor Test', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("用戶中斷測試")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("測試結束")