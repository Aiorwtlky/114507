# test_all_events.py
import cv2
from utils.drowsiness_detector import PersonalizedDrowsinessDetector

detector = PersonalizedDrowsinessDetector('TEST_ALL')
cap = cv2.VideoCapture(0)

print("=" * 60)
print("完整事件測試")
print("=" * 60)
print("\n測試項目：")
print("  1. 閉眼 1 秒 → A02")
print("  2. 閉眼 3 秒 → A01")
print("  3. 打哈欠 3 次 → A03")
print("  4. 低頭/轉頭 5 秒 → A04")
print("\n按 'q' 退出\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    result, display_frame = detector.detect(frame, draw_landmarks=True)
    
    if result.get('status') == 'calibrating':
        print(f"\r校準中... {result['progress']}/30", end='')
    elif result.get('event_type'):
        event = result['event_type']
        metrics = result.get('metrics', {})
        print(f"\n🚨 {event}")
        print(f"   MAR: {metrics.get('mar', 0):.3f}")
        print(f"   打哈欠: {metrics.get('total_yawns', 0)} 次")
    
    cv2.imshow('Test', display_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print(f"\n總打哈欠: {detector.total_yawns} 次")