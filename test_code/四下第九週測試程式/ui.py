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
                bbox_height = y2 - y1

                # ✅ 這行是新增的，印出高度
                print(f"[INFO] BBox高度 = {bbox_height}px")

                # 下面 distance 可以先暫時不管，或者用假的也行
                distance = estimate_distance(bbox_height)

                color = (0, 255, 0) if distance > 10 else (0, 0, 255)

                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(annotated_frame, f"{distance:.1f} m", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    return annotated_frame

def estimate_distance(bbox_height_pixels):
    if bbox_height_pixels == 0:
        return 999  # 避免除以零

    k = 958  # 你自己量出來的
    distance = k / bbox_height_pixels
    return distance
