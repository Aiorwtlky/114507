# main.py

import cv2
from ultralytics import YOLO
from utils.camera_reader import CameraReader
from utils.distance_estimator import DistanceEstimator
from utils.visualizer import Visualizer
from utils.logger import WarningLogger

def main():
    # ====== 1. 定義三個鏡頭的RTSP路徑 ======
    front_rtsp_url = "rtsp://admin:123456@192.168.1.10/stream1"
    center_rtsp_url = "rtsp://admin:123456@192.168.1.11/stream1"
    rear_rtsp_url = "rtsp://admin:123456@192.168.1.12/stream1"

    # ====== 2. 初始化 Camera ======
    front_camera = CameraReader(front_rtsp_url)
    center_camera = CameraReader(center_rtsp_url)
    rear_camera = CameraReader(rear_rtsp_url)

    # ====== 3. 初始化 YOLOv8n 模型 ======
    model = YOLO("yolov8n.pt")
    class_ids_of_interest = [2, 5, 7]  # car, bus, truck

    # ====== 4. 初始化 Estimator / Visualizer / Logger ======
    front_estimator = DistanceEstimator()
    center_estimator = DistanceEstimator()
    rear_estimator = DistanceEstimator()

    front_visualizer = Visualizer(danger_distance=2.0)
    center_visualizer = Visualizer(danger_distance=2.0)
    rear_visualizer = Visualizer(danger_distance=1.5)

    logger = WarningLogger()

    # ====== 5. 啟動連線 ======
    front_camera.connect()
    center_camera.connect()
    rear_camera.connect()

    try:
        while True:
            front_frame = front_camera.read_frame()
            center_frame = center_camera.read_frame()
            rear_frame = rear_camera.read_frame()

            danger_detected = False  # 每輪一開始都假設安全

            # ====== 前鏡頭推論 ======
            front_results = model.predict(source=front_frame, verbose=False)[0]
            front_detections = process_results(front_results, front_estimator, class_ids_of_interest)
            for det in front_detections:
                if det[4] < 2.0:
                    logger.log_warning("Front Camera", det[4])
                    danger_detected = True
            front_frame = front_visualizer.draw_detections(front_frame, front_detections)

            # ====== 中鏡頭推論 ======
            center_results = model.predict(source=center_frame, verbose=False)[0]
            center_detections = process_results(center_results, center_estimator, class_ids_of_interest)
            for det in center_detections:
                if det[4] < 2.0:
                    logger.log_warning("Center Camera", det[4])
                    danger_detected = True
            center_frame = center_visualizer.draw_detections(center_frame, center_detections)

            # ====== 後鏡頭推論 ======
            rear_results = model.predict(source=rear_frame, verbose=False)[0]
            rear_detections = process_results(rear_results, rear_estimator, class_ids_of_interest)
            for det in rear_detections:
                if det[4] < 1.5:
                    logger.log_warning("Rear Camera", det[4])
                    danger_detected = True
            rear_frame = rear_visualizer.draw_detections(rear_frame, rear_detections)

            # ====== 畫面處理與合併 ======
            front_frame = cv2.resize(front_frame, (640, 360))
            center_frame = cv2.resize(center_frame, (640, 360))
            rear_frame = cv2.resize(rear_frame, (640, 360))

            combined_frame = cv2.vconcat([front_frame, center_frame, rear_frame])

            # ====== 加上右上角警告燈泡 ======
            if danger_detected:
                color = (0, 0, 255)  # 紅燈
                text = "DANGER"
            else:
                color = (0, 255, 0)  # 綠燈
                text = "SAFE"

            cv2.circle(combined_frame, (600, 30), 20, color, -1)
            cv2.putText(combined_frame, text, (560, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            cv2.imshow("Car Distance Estimation - 3 Views", combined_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"錯誤：{e}")

    finally:
        front_camera.release()
        center_camera.release()
        rear_camera.release()
        cv2.destroyAllWindows()

def process_results(results, estimator, class_ids_of_interest):
    detections = []
    for box, cls_id in zip(results.boxes.xyxy, results.boxes.cls):
        x1, y1, x2, y2 = map(int, box)
        class_id = int(cls_id)

        if class_id in class_ids_of_interest:
            height = y2 - y1
            distance = estimator.estimate_distance(height)
            if distance is not None:
                detections.append((x1, y1, x2, y2, distance))
    return detections

if __name__ == "__main__":
    main()
