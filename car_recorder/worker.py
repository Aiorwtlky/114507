# worker.py
import cv2
import time
import numpy as np
import os
from datetime import datetime
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QImage

# --- 本地模組匯入 ---
# 根據您提供的檔案，匯入對應的類別
from event_detectors.advanced_fatigue_detector import FatigueDetector
from event_detectors.advanced_distration_detector import DistractionDetector
from event_detectors.advanced_adas_detector import AdasDetector

from dummy_gpio import GPIOSimulator
from utils.api_client import ApiClient
from local_database import LocalDatabase

# UploaderWorker 執行緒 (為了 Demo 穩定，保持低度活動)
class UploaderWorker(QThread):
    def __init__(self, db, api_client):
        super().__init__()
        self.db = db
        self.api = api_client
        self._is_running = True

    def run(self):
        print("[Uploader] Background uploader started (in standby mode for demo).")
        while self._is_running:
            time.sleep(30) # 發表會期間不執行上傳，只休眠
            
    def stop(self):
        self._is_running = False

# --- VideoWorker 執行緒 ---
class VideoWorker(QThread):
    # 訊號定義
    change_pixmap = Signal(QImage)
    update_suggestion_inner = Signal(str)
    update_suggestion_outer = Signal(str)
    update_driver_status = Signal(str)
    finished = Signal()

    def __init__(self, road_video_path):
        super().__init__()
        self.road_video_path = road_video_path
        self.driver_camera_index = 0
        self._is_running = True
        
        # 初始化所有模組
        self.gpio = GPIOSimulator()
        self.api = ApiClient(mock_mode=True)
        self.db = LocalDatabase()
        
        print("Initializing AI Detectors from your final files...")
        self.fatigue_detector = FatigueDetector()
        self.distraction_detector = DistractionDetector()
        self.adas_detector = AdasDetector()
        print("AI Detectors Initialized.")

        self.uploader_thread = UploaderWorker(self.db, self.api)
        
        self.cache_dir = "upload_queue_videos"
        os.makedirs(self.cache_dir, exist_ok=True)

        self.driver_logged_in = False
        self.current_driver = "Unknown"
        
        self.current_mode = 'inner' # 預設為內部鏡頭模式
        self.event_cooldowns = {}
        self.EVENT_COOLDOWN_SECONDS = 10

    def run(self):
        # self.uploader_thread.start() # 發表會期間建議保持註解
        
        cap_road = cv2.VideoCapture(self.road_video_path)
        cap_driver = cv2.VideoCapture(self.driver_camera_index)
        
        if not cap_road.isOpened() or not cap_driver.isOpened():
            print(f"錯誤: 無法開啟影像來源 (road: {cap_road.isOpened()}, driver: {cap_driver.isOpened()})。")
            self.finished.emit()
            return

        frame_count = 0
        self.update_driver_status.emit("狀態：未登入 (按 'n') | 按 'Tab' 切換模式")

        while self._is_running:
            # 硬體事件處理
            if self.gpio.check_nfc_scan():
                self.driver_logged_in = not self.driver_logged_in
                if self.driver_logged_in:
                    self.current_driver = "Driver_1013"
                    self.api.start_trip(self.current_driver, "Demo_Car")
                    self.update_driver_status.emit(f"駕駛 {self.current_driver} 已登入")
                else:
                    self.api.end_trip()
                    self.update_driver_status.emit("狀態：駕駛已登出")
            
            if self.gpio.check_mode_switch():
                self.current_mode = 'outer' if self.current_mode == 'inner' else 'inner'
                if self.current_mode == 'outer': cap_road.set(cv2.CAP_PROP_POS_FRAMES, 0)
                print(f"--- Switched to {self.current_mode.upper()} MODE ---")

            if not self.driver_logged_in:
                time.sleep(0.1)
                continue

            # 根據模式執行對應 AI 引擎
            display_frame = None
            if self.current_mode == 'inner':
                ret, frame = cap_driver.read()
                if not ret: continue
                frame = cv2.flip(frame, 1)
                
                # 依序執行內部偵測
                distraction_event, display_frame = self.distraction_detector.analyze_frame(frame, frame_count)
                if distraction_event: self.handle_event(distraction_event, frame, 'inner')
                
                fatigue_event, display_frame = self.fatigue_detector.analyze_frame(display_frame, frame_count)
                if fatigue_event: self.handle_event(fatigue_event, frame, 'inner')

            else: # 'outer' mode
                ret, frame = cap_road.read()
                if not ret: 
                    cap_road.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                
                adas_event, display_frame = self.adas_detector.analyze_frame(
                    frame, frame_count, self.gpio.is_left_on(), self.gpio.is_right_on()
                )
                if adas_event: self.handle_event(adas_event, frame, 'outer')

            # 更新 UI
            if display_frame is not None:
                final_frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                h, w, ch = final_frame_rgb.shape
                qt_image = QImage(final_frame_rgb.data, w, h, w * ch, QImage.Format_RGB888)
                self.change_pixmap.emit(qt_image.scaled(1024, 768, Qt.AspectRatioMode.KeepAspectRatio))
            
            time.sleep(1 / 30)
            frame_count += 1
            
        # 清理資源
        cap_road.release()
        cap_driver.release()
        self.gpio.stop()
        if self.uploader_thread.isRunning():
            self.uploader_thread.stop()
            self.uploader_thread.wait()
        self.db.close()
        self.finished.emit()
        print("Worker thread finished.")

    def handle_event(self, event_string: str, frame, event_type: str):
        current_time = time.time()
        # 穩定地從 "A01 重度疲勞(...)" 中提取出 "A01"
        event_code = event_string.split(' ')[0]
        
        last_triggered_time = self.event_cooldowns.get(event_code)
        if last_triggered_time and (current_time - last_triggered_time < self.EVENT_COOLDOWN_SECONDS):
            return

        print(f"--- Event ({event_type.upper()}) --- : {event_string}")
        self.event_cooldowns[event_code] = current_time

        if event_type == 'inner':
            self.update_suggestion_inner.emit(event_string)
        elif event_type == 'outer':
            self.update_suggestion_outer.emit(event_string)

        # 離線暫存邏輯
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        media_filename = f"{timestamp_str}_{event_code}.jpg"
        local_media_path = os.path.join(self.cache_dir, media_filename)
        cv2.imwrite(local_media_path, frame)
        if self.driver_logged_in:
            self.db.add_event(event_string, self.current_driver, local_media_path)

    def stop(self):
        self._is_running = False