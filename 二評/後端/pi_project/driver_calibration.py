import cv2
import numpy as np
import json
import time
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from utils import (
    calculate_ear_robust, 
    save_json_file, 
    load_json_file, 
    setup_logging,
    ensure_directory_exists
)
from config import config

@dataclass
class DriverProfile:
    """駕駛員個人檔案"""
    driver_id: str
    name: str
    baseline_ear: float  # 基準 EAR 值
    ear_std: float       # EAR 標準差
    eye_closure_threshold: float  # 個人化閉眼閾值
    blink_ear_threshold: float    # 眨眼閾值
    head_pose_baseline: Dict[str, float]  # 基準頭部姿態
    calibration_date: str
    sample_count: int
    confidence_score: float  # 校準信心度 (0-1)
    
    def to_dict(self) -> Dict:
        """轉換為字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DriverProfile':
        """從字典建立"""
        return cls(**data)

class CalibrationSession:
    """校準會話"""
    
    def __init__(self, driver_name: str):
        self.driver_name = driver_name
        self.driver_id = f"driver_{int(time.time())}_{hash(driver_name) % 1000}"
        self.start_time = time.time()
        
        # 收集的資料
        self.normal_ear_samples = []
        self.blink_samples = []
        self.head_pose_samples = []
        
        # 校準狀態
        self.current_phase = "ready"
        self.phase_start_time = None
        
        # MediaPipe 初始化
        import mediapipe as mp
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        
        # 眼部地標點索引
        self.LEFT_EYE_LANDMARKS = [33, 7, 163, 144, 145, 153]
        self.RIGHT_EYE_LANDMARKS = [362, 382, 381, 380, 374, 373]
        
        # 日誌
        self.logger = setup_logging()

class DriverCalibration:
    """駕駛員個人化校準系統"""
    
    def __init__(self, config_obj):
        self.config = config_obj
        self.profiles_file = config_obj.driver_profiles_file
        self.logger = setup_logging()
        
        # 確保資料目錄存在
        ensure_directory_exists(os.path.dirname(self.profiles_file))
        
        self.logger.info("駕駛員校準系統已初始化")
    
    def start_calibration(self, driver_name: str) -> Optional[str]:
        """
        開始校準流程
        
        Args:
            driver_name: 駕駛員姓名
            
        Returns:
            str: 駕駛員 ID，失敗時返回 None
        """
        try:
            print(f"\n{'='*50}")
            print(f"🎯 駕駛員個人化校準系統")
            print(f"駕駛員: {driver_name}")
            print(f"日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*50}")
            
            session = CalibrationSession(driver_name)
            
            # 第一階段：正常狀態校準
            if not self._phase_normal_state(session):
                print("❌ 正常狀態校準失敗")
                return None
            
            # 第二階段：眨眼校準
            if not self._phase_blink_calibration(session):
                print("❌ 眨眼校準失敗")
                return None
            
            # 第三階段：頭部姿態校準
            if not self._phase_head_pose_calibration(session):
                print("❌ 頭部姿態校準失敗")
                return None
            
            # 計算個人化參數
            profile = self._calculate_personalized_profile(session)
            if not profile:
                print("❌ 個人化參數計算失敗")
                return None
            
            # 儲存檔案
            if not self._save_driver_profile(profile):
                print("❌ 儲存駕駛員檔案失敗")
                return None
            
            self._display_calibration_results(profile)
            
            self.logger.info(f"駕駛員 {driver_name} 校準完成，ID: {profile.driver_id}")
            return profile.driver_id
            
        except Exception as e:
            self.logger.error(f"校準過程發生錯誤: {e}")
            print(f"❌ 校準失敗: {e}")
            return None
    
    def _phase_normal_state(self, session: CalibrationSession) -> bool:
        """第一階段：正常狀態校準"""
        print(f"\n📋 第一階段：正常駕駛狀態校準")
        print(f"請保持正常的眼睛狀態，直視前方攝影機 30 秒")
        print(f"目標：收集您的基準眼睛狀態資料")
        
        input("準備好後按 Enter 開始...")
        
        cap = cv2.VideoCapture(config.camera.internal_camera_index)
        if not cap.isOpened():
            print("❌ 無法開啟攝影機")
            return False
        
        session.current_phase = "normal_state"
        session.phase_start_time = time.time()
        duration = 30  # 30 秒
        
        print(f"🎥 開始錄製...")
        
        while time.time() - session.phase_start_time < duration:
            ret, frame = cap.read()
            if not ret:
                continue
            
            # 分析當前幀
            ear_data = self._analyze_frame_for_ear(session, frame)
            if ear_data:
                session.normal_ear_samples.append(ear_data)
            
            # 顯示進度
            remaining = duration - (time.time() - session.phase_start_time)
            self._draw_calibration_ui(frame, f"正常狀態校準", remaining, len(session.normal_ear_samples))
            
            cv2.imshow('Driver Calibration', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("用戶中斷校準")
                cap.release()
                cv2.destroyAllWindows()
                return False
        
        cap.release()
        cv2.destroyAllWindows()
        
        # 檢查樣本數量
        if len(session.normal_ear_samples) < 500:
            print(f"❌ 樣本數量不足: {len(session.normal_ear_samples)} < 500")
            return False
        
        print(f"✅ 正常狀態校準完成，收集 {len(session.normal_ear_samples)} 個樣本")
        return True
    
    def _phase_blink_calibration(self, session: CalibrationSession) -> bool:
        """第二階段：眨眼校準"""
        print(f"\n👀 第二階段：眨眼模式校準")
        print(f"請進行 15 次正常眨眼，每次眨眼後稍作停頓")
        print(f"目標：學習您的個人眨眼模式")
        
        input("準備好後按 Enter 開始...")
        
        cap = cv2.VideoCapture(config.camera.internal_camera_index)
        if not cap.isOpened():
            print("❌ 無法開啟攝影機")
            return False
        
        session.current_phase = "blink_calibration"
        session.phase_start_time = time.time()
        target_blinks = 15
        detected_blinks = 0
        
        last_ear = 0.3
        blink_in_progress = False
        blink_start_time = None
        
        print(f"🎥 開始眨眼檢測...")
        
        while detected_blinks < target_blinks:
            ret, frame = cap.read()
            if not ret:
                continue
            
            # 分析當前幀
            ear_data = self._analyze_frame_for_ear(session, frame)
            if not ear_data:
                continue
            
            current_ear = ear_data['avg_ear']
            
            # 眨眼檢測邏輯
            if current_ear < 0.2 and not blink_in_progress:  # 開始眨眼
                blink_in_progress = True
                blink_start_time = time.time()
            elif current_ear > 0.25 and blink_in_progress:  # 眨眼結束
                if blink_start_time and (time.time() - blink_start_time) < 1.0:  # 合理的眨眼時間
                    detected_blinks += 1
                    session.blink_samples.append({
                        'min_ear': min([s['avg_ear'] for s in session.normal_ear_samples[-10:]]),
                        'timestamp': time.time(),
                        'duration': time.time() - blink_start_time
                    })
                    print(f"檢測到眨眼 {detected_blinks}/{target_blinks}")
                
                blink_in_progress = False
                blink_start_time = None
                time.sleep(0.5)  # 避免重複檢測
            
            last_ear = current_ear
            
            # 顯示進度
            self._draw_calibration_ui(frame, f"眨眼校準", 0, detected_blinks, target_blinks)
            cv2.imshow('Driver Calibration', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("用戶中斷校準")
                cap.release()
                cv2.destroyAllWindows()
                return False
        
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"✅ 眨眼校準完成，檢測到 {detected_blinks} 次眨眼")
        return True
    
    def _phase_head_pose_calibration(self, session: CalibrationSession) -> bool:
        """第三階段：頭部姿態校準"""
        print(f"\n🗣️ 第三階段：頭部姿態校準")
        print(f"請保持正常的駕駛姿勢 20 秒")
        print(f"目標：建立您的基準頭部角度")
        
        input("準備好後按 Enter 開始...")
        
        cap = cv2.VideoCapture(config.camera.internal_camera_index)
        if not cap.isOpened():
            print("❌ 無法開啟攝影機")
            return False
        
        session.current_phase = "head_pose"
        session.phase_start_time = time.time()
        duration = 20  # 20 秒
        
        print(f"🎥 開始頭部姿態錄製...")
        
        while time.time() - session.phase_start_time < duration:
            ret, frame = cap.read()
            if not ret:
                continue
            
            # 分析頭部姿態 (簡化版本)
            pose_data = self._analyze_frame_for_head_pose(session, frame)
            if pose_data:
                session.head_pose_samples.append(pose_data)
            
            # 顯示進度
            remaining = duration - (time.time() - session.phase_start_time)
            self._draw_calibration_ui(frame, f"頭部姿態校準", remaining, len(session.head_pose_samples))
            
            cv2.imshow('Driver Calibration', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("用戶中斷校準")
                cap.release()
                cv2.destroyAllWindows()
                return False
        
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"✅ 頭部姿態校準完成，收集 {len(session.head_pose_samples)} 個樣本")
        return True
    
    def _analyze_frame_for_ear(self, session: CalibrationSession, frame: np.ndarray) -> Optional[Dict]:
        """分析幀以提取 EAR 資料"""
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = session.face_mesh.process(rgb_frame)
            
            if not results.multi_face_landmarks:
                return None
            
            face_landmarks = results.multi_face_landmarks[0]
            landmarks = np.array([[lm.x * frame.shape[1], lm.y * frame.shape[0]] 
                                for lm in face_landmarks.landmark])
            
            # 提取眼部地標
            left_eye = landmarks[session.LEFT_EYE_LANDMARKS]
            right_eye = landmarks[session.RIGHT_EYE_LANDMARKS]
            
            # 計算 EAR
            left_ear = calculate_ear_robust(left_eye)
            right_ear = calculate_ear_robust(right_eye)
            avg_ear = (left_ear + right_ear) / 2.0
            
            return {
                'left_ear': left_ear,
                'right_ear': right_ear,
                'avg_ear': avg_ear,
                'timestamp': time.time(),
                'asymmetry': abs(left_ear - right_ear)
            }
            
        except Exception as e:
            return None
    
    def _analyze_frame_for_head_pose(self, session: CalibrationSession, frame: np.ndarray) -> Optional[Dict]:
        """分析幀以提取頭部姿態資料"""
        try:
            # 簡化的頭部姿態估算
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = session.face_mesh.process(rgb_frame)
            
            if not results.multi_face_landmarks:
                return None
            
            # 使用簡化的角度計算
            # 這裡可以實作更複雜的 3D 姿態估算
            return {
                'pitch': 0.0,  # 上下點頭
                'yaw': 0.0,    # 左右搖頭
                'roll': 0.0,   # 傾斜
                'timestamp': time.time()
            }
            
        except Exception:
            return None
    
    def _draw_calibration_ui(self, frame: np.ndarray, phase: str, remaining: float, samples: int, target: int = None):
        """繪製校準 UI"""
        height, width = frame.shape[:2]
        
        # 半透明覆蓋層
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (width, 120), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # 文字資訊
        cv2.putText(frame, f"校準階段: {phase}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        if remaining > 0:
            cv2.putText(frame, f"剩餘時間: {remaining:.1f}s", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        if target:
            cv2.putText(frame, f"進度: {samples}/{target}", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        else:
            cv2.putText(frame, f"樣本數: {samples}", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        # 退出提示
        cv2.putText(frame, "按 'q' 退出", (width - 150, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def _calculate_personalized_profile(self, session: CalibrationSession) -> Optional[DriverProfile]:
        """計算個人化參數"""
        try:
            # 提取 EAR 資料
            normal_ears = [sample['avg_ear'] for sample in session.normal_ear_samples]
            
            if len(normal_ears) < 100:
                print("❌ 正常狀態樣本不足")
                return None
            
            # 計算基本統計
            baseline_ear = np.mean(normal_ears)
            ear_std = np.std(normal_ears)
            
            # 計算個人化閾值
            # 方法1: 基於統計分布
            statistical_threshold = baseline_ear - 2.0 * ear_std
            
            # 方法2: 基於眨眼資料
            blink_threshold = 0.2  # 預設值
            if session.blink_samples:
                blink_ears = [sample['min_ear'] for sample in session.blink_samples]
                blink_threshold = np.mean(blink_ears)
            
            # 最終閾值：兩種方法的加權平均
            final_threshold = 0.7 * statistical_threshold + 0.3 * blink_threshold
            
            # 確保閾值在合理範圍內
            final_threshold = max(0.1, min(0.4, final_threshold))
            
            # 計算信心度
            confidence = self._calculate_confidence_score(session, baseline_ear, ear_std)
            
            # 頭部姿態基準
            head_pose_baseline = {}
            if session.head_pose_samples:
                head_pose_baseline = {
                    'pitch': np.mean([s['pitch'] for s in session.head_pose_samples]),
                    'yaw': np.mean([s['yaw'] for s in session.head_pose_samples]),
                    'roll': np.mean([s['roll'] for s in session.head_pose_samples])
                }
            
            # 建立個人檔案
            profile = DriverProfile(
                driver_id=session.driver_id,
                name=session.driver_name,
                baseline_ear=baseline_ear,
                ear_std=ear_std,
                eye_closure_threshold=final_threshold,
                blink_ear_threshold=blink_threshold,
                head_pose_baseline=head_pose_baseline,
                calibration_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                sample_count=len(session.normal_ear_samples),
                confidence_score=confidence
            )
            
            return profile
            
        except Exception as e:
            self.logger.error(f"計算個人化參數失敗: {e}")
            return None
    
    def _calculate_confidence_score(self, session: CalibrationSession, baseline_ear: float, ear_std: float) -> float:
        """計算校準信心度"""
        try:
            score = 0.0
            
            # 樣本數量因子 (0-0.3)
            sample_factor = min(0.3, len(session.normal_ear_samples) / 1000.0)
            score += sample_factor
            
            # 穩定性因子 (0-0.3)
            stability_factor = max(0, 0.3 - ear_std * 10)  # std 越小越好
            score += stability_factor
            
            # 眨眼檢測因子 (0-0.2)
            blink_factor = min(0.2, len(session.blink_samples) / 15.0)
            score += blink_factor
            
            # 時間因子 (0-0.2)
            duration = time.time() - session.start_time
            time_factor = min(0.2, duration / 300.0)  # 5分鐘內完成
            score += time_factor
            
            return min(1.0, score)
            
        except Exception:
            return 0.5  # 預設中等信心度
    
    def _save_driver_profile(self, profile: DriverProfile) -> bool:
        """儲存駕駛員檔案"""
        try:
            # 載入現有檔案
            profiles = load_json_file(self.profiles_file, {})
            
            # 新增或更新檔案
            profiles[profile.driver_id] = profile.to_dict()
            
            # 儲存檔案
            return save_json_file(profiles, self.profiles_file)
            
        except Exception as e:
            self.logger.error(f"儲存駕駛員檔案失敗: {e}")
            return False
    
    def _display_calibration_results(self, profile: DriverProfile):
        """顯示校準結果"""
        print(f"\n{'='*50}")
        print(f"🎉 校準完成！")
        print(f"{'='*50}")
        print(f"駕駛員: {profile.name}")
        print(f"駕駛員 ID: {profile.driver_id}")
        print(f"校準日期: {profile.calibration_date}")
        print(f"")
        print(f"📊 個人化參數:")
        print(f"   基準 EAR 值: {profile.baseline_ear:.3f}")
        print(f"   EAR 標準差: {profile.ear_std:.3f}")
        print(f"   個人化閾值: {profile.eye_closure_threshold:.3f}")
        print(f"   眨眼閾值: {profile.blink_ear_threshold:.3f}")
        print(f"")
        print(f"📈 校準品質:")
        print(f"   樣本數量: {profile.sample_count}")
        print(f"   信心度: {profile.confidence_score:.1%}")
        print(f"")
        
        # 品質評估
        if profile.confidence_score >= 0.8:
            print(f"✅ 校準品質: 優秀")
        elif profile.confidence_score >= 0.6:
            print(f"⚠️  校準品質: 良好")
        else:
            print(f"⚠️  校準品質: 一般，建議重新校準")
        
        print(f"")
        print(f"💡 提醒:")
        print(f"   - 建議每個月重新校準一次")
        print(f"   - 環境光線變化時可能需要重新校準")
        print(f"   - 如發現檢測不準確，請重新校準")
        print(f"{'='*50}")
    
    def load_driver_profile(self, driver_id: str) -> Optional[DriverProfile]:
        """載入駕駛員檔案"""
        try:
            profiles = load_json_file(self.profiles_file, {})
            
            if driver_id in profiles:
                return DriverProfile.from_dict(profiles[driver_id])
            
            return None
            
        except Exception as e:
            self.logger.error(f"載入駕駛員檔案失敗: {e}")
            return None
    
    def list_driver_profiles(self) -> List[Dict[str, Any]]:
        """列出所有駕駛員檔案"""
        try:
            profiles = load_json_file(self.profiles_file, {})
            
            return [
                {
                    'driver_id': driver_id,
                    'name': data['name'],
                    'calibration_date': data['calibration_date'],
                    'threshold': data['eye_closure_threshold'],
                    'confidence': data.get('confidence_score', 0.5),
                    'sample_count': data.get('sample_count', 0)
                }
                for driver_id, data in profiles.items()
            ]
            
        except Exception as e:
            self.logger.error(f"列出駕駛員檔案失敗: {e}")
            return []
    
    def delete_driver_profile(self, driver_id: str) -> bool:
        """刪除駕駛員檔案"""
        try:
            profiles = load_json_file(self.profiles_file, {})
            
            if driver_id in profiles:
                del profiles[driver_id]
                return save_json_file(profiles, self.profiles_file)
            
            return False
            
        except Exception as e:
            self.logger.error(f"刪除駕駛員檔案失敗: {e}")
            return False

# 如果直接執行此檔案，則進入測試模式
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        driver_name = sys.argv[1]
    else:
        driver_name = input("請輸入駕駛員姓名: ")
    
    calibration = DriverCalibration(config)
    driver_id = calibration.start_calibration(driver_name)
    
    if driver_id:
        print(f"\n✅ 校準成功！駕駛員 ID: {driver_id}")
    else:
        print(f"\n❌ 校準失敗")