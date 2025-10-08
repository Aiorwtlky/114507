import cv2
import torch

# 載入你下載的模型（指定路徑）
model = torch.hub.load('ultralytics/yolov5', 'custom', path='weights/yolov5s.pt', source='github')
model.eval()

# 開啟攝影機
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 轉成 RGB（模型需要）
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 推論
    results = model(img_rgb)

    # 處理結果
    for *box, conf, cls in results.xyxy[0]:
        x1, y1, x2, y2 = map(int, box)
        label = model.names[int(cls)]
        confidence = float(conf)

        # 繪製框線與文字
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
        cv2.putText(frame, f'{label} {confidence:.2f}', (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # 顯示畫面
    cv2.imshow("YOLOv5 Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
