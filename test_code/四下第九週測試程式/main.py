from camera import Camera
from detector import Detector
from ui import draw_detections
import cv2

def main():
    cam = Camera()
    detector = Detector()

    while True:
        frame = cam.get_frame()
        if frame is None:
            print("❌ 無法讀取影像，退出。")
            break

        results = detector.detect(frame)
        annotated_frame = draw_detections(frame, results)

        cv2.imshow('YOLOv8 - USB Camera Test', annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
