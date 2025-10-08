import cv2

for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"✅ 攝影機 {i} 可用")
        ret, frame = cap.read()
        if ret:
            print(f"    畫面解析度：{frame.shape[1]}x{frame.shape[0]}")
        cap.release()
    else:
        print(f"❌ 攝影機 {i} 無法開啟")
