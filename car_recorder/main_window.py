# main_window.py
import sys
import configparser
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QApplication
from PySide6.QtCore import Qt, Slot, QTimer, QThread
from PySide6.QtGui import QFont, QPixmap, QImage
from worker import VideoWorker

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.video_path = config['DataSource']['road_video_path']
        self.init_ui()
        self.init_worker_thread()

    def init_ui(self):
        self.setWindowTitle("吾駕仙 - AI 駕駛監控系統 (智慧切換模式)")
        self.setGeometry(100, 100, 1024, 768)
        self.setStyleSheet("background-color: #1c1c1c;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.video_label = QLabel("系統啟動中... 按 'Tab' 切換內/外模式 | 按 'n' 登入", self)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.video_label.setStyleSheet("background-color: black; color: #cccccc;")
        main_layout.addWidget(self.video_label, 90)

        bottom_bar_layout = QHBoxLayout()
        bottom_bar_layout.setSpacing(0)
        
        self.suggestion_label_inner = QLabel("--- 內部偵測 ---", self)
        self.suggestion_label_outer = QLabel("--- 外部偵測 ---", self)
        self.driver_status_label = QLabel("狀態：未登入", self)

        for label in [self.suggestion_label_inner, self.suggestion_label_outer]:
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFont(QFont("Arial", 14, QFont.Bold))
            label.setStyleSheet("background-color: #2c3e50; color: #ecf0f1; padding: 10px; border: 1px solid #40576d;")

        self.driver_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.driver_status_label.setFont(QFont("Arial", 12))
        self.driver_status_label.setStyleSheet("background-color: #34495e; color: white; padding: 10px; border-right: 1px solid #40576d; border-left: 1px solid #40576d;")
        
        bottom_bar_layout.addWidget(self.suggestion_label_inner, 40)
        bottom_bar_layout.addWidget(self.driver_status_label, 20)
        bottom_bar_layout.addWidget(self.suggestion_label_outer, 40)
        main_layout.addLayout(bottom_bar_layout, 10)

        self.timer_inner = QTimer(self)
        self.timer_inner.setSingleShot(True)
        self.timer_inner.timeout.connect(self.reset_suggestion_inner)

        self.timer_outer = QTimer(self)
        self.timer_outer.setSingleShot(True)
        self.timer_outer.timeout.connect(self.reset_suggestion_outer)

    def init_worker_thread(self):
        self.thread = QThread()
        self.worker = VideoWorker(self.video_path)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.worker.change_pixmap.connect(self.set_image)
        self.worker.update_driver_status.connect(self.set_driver_status)
        self.worker.update_suggestion_inner.connect(self.set_suggestion_inner)
        self.worker.update_suggestion_outer.connect(self.set_suggestion_outer)

        self.thread.start()

    @Slot(QImage)
    def set_image(self, image: QImage):
        self.video_label.setPixmap(QPixmap.fromImage(image))

    @Slot(str)
    def set_suggestion_inner(self, text: str):
        self.suggestion_label_inner.setText(text)
        self.suggestion_label_inner.setStyleSheet("background-color: #c0392b; color: white; padding: 10px; border: 1px solid #40576d;")
        self.timer_inner.start(5000)

    @Slot(str)
    def set_suggestion_outer(self, text: str):
        self.suggestion_label_outer.setText(text)
        self.suggestion_label_outer.setStyleSheet("background-color: #e67e22; color: white; padding: 10px; border: 1px solid #40576d;")
        self.timer_outer.start(5000)

    def reset_suggestion_inner(self):
        self.suggestion_label_inner.setText("--- 內部偵測 ---")
        self.suggestion_label_inner.setStyleSheet("background-color: #2c3e50; color: #ecf0f1; padding: 10px; border: 1px solid #40576d;")
        
    def reset_suggestion_outer(self):
        self.suggestion_label_outer.setText("--- 外部偵測 ---")
        self.suggestion_label_outer.setStyleSheet("background-color: #2c3e50; color: #ecf0f1; padding: 10px; border: 1px solid #40576d;")
        
    @Slot(str)
    def set_driver_status(self, text: str):
        self.driver_status_label.setText(text)

    def closeEvent(self, event):
        print("Closing application...")
        if self.thread.isRunning():
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()
        event.accept()