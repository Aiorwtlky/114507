# worker.py
import cv2
import time
import os
import numpy as np
from datetime import datetime
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QImage


from event_detectors.advanced_fatigue_detector import FatigueDetector
from event_detectors.advanced_distraction_detector import DistractionDetector
# 確保您有 dummy_gpio.py
from dummy_gpio import GPIOSimulator 

class VideoWorker(QThread):
    # --- 訊號定義 ---
    change_pixmap = Signal(QImage)
    update_event_log = Signal(str)
    update_driver_status = Signal(str)

    def __init__(self, driver_camera_index=0):
        super().__init__()
        self._is_running = True
        self.driver_camera_index = driver_camera_index
        
        # --- 初始化核心模組 ---
        print("[INFO] Initializing modules...")
        self.gpio = GPIOSimulator()
        self.fatigue_detector = FatigueDetector()
        self.distraction_detector = DistractionDetector()
        print("[INFO] Modules initialized.")

        self.driver_logged_in = False
        self.current_driver = "Unknown"
        self.current_mode = 'inner'
        
        # --- 事件冷卻機制 ---
        self.event_cooldowns = {}
        self.EVENT_COOLDOWN_SECONDS = 10 # 每個事件觸發後冷卻10秒

        # --- 影像處理參數 ---
        self.PROCESSING_WIDTH = 640
        self.PROCESSING_HEIGHT = 480

    def run(self):
        print("[INFO] VideoWorker thread started.")
        
        # --- 初始化攝影機 ---
        try:
            cap_driver = cv2.VideoCapture(self.driver_camera_index)
            if not cap_driver.isOpened():
                raise IOError(f"Cannot open driver camera index {self.driver_camera_index}")
        except Exception as e:
            print(f"[ERROR] {e}")
            self.update_driver_status.emit(f"錯誤: 無法開啟攝影機 {self.driver_camera_index}")
            return

        self.update_driver_status.emit("狀態：未登入 (按 'n') | 按 'Tab' 切換模式")

        while self._is_running:
            start_time = time.time()

            # 1. 硬體事件處理
            if self.gpio.check_nfc_scan():
                self.driver_logged_in = not self.driver_logged_in
                status = "已登入" if self.driver_logged_in else "已登出"
                print(f"[INFO] Driver status changed to: {status}")
                self.update_driver_status.emit(f"狀態：駕駛 {status}")

            if self.gpio.check_mode_switch():
                # 專注於內部鏡頭，此處可先不實作
                print("[INFO] Mode switch pressed (currently only inner mode supported).")

            # 2. 檢查登入狀態
            if not self.driver_logged_in:
                # 顯示一個待機畫面
                idle_frame = np.zeros((self.PROCESSING_HEIGHT, self.PROCESSING_WIDTH, 3), dtype=np.uint8)
                cv2.putText(idle_frame, "Please Log In (Press 'n')", (100, self.PROCESSING_HEIGHT // 2), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                self.emit_frame(idle_frame)
                time.sleep(0.1)
                continue

            # 3. 讀取與預處理影像
            ret, frame = cap_driver.read()
            if not ret:
                print("[WARN] Failed to grab frame from driver camera.")
                time.sleep(0.5)
                continue
            
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (self.PROCESSING_WIDTH, self.PROCESSING_HEIGHT))

            # 4. AI 分析
            # 分心偵測優先，並取得頭部姿態數據
            distraction_events, frame, head_pose = self.distraction_detector.analyze_frame(frame)
            # 疲勞偵測使用頭部姿態數據
            fatigue_events, frame = self.fatigue_detector.analyze_frame(frame, head_pose)

            # 5. 事件處理
            all_events = distraction_events + fatigue_events
            for event_string in all_events:
                self.handle_event(event_string)

            # 6. 更新UI
            self.emit_frame(frame)
            
            # 控制幀率
            processing_time = time.time() - start_time
            sleep_time = max(0, (1/30) - processing_time)
            time.sleep(sleep_time)
            
        # --- 清理資源 ---
        cap_driver.release()
        self.gpio.stop()
        print("[INFO] VideoWorker thread finished.")

    def handle_event(self, event_string: str):
        current_time = time.time()
        event_code = event_string.split(':')[0]
        
        last_triggered = self.event_cooldowns.get(event_code, 0)
        if (current_time - last_triggered) > self.EVENT_COOLDOWN_SECONDS:
            self.event_cooldowns[event_code] = current_time
            
            timestamp = datetime.now().strftime('%H:%M:%S')
            log_message = f"[{timestamp}] {event_string}"
            
            print(f"[EVENT] {log_message}")
            self.update_event_log.emit(log_message)

    def emit_frame(self, frame):
        """將 OpenCV frame 轉換並發射給 UI"""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.change_pixmap.emit(qt_image)

    def stop(self):
        self._is_running = False
        print("[INFO] Stopping VideoWorker thread...")