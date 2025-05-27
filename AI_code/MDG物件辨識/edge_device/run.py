import cv2
import time
from camera_input import get_camera, read_frame, release_camera
from yolo_detector import detect_objects
from roi_checker import InnerWheelDiffROI
from event_manager import EventManager

def main():
    # 參數設定
    axle_length = 3.5  # 公尺
    turn_angle_deg = 30
    pixels_per_meter = 50
    frame_width = 640
    frame_height = 480
    center_x = frame_width // 2
    center_y = frame_height - 50

    roi = InnerWheelDiffROI(axle_length, turn_angle_deg, pixels_per_meter, center_x, center_y)
    event_manager = EventManager()

    cap = get_camera(0)

    try:
        while True:
            frame = read_frame(cap)

            detections = detect_objects(frame)

            roi.draw_roi(frame)

            triggered = False
            detected_objects = []

            for det in detections:
                x1, y1, x2, y2 = det['bbox']
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                if det['class'] in ['person', 'bicycle', 'motorcycle']:
                    if roi.is_point_in_roi(cx, cy):
                        triggered = True
                        detected_objects.append(det)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    else:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"{det['class']} {det['confidence']:.2f}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            if triggered and not event_manager.recording:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                video_path = event_manager.start_recording(frame.shape, timestamp)
                image_path = event_manager.save_screenshot(frame, timestamp)
                print(f"警示觸發：錄影 {video_path}，截圖 {image_path}")
                print("偵測物件：", detected_objects)

            if event_manager.recording:
                event_manager.record_frame(frame)
                if event_manager.check_recording_timeout():
                    print("錄影結束")

            cv2.imshow("內輪差警示系統", frame)
            if cv2.waitKey(1) == 27:
                break

    finally:
        release_camera(cap)

if __name__ == "__main__":
    main()
