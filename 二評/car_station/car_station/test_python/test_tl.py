# test_final.py
import cv2
import time
from utils.traffic_light_final import TrafficLightDetectorFinal

detector = TrafficLightDetectorFinal()
cap = cv2.VideoCapture('C:\\Users\\super\\Desktop\\114507\\二評\\car_station\\car_station\\Result2.mp4')

frame_count = 0
b03_count = 0
last_b03 = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_count += 1
    result = detector.detect(frame, draw_visualization=True)
    
    if frame_count % 30 == 0:
        print(f"[{frame_count}] {result['light_state']} | "
              f"偵測: {result['light_detected']} | 移動: {result['vehicle_moving']}")
    
    if result['red_light_violation']:
        current = time.time()
        if current - last_b03 > 5:
            b03_count += 1
            last_b03 = current
            print(f"\n🚨 [B03] #{b03_count}\n")
    
    cv2.imshow('B03 Final', result['visualization'])
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

print(f"\n偵測率: {detector.detection_count/frame_count*100:.1f}%")
print(f"B03 事件: {b03_count}")
cap.release()
cv2.destroyAllWindows()