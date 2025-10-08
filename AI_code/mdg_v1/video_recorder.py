# video_recorder.py

import cv2
import time

# 開啟 WebCam（index 0）
cap = cv2.VideoCapture(0)

# 取得解析度與 FPS 設定
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))   # 一般為 640
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # 一般為 480
fps    = int(cap.get(cv2.CAP_PROP_FPS)) or 20     # 若抓不到 FPS，預設為 20

# 設定錄製參數（錄 15 秒）
duration_seconds = 15
frame_count = duration_seconds * fps

# 建立錄影器
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('clip.mp4', fourcc, fps, (width, height))

print(f"開始錄影：{duration_seconds} 秒 @ {fps} fps, 解析度：{width}x{height}")

count = 0
while count < frame_count:
    ret, frame = cap.read()
    if not ret:
        break

    out.write(frame)
    count += 1

print("錄影結束，檔案已儲存為 clip.mp4")

cap.release()
out.release()
cv2.destroyAllWindows()
