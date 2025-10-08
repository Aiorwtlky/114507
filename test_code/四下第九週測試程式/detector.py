from ultralytics import YOLO

class Detector:
    def __init__(self):
        self.model = YOLO('yolov8n.pt')  # 使用Nano版，速度快

    def detect(self, frame):
        results = self.model.predict(frame, imgsz=640, conf=0.5, verbose=False)
        return results
