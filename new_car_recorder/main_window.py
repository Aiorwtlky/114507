# main_window.py (改良版)
"""
主視窗 UI
顯示影像、行程狀態、事件記錄
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, 
    QHBoxLayout, QTextEdit, QPushButton, QGroupBox
)
from PySide6.QtGui import QPixmap, QImage, QFont
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from worker import VideoWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("吾駕仙 - AI 駕駛行為分析系統")
        self.setGeometry(100, 100, 1400, 900)
        
        # === 建立 UI 元件 ===
        self._create_widgets()
        self._create_layout()
        
        # === 啟動 Worker ===
        self.init_worker_thread()
        
        # === 定時更新行程資訊 ===
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_trip_display)
        self.update_timer.start(1000)  # 每秒更新一次
    
    def _create_widgets(self):
        """建立所有 UI 元件"""
        # --- 影像顯示區 ---
        self.video_label = QLabel("正在初始化攝影機...")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: black; color: white; border: 2px solid #333;")
        self.video_label.setMinimumSize(800, 600)
        
        # --- 行程資訊區 ---
        self.trip_status_label = QLabel("等待刷卡開始行程...")
        self.trip_status_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.trip_status_label.setStyleSheet("color: #FF6B35; padding: 10px;")
        
        self.trip_number_label = QLabel("行程編號: --")
        self.trip_duration_label = QLabel("行程時長: --")
        self.trip_events_label = QLabel("事件數量: --")
        self.trip_recording_label = QLabel("錄影狀態: --")
        
        for label in [self.trip_number_label, self.trip_duration_label, 
                      self.trip_events_label, self.trip_recording_label]:
            label.setFont(QFont("Arial", 11))
            label.setStyleSheet("padding: 5px;")
        
        # --- 評分顯示區 ---
        self.score_label = QLabel("總分: --")
        self.score_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.score_label.setStyleSheet("color: #4ECDC4; padding: 10px;")
        
        self.in_car_score_label = QLabel("車內: --")
        self.out_car_score_label = QLabel("車外: --")
        
        for label in [self.in_car_score_label, self.out_car_score_label]:
            label.setFont(QFont("Arial", 12))
            label.setStyleSheet("padding: 5px;")
        
        # --- 事件記錄區 ---
        self.log_title = QLabel("即時事件記錄:")
        self.log_title.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.event_log = QTextEdit()
        self.event_log.setReadOnly(True)
        self.event_log.setFont(QFont("Consolas", 10))
        self.event_log.setMaximumHeight(250)
        self.event_log.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #00ff00;
                border: 1px solid #333;
            }
        """)
        
        # --- 控制按鈕區 ---
        self.simulate_nfc_btn = QPushButton("🧪 模擬刷卡")
        self.simulate_nfc_btn.setFont(QFont("Arial", 11))
        self.simulate_nfc_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6B35;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #FF8C61;
            }
        """)
        self.simulate_nfc_btn.clicked.connect(self.on_simulate_nfc_clicked)
        
        self.clear_log_btn = QPushButton("🗑️ 清除記錄")
        self.clear_log_btn.setFont(QFont("Arial", 11))
        self.clear_log_btn.setStyleSheet("""
            QPushButton {
                background-color: #555;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)
        self.clear_log_btn.clicked.connect(self.event_log.clear)
    
    def _create_layout(self):
        """建立佈局"""
        # === 右側資訊面板 ===
        right_panel = QVBoxLayout()
        
        # 行程資訊群組
        trip_group = QGroupBox("📊 行程資訊")
        trip_group.setFont(QFont("Arial", 12, QFont.Bold))
        trip_layout = QVBoxLayout()
        trip_layout.addWidget(self.trip_status_label)
        trip_layout.addWidget(self.trip_number_label)
        trip_layout.addWidget(self.trip_duration_label)
        trip_layout.addWidget(self.trip_events_label)
        trip_layout.addWidget(self.trip_recording_label)
        trip_group.setLayout(trip_layout)
        
        # 評分資訊群組
        score_group = QGroupBox("🏆 評分")
        score_group.setFont(QFont("Arial", 12, QFont.Bold))
        score_layout = QVBoxLayout()
        score_layout.addWidget(self.score_label)
        score_layout.addWidget(self.in_car_score_label)
        score_layout.addWidget(self.out_car_score_label)
        score_group.setLayout(score_layout)
        
        # 事件記錄群組
        log_group = QGroupBox("📝 事件記錄")
        log_group.setFont(QFont("Arial", 12, QFont.Bold))
        log_layout = QVBoxLayout()
        log_layout.addWidget(self.event_log)
        log_group.setLayout(log_layout)
        
        # 控制按鈕
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.simulate_nfc_btn)
        button_layout.addWidget(self.clear_log_btn)
        
        # 組合右側面板
        right_panel.addWidget(trip_group)
        right_panel.addWidget(score_group)
        right_panel.addWidget(log_group)
        right_panel.addLayout(button_layout)
        right_panel.addStretch()
        
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        right_widget.setFixedWidth(450)
        
        # === 主佈局 ===
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.video_label, 1)
        main_layout.addWidget(right_widget)
        
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # 設定整體樣式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c2c2c;
            }
            QGroupBox {
                background-color: #3a3a3a;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #fff;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #fff;
            }
        """)
    
    def init_worker_thread(self):
        """初始化並啟動影像處理執行緒"""
        self.worker = VideoWorker(driver_camera_index=0, road_camera_index=1)
        
        # 連接訊號
        self.worker.change_pixmap.connect(self.set_image)
        self.worker.update_driver_status.connect(self.update_status)
        self.worker.update_event_log.connect(self.add_to_log)
        
        self.worker.start()
        print("[MainWindow] Worker thread started")
    
    def update_trip_display(self):
        """定時更新行程資訊顯示"""
        if not hasattr(self, 'worker') or not self.worker.trip_manager:
            return
        
        trip_info = self.worker.trip_manager.get_current_trip_info()
        
        if trip_info:
            # 有進行中的行程
            self.trip_status_label.setText("🚗 行程進行中")
            self.trip_status_label.setStyleSheet("color: #4ECDC4; padding: 10px;")
            
            self.trip_number_label.setText(f"行程編號: {trip_info['trip_number']}")
            
            duration_min = int(trip_info['duration_seconds'] / 60)
            duration_sec = int(trip_info['duration_seconds'] % 60)
            self.trip_duration_label.setText(f"行程時長: {duration_min:02d}:{duration_sec:02d}")
            
            self.trip_events_label.setText(f"事件數量: {trip_info['event_count']}")
            
            recording_status = "🔴 錄影中" if trip_info['is_recording'] else "⚫ 未錄影"
            self.trip_recording_label.setText(f"錄影狀態: {recording_status}")
        else:
            # 無進行中的行程
            self.trip_status_label.setText("⏸️ 等待刷卡開始行程...")
            self.trip_status_label.setStyleSheet("color: #FF6B35; padding: 10px;")
            
            self.trip_number_label.setText("行程編號: --")
            self.trip_duration_label.setText("行程時長: --")
            self.trip_events_label.setText("事件數量: --")
            self.trip_recording_label.setText("錄影狀態: --")
    
    # === Slot 函式 ===
    
    def set_image(self, image: QImage):
        """更新視訊畫面"""
        self.video_label.setPixmap(QPixmap.fromImage(image).scaled(
            self.video_label.size(), 
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
    
    def update_status(self, text: str):
        """更新狀態（此方法可能不再需要，因為我們用定時器更新）"""
        pass
    
    def add_to_log(self, message: str):
        """在事件記錄中新增一筆訊息"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.event_log.append(f"[{timestamp}] {message}")
        
        # 自動滾動到底部
        scrollbar = self.event_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # 如果是行程結束，更新評分顯示
        if "行程結束" in message:
            self.update_score_display()
    
    def update_score_display(self):
        """更新評分顯示（從最後一次行程）"""
        # TODO: 從資料庫讀取最後一次行程的評分
        # 這裡先用 Worker 傳來的資訊
        pass
    
    def on_simulate_nfc_clicked(self):
        """模擬 NFC 刷卡按鈕點擊"""
        # 觸發主程式中的 GPIO 模擬
        if hasattr(self, '_gpio_handler'):
            self._gpio_handler.simulate_nfc_scan("TEST:AA:BB:CC:DD")
        else:
            self.add_to_log("⚠️ GPIO Handler 尚未初始化")
    
    def set_gpio_handler(self, gpio_handler):
        """設定 GPIO Handler（從 main.py 傳入）"""
        self._gpio_handler = gpio_handler
    
    def closeEvent(self, event):
        """當視窗被關閉時，安全地停止背景執行緒"""
        print("[MainWindow] Closing application...")
        
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()
        
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(5000)  # 等待最多 5 秒
        
        event.accept()


# === 測試用主程式 ===
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())