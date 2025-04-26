import cv2

def draw_detections(frame, results):
    annotated_frame = frame.copy()
    detections = results[0].boxes

    if detections is not None:
        for box in detections:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = box.conf[0]
            cls = int(box.cls[0])

            # 只標示 person（類別0）
            if cls == 0:
                height = y2 - y1
                distance = estimate_distance(height)

                # 判斷危險距離
                color = (0, 255, 0) if distance > 10 else (0, 0, 255)

                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(annotated_frame, f"{distance:.1f} m", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    return annotated_frame

def estimate_distance(bbox_height_pixels):
    if bbox_height_pixels == 0:
        return 999

    # 區間判斷
    if bbox_height_pixels > 200:
        return 2  # 超近距離，2公尺內
    elif bbox_height_pixels > 120:
        return 5  # 中距離，5公尺內
    elif bbox_height_pixels > 60:
        return 8  # 遠距離，8公尺內
    else:
        return 15  # 很遠（無危險）
