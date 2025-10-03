# blueprints/external_camera.py

import cv2
import threading
import time
from utils.lane_departure_detector import LaneDepartureDetector
from utils.db_helper import LocalEventHelper
from blueprints.gpio import get_turn_signal_status

class ExternalCameraMonitor:
    """外鏡頭監控管理器"""
    
    def __init__(self, camera_index=1):
        self.camera_index = camera_index
        self.lane_detector = LaneDepartureDetector(skip_undistort=True)
        
        self.active = False
        self.thread = None
        self.cap = None
        
        # B01 事件節流
        self.last_b01_time = 0
        self.b01_cooldown = 10  # 10 秒內不重複觸發
        
    def start(self, trip_id):
        """啟動監控"""
        if self.active:
            print("[External Camera] Already running")
            return
        
        self.active = True
        self.thread = threading.Thread(
            target=self._monitoring_worker,
            args=(trip_id,),
            daemon=True
        )
        self.thread.start()
        print(f"[External Camera] Started for trip {trip_id}")
    
    def stop(self):
        """停止監控"""
        self.active = False
        if self.thread:
            self.thread.join(timeout=5)
        if self.cap:
            self.cap.release()
        print("[External Camera] Stopped")
    
    def _monitoring_worker(self, trip_id):
        """監控執行緒"""
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            print("[External Camera] Failed to open camera")
            return
        
        print("[External Camera] Worker started")
        
        while self.active:
            ret, frame = self.cap.read()
            if not ret:
                print("[External Camera] Failed to read frame")
                time.sleep(1)
                continue
            
            # B01: 車道偵測
            self._check_lane_departure(frame, trip_id)
            
            time.sleep(0.1)  # 10 FPS
        
        self.cap.release()
        print("[External Camera] Worker stopped")
    
    def _check_lane_departure(self, frame, trip_id):
        """檢查車道偏離 (B01)"""
        # 偵測車道
        result = self.lane_detector.detect(frame)
        
        if not result['departed']:
            return
        
        # 檢查方向燈
        turn_signal = get_turn_signal_status()  # GPIO 讀取
        
        # 如果打了方向燈，就不算偏離
        if turn_signal['left'] or turn_signal['right']:
            print(f"[B01] Lane departure detected but turn signal ON")
            return
        
        # 節流檢查
        current_time = time.time()
        if current_time - self.last_b01_time < self.b01_cooldown:
            return
        
        # 觸發 B01 事件
        print(f"[B01] Lane Departure! Offset: {result['offset']:.2f}m")
        
        LocalEventHelper.create_event(
            trip_id=trip_id,
            event_type='lane_departure',
            event_data={
                'offset': result['offset'],
                'direction': result['direction']
            }
        )
        
        self.last_b01_time = current_time