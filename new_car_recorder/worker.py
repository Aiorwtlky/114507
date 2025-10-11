# worker.py (完整修正版)
"""
影像處理工作執行緒
整合 TripManager、VideoRecorder 等模組
"""

import cv2
import sys
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage
from datetime import datetime
from pathlib import Path

# ✅ 修正後的 import（使用正確的類別名稱）
from event_detectors.advanced_fatigue_detector import FatigueDetector
from event_detectors.advanced_distraction_detector import DistractionDetector
from event_detectors.presentation_adas_detector import AdasDetector

# 匯入核心模組
from core.trip_manager import TripManager
from database.local_db import LocalDatabase


class VideoWorker(QThread):
    # 訊號定義
    change_pixmap = Signal(QImage)
    update_driver_status = Signal(str)
    update_event_log = Signal(str)
    
    def __init__(self, driver_camera_index=0, road_camera_index=1):
        super().__init__()
        
        # 攝影機設定
        self.driver_camera_index = driver_camera_index
        self.road_camera_index = road_camera_index
        self.cap_driver = None
        self.cap_road = None
        
        # ✅ 偵測器（使用正確的類別名稱）
        self.fatigue_detector = FatigueDetector()
        self.distraction_detector = DistractionDetector()
        self.adas_detector = AdasDetector()
        
        # 資料庫與行程管理
        self.db = LocalDatabase()
        self.trip_manager = TripManager(self.db)
        
        # 執行緒控制
        self._run_flag = True
        self.frame_count = 0
        
        # 方向燈狀態（模擬）
        self.left_signal_on = False
        self.right_signal_on = False
        
        print("[Worker] Initialized with TripManager")
    
    def run(self):
        """執行緒主迴圈"""
        # 初始化攝影機
        self.cap_driver = cv2.VideoCapture(self.driver_camera_index)
        self.cap_road = cv2.VideoCapture(self.road_camera_index)
        
        if not self.cap_driver.isOpened():
            print("[Worker] ERROR: Cannot open driver camera")
            return
        
        if not self.cap_road.isOpened():
            print("[Worker] WARNING: Cannot open road camera, will use driver camera only")
        
        print("[Worker] Started")
        
        while self._run_flag:
            # 讀取內鏡頭（駕駛）
            ret_driver, frame_driver = self.cap_driver.read()
            if not ret_driver:
                print("[Worker] ERROR: Failed to read driver camera")
                break
            
            # 讀取外鏡頭（道路）
            ret_road, frame_road = self.cap_road.read() if self.cap_road.isOpened() else (False, None)
            
            self.frame_count += 1
            
            # === 內鏡頭處理 (A 類事件) ===
            frame_driver, driver_event = self._process_driver_camera(frame_driver)
            
            # === 外鏡頭處理 (B 類事件) ===
            if ret_road and frame_road is not None:
                frame_road, road_event = self._process_road_camera(frame_road)
                
                # 如果正在錄影，寫入外鏡頭影像
                if self.trip_manager.video_recorder.is_recording_active():
                    self.trip_manager.video_recorder.write_frame(outer_frame=frame_road)
            else:
                road_event = None
            
            # === 記錄事件到資料庫 ===
            if driver_event:
                self.trip_manager.add_event(driver_event, camera_mode='inner')
                self.update_event_log.emit(f"[內] {driver_event}")
            
            if road_event:
                self.trip_manager.add_event(road_event, camera_mode='outer')
                self.update_event_log.emit(f"[外] {road_event}")
            
            # === 更新 UI ===
            # 將內鏡頭影像轉換為 QImage 並發送訊號
            rgb_image = cv2.cvtColor(frame_driver, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.change_pixmap.emit(qt_image)
            
            # 更新駕駛狀態
            trip_info = self.trip_manager.get_current_trip_info()
            if trip_info:
                duration_min = int(trip_info['duration_seconds'] / 60)
                status = f"行程中: {trip_info['trip_number']} | 時長: {duration_min} 分鐘 | 事件: {trip_info['event_count']}"
            else:
                status = "等待刷卡開始行程..."
            self.update_driver_status.emit(status)
        
        # 清理
        self.cap_driver.release()
        if self.cap_road:
            self.cap_road.release()
        self.db.close()
        print("[Worker] Stopped")
    
    def _process_driver_camera(self, frame):
        """
        處理內鏡頭（駕駛）
        
        Returns:
            (processed_frame, event_string or None)
        """
        event = None
        
        # 疲勞偵測
        fatigue_event = self.fatigue_detector.analyze_frame(frame, self.frame_count)
        if fatigue_event:
            event = fatigue_event
        
        # 分心偵測
        distraction_events, frame, _ = self.distraction_detector.analyze_frame(frame)
        if distraction_events and not event:  # 避免重複
            event = distraction_events[0]  # 取第一個事件
        
        return frame, event
    
    def _process_road_camera(self, frame):
        """
        處理外鏡頭（道路）
        
        Returns:
            (processed_frame, event_string or None)
        """
        event, frame = self.adas_detector.analyze_frame(
            frame, 
            self.frame_count,
            self.left_signal_on,
            self.right_signal_on
        )
        
        return frame, event
    
    def start_trip(self, nfc_uid: str, user_info: dict):
        """
        開始行程
        
        Args:
            nfc_uid: NFC UID
            user_info: 使用者資訊
        """
        trip_id = self.trip_manager.start_trip(nfc_uid, user_info)
        if trip_id:
            self.update_event_log.emit(f"✅ 行程開始: {user_info.get('username', 'Unknown')}")
        else:
            self.update_event_log.emit("❌ 行程開始失敗（可能已有進行中的行程）")
    
    def end_trip(self):
        """結束行程"""
        result = self.trip_manager.end_trip()
        if result:
            self.update_event_log.emit(f"✅ 行程結束")
            self.update_event_log.emit(f"   總分: {result['score']:.2f}")
            self.update_event_log.emit(f"   車內: {result['in_car_score']:.2f} | 車外: {result['out_car_score']:.2f}")
        else:
            self.update_event_log.emit("❌ 沒有進行中的行程")
    
    def stop(self):
        """停止執行緒"""
        self._run_flag = False
        print("[Worker] Stopping...")