# services/external_camera_ai.py（加強版）

import cv2
import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.lane_departure_detector import LaneDepartureDetector
from utils.vehicle_distance_detector import VehicleDistanceDetector
from utils.traffic_light_detector_final import TrafficLightDetectorFinal
from models import db, EventLogLocal, TripLog
from app import app

class ExternalCameraService:
    """外鏡頭 AI 獨立服務"""
    
    def __init__(self):
        print("載入外鏡頭 AI 模型...")
        self.lane_detector = LaneDepartureDetector()
        self.vehicle_detector = VehicleDistanceDetector()
        self.traffic_detector = TrafficLightDetectorFinal()
        print("✅ 模型載入完成")
        
        self.current_trip_id = None
        
        # ✅ 事件節流（B01/B02/B03 可重複觸發，但有冷卻時間）
        self.last_events = {
            'lane_departure': 0,        # B01
            'too_close': 0,            # B02
            'red_light_violation': 0   # B03
        }
        
        self.cooldown = {
            'lane_departure': 5,        # 5 秒
            'too_close': 3,            # 3 秒
            'red_light_violation': 5   # 5 秒
        }
    
    def check_active_trip(self):
        """檢查行程狀態"""
        with app.app_context():
            active_trip = TripLog.query.filter_by(status='ongoing').first()
            
            if active_trip:
                if self.current_trip_id != active_trip.id:
                    # 新行程，重置計時器
                    self.reset_timers()
                
                self.current_trip_id = active_trip.id
                return True
            else:
                self.current_trip_id = None
                return False
    
    def reset_timers(self):
        """重置計時器"""
        for key in self.last_events:
            self.last_events[key] = 0
    
    def create_event(self, event_type):
        """建立事件（含節流）"""
        current_time = time.time()
        
        # ✅ 檢查冷卻時間
        if current_time - self.last_events[event_type] < self.cooldown[event_type]:
            return False
        
        with app.app_context():
            event = EventLogLocal(
                trip_id=self.current_trip_id,
                event_type=event_type
            )
            db.session.add(event)
            db.session.commit()
            print(f"[{event_type}] 事件已記錄")
        
        self.last_events[event_type] = current_time
        return True
    
    def run(self):
        """主執行迴圈"""
        print("外鏡頭 AI 服務啟動...")
        
        cap = cv2.VideoCapture(1)  # 外鏡頭
        if not cap.isOpened():
            print("❌ 無法開啟外鏡頭")
            return
        
        print("✅ 外鏡頭已開啟，等待行程開始...")
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            
            frame_count += 1
            
            # 檢查行程狀態
            if frame_count % 30 == 0:
                if not self.check_active_trip():
                    cv2.putText(frame, "Waiting for trip...", (50, 50),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    cv2.imshow('External Camera AI', frame)
                    cv2.waitKey(1)
                    time.sleep(1)
                    continue
            
            # ✅ 只在有行程時執行偵測
            if self.current_trip_id:
                # B01: 車道偏離（每幀）
                lane_result = self.lane_detector.detect(frame)
                if lane_result['departed']:
                    self.create_event('lane_departure')
                
                # B02: 前車距離（每 3 幀，降低 CPU）
                if frame_count % 3 == 0:
                    vehicle_result = self.vehicle_detector.detect(frame, speed_kmh=50)
                    if vehicle_result['too_close']:
                        self.create_event('too_close')
                
                # B03: 紅綠燈（每 2 幀，降低 CPU）
                if frame_count % 2 == 0:
                    traffic_result = self.traffic_detector.detect(frame)
                    if traffic_result['red_light_violation']:
                        self.create_event('red_light_violation')
                
                # 顯示狀態
                cv2.putText(frame, f"Trip: {self.current_trip_id}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow('External Camera AI', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    service = ExternalCameraService()
    service.run()