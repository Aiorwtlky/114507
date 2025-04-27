# utils/visualizer.py

import cv2

class Visualizer:
    def __init__(self, danger_distance=2.0):
        self.danger_distance = danger_distance

    def draw_detections(self, frame, detections):
        for det in detections:
            x1, y1, x2, y2, distance = det
            if distance < self.danger_distance:
                color = (0, 0, 255)  # 紅色
                label = f"Too Close! {distance:.2f} m"
            else:
                color = (0, 255, 0)  # 綠色
                label = f"{distance:.2f} m"

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        return frame
