# utils/camera_reader.py

import cv2

class CameraReader:
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.cap = None

    def connect(self):
        self.cap = cv2.VideoCapture(self.rtsp_url)
        if not self.cap.isOpened():
            raise Exception(f"無法連接到 IP Camera：{self.rtsp_url}")

    def read_frame(self):
        if self.cap is None:
            self.connect()
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("無法讀取影像")
        return frame

    def release(self):
        if self.cap:
            self.cap.release()
