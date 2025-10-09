# main_window.py
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                               QVBoxLayout, QHBoxLayout, QTextEdit)
from PySide6.QtGui import QPixmap, QImage, QFont
from PySide6.QtCore import Qt, QThread, Signal

from worker import VideoWorker # 確保 worker.py 在同一個資料夾

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("吾駕仙 - AI 駕駛行為分析模擬器")
        self.setGeometry(100, 100, 1100, 800)

        # --- UI 元件 ---
        self.video_label = QLabel("正在初始化攝影機...")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: black; color: white;")
        
        self.status_label = QLabel("狀態：初始化中...")
        self.status_label.setFont(QFont("Arial", 14))
        
        self.log_label = QLabel("即時事件紀錄:")
        self.log_label.setFont(QFont("Arial", 12))
        
        self.event_log = QTextEdit()
        self.event_log.setReadOnly(True)
        self.event_log.setFont(QFont("Consolas", 11))
        self.event_log.setMaximumHeight(200) # 限制紀錄區塊的高度

        # --- 佈局 ---
        # 右側資訊面板
        right_panel_layout = QVBoxLayout()
        right_panel_layout.addWidget(self.status_label)
        right_panel_layout.addWidget(self.log_label)
        right_panel_layout.addWidget(self.event_log)
        right_panel_layout.setContentsMargins(10, 10, 10, 10)
        
        right_panel_widget = QWidget()
        right_panel_widget.setLayout(right_panel_layout)
        right_panel_widget.setFixedWidth(400)

        # 主佈局
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.video_label, 1) # 影像佔用更大比例
        main_layout.addWidget(right_panel_widget)
        
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # --- 啟動背景執行緒 ---
        self.init_worker_thread()

    def init_worker_thread(self):
        """初始化並啟動影像處理執行緒"""
        self.worker = VideoWorker(driver_camera_index=0)
        
        # 連接新版的訊號到對應的 UI 更新函式
        self.worker.change_pixmap.connect(self.set_image)
        self.worker.update_driver_status.connect(self.set_driver_status)
        self.worker.update_event_log.connect(self.add_to_log)
        
        self.worker.start()
        print("[INFO] Worker thread started from main window.")

    # --- Slot 函式 (用來接收訊號) ---
    def set_image(self, image: QImage):
        """更新視訊畫面"""
        self.video_label.setPixmap(QPixmap.fromImage(image))

    def set_driver_status(self, text: str):
        """更新駕駛員狀態標籤"""
        self.status_label.setText(text)

    def add_to_log(self, message: str):
        """在事件紀錄中新增一筆訊息"""
        self.event_log.append(message)
        self.event_log.verticalScrollBar().setValue(self.event_log.verticalScrollBar().maximum()) # 自動滾動到底部

    def closeEvent(self, event):
        """當視窗被關閉時，安全地停止背景執行緒"""
        print("[INFO] Closing application...")
        if self.worker.isRunning():
            self.worker.stop()
            self.worker.wait() # 等待執行緒完全結束
        event.accept()

# --- 主程式進入點 ---
if __name__ == '__main__':
    # 確保您有 main.py，或者直接由此處執行
    from main import main # 假設 main.py 裡有 main() 函式
    main()