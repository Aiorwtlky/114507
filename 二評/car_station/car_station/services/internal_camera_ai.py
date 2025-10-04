# services/internal_camera_ai.py（修正版）

import cv2
import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.drowsiness_detector import PersonalizedDrowsinessDetector
from models import db, EventLogLocal, TripLog
from app import app

class InternalCameraService:
    """內鏡頭 AI 獨立服務（修正版）"""
    
    def __init__(self):
        self.detector = None
        self.current_trip_id = None
        self.current_driver_id = None
        
        # ✅ 事件觸發狀態管理
        self.event_triggered = {
            'drowsy_severe': False,    # A01
            'drowsy_moderate': False,  # A02
            'yawning': False,          # A03
            'no_face': False           # A04
        }
        
        # ✅ 上次觸發時間（用於冷卻）
        self.last_event_time = {
            'drowsy_severe': 0,
            'drowsy_moderate': 0,
            'yawning': 0,
            'no_face': 0
        }
        
        # 事件冷卻時間（秒）
        self.cooldown = {
            'drowsy_severe': 60,    # A01: 1 分鐘
            'drowsy_moderate': 30,  # A02: 30 秒
            'yawning': 60,          # A03: 1 分鐘
            'no_face': 10           # A04: 10 秒
        }
    
    def check_active_trip(self):
        """檢查是否有進行中的行程"""
        with app.app_context():
            active_trip = TripLog.query.filter_by(status='ongoing').first()
            
            if active_trip:
                # ✅ 如果是新行程，重置觸發狀態
                if self.current_trip_id != active_trip.id:
                    self.reset_event_states()
                
                self.current_trip_id = active_trip.id
                self.current_driver_id = active_trip.driver_id
                return True
            else:
                self.current_trip_id = None
                self.current_driver_id = None
                self.detector = None  # 清除偵測器
                return False
    
    def reset_event_states(self):
        """重置事件觸發狀態"""
        for key in self.event_triggered:
            self.event_triggered[key] = False
            self.last_event_time[key] = 0
    
    def create_event(self, event_type):
        """建立事件到資料庫（含冷卻機制）"""
        current_time = time.time()
        
        # ✅ 檢查冷卻時間
        if current_time - self.last_event_time[event_type] < self.cooldown[event_type]:
            return False
        
        # ✅ 檢查是否已觸發（單次觸發事件）
        if event_type in ['drowsy_severe', 'drowsy_moderate', 'yawning']:
            if self.event_triggered[event_type]:
                return False
        
        with app.app_context():
            event = EventLogLocal(
                trip_id=self.current_trip_id,
                event_type=event_type,
                driver_id=self.current_driver_id
            )
            db.session.add(event)
            db.session.commit()
            
            print(f"[{event_type}] 事件已記錄")
            
            # ✅ 更新狀態
            self.event_triggered[event_type] = True
            self.last_event_time[event_type] = current_time
            
            return True
    
    def run(self):
        """主執行迴圈"""
        print("內鏡頭 AI 服務啟動...")
        
        cap = cv2.VideoCapture(0)  # 內鏡頭
        if not cap.isOpened():
            print("❌ 無法開啟內鏡頭")
            return
        
        print("✅ 內鏡頭已開啟，等待行程開始...")
        
        frame_count = 0
        calibration_frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            
            frame_count += 1
            
            # 每 30 幀檢查一次行程狀態
            if frame_count % 30 == 0:
                if not self.check_active_trip():
                    # 沒有行程，等待
                    cv2.putText(frame, "Waiting for trip...", (50, 50),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    cv2.imshow('Internal Camera AI', frame)
                    cv2.waitKey(1)
                    time.sleep(1)
                    continue
                
                # 有行程但沒偵測器，初始化
                if self.detector is None:
                    print(f"初始化偵測器（駕駛員: {self.current_driver_id}）")
                    self.detector = PersonalizedDrowsinessDetector(
                        driver_id=self.current_driver_id
                    )
                    calibration_frame_count = 0
            
            # ✅ 如果有偵測器，執行偵測
            if self.detector:
                # 校準階段
                if not self.detector.is_calibrated:
                    calibration_frame_count += 1
                    result = self.detector.calibrate(frame)
                    
                    # 顯示校準進度
                    cv2.putText(frame, f"Calibrating: {calibration_frame_count}/30", 
                               (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    
                    if result and result.get('calibration_complete'):
                        print("✅ 校準完成")
                        print(f"   Baseline EAR: {self.detector.baseline_ear:.3f}")
                        print(f"   Baseline MAR: {self.detector.baseline_mar:.3f}")
                else:
                    # ✅ 偵測階段
                    result = self.detector.detect(frame)
                    
                    # 觸發事件
                    if result['event_type']:
                        self.create_event(result['event_type'])
                    
                    # 顯示狀態
                    status_text = f"Trip: {self.current_trip_id} | Driver: {self.current_driver_id}"
                    cv2.putText(frame, status_text, (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
                    # 顯示 EAR/MAR
                    cv2.putText(frame, f"EAR: {result['ear']:.3f}", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    cv2.putText(frame, f"MAR: {result['mar']:.3f}", (10, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    # 顯示事件狀態
                    if result['event_type']:
                        event_map = {
                            'drowsy_severe': 'A01: SEVERE DROWSY',
                            'drowsy_moderate': 'A02: MODERATE DROWSY',
                            'yawning': 'A03: YAWNING',
                            'no_face': 'A04: NO FACE'
                        }
                        cv2.putText(frame, event_map.get(result['event_type'], ''), 
                                   (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            
            cv2.imshow('Internal Camera AI', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    service = InternalCameraService()
    service.run()