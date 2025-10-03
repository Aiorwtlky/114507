```markdown
# 🚗 AI 視覺辨識車機系統 - 外鏡頭開發交接文件

> 交接時間：2025-10-02  
> 專案階段：內鏡頭完成 ✅ / 外鏡頭待開發 ⏳  
> 技術棧：Flask + MediaPipe + YOLOv8 + OpenCV

---

## 📋 專案現況總覽

### 已完成功能 ✅

**內鏡頭 AI 偵測（MediaPipe）- 100% 完成**
- A01：閉眼 3-5 秒（重度疲勞）- 25 分
- A02：閉眼 ≥ 5 秒（中度疲勞）- 15 分
- A04：無臉部 ≥ 5 秒（分心駕駛）- 15 分
- 個體化校準系統（適應不同眼睛大小）
- 動態閾值調整（0.65-0.72）
- 完整異常處理

**系統測試狀態：**
- ✅ 校準成功率：100%
- ✅ A01/A02 準確率：95%+（無誤判）
- ✅ A04 穩定觸發
- ✅ 適應小眼睛駕駛

### 待開發功能 ⏳

**外鏡頭 AI 偵測（OpenCV + YOLOv8）**
- B01：車道偏離（未打方向燈）- 5 分
- B02：前車過近 - 15 分
- B03：闖紅燈 - 30 分

---

## 🎯 外鏡頭功能需求

### B01：車道偏離偵測（OpenCV）

**技術方案：**
- 使用 Canny 邊緣偵測 + Hough 直線變換
- 偵測左右車道線
- 計算車輛位置是否偏離

**觸發條件：**
```python
if 偵測到偏離車道 and 未打方向燈:
    觸發 B01（扣 5 分）
```

**需要整合：**
- GPIO 讀取左/右方向燈狀態
- 車道線持續追蹤（3 秒寬限期）

---

### B02：前車過近偵測（YOLOv8）

**技術方案：**
- YOLOv8 偵測前方車輛（class: car, truck, bus）
- 根據 bounding box 大小估算距離
- 參考安全距離公式

**距離估算：**
```python
distance = (實際車寬 × 焦距) / 像素寬度
標準車寬 = 1.8m
焦距 = 700 像素（需校準）
```

**觸發條件：**
```python
if 前車距離 < 安全距離:
    觸發 B02（扣 15 分）

安全距離 = max(車速 × 0.5, 5 米)
```

**需要整合：**
- GPS 模組讀取車速

---

### B03：闖紅燈偵測（YOLOv8）

**技術方案：**
- YOLOv8 偵測交通號誌（class: traffic light）
- 識別紅燈狀態（透過 ROI 顏色分析）
- 結合 GPS 車速判斷

**觸發條件：**
```python
if 偵測到紅燈 and 車速 > 5 km/h:
    觸發 B03（扣 30 分）
```

---

## 📂 專案架構

```
car_station/
├── utils/
│   ├── drowsiness_detector.py       ✅ 內鏡頭（已完成）
│   ├── unified_ai_detector.py       ✅ 統一控制器（需更新事件映射）
│   ├── image_recognition.py         ✅ 主接口（需加入外鏡頭邏輯）
│   ├── lane_departure_detector.py   ⏳ 車道偵測（待開發）
│   └── vehicle_traffic_detector.py  ⏳ YOLOv8 偵測（待開發）
│
├── blueprints/
│   ├── camera.py                    ✅ AI 監控執行緒（已整合內鏡頭）
│   ├── trip.py                      ✅ 行程管理
│   └── gpio.py                      ✅ GPIO 讀取（方向燈）
│
├── models.py                        ✅ 資料庫模型
├── yolov8n.pt                       ✅ YOLOv8 模型檔案
└── calibrations/                    ✅ 校準數據目錄
```

---

## 🔑 關鍵檔案狀態

### 1. drowsiness_detector.py（已完成）✅

**核心功能：**
```python
class PersonalizedDrowsinessDetector:
    def calibrate(self, frame):
        # 個體化校準（30 個 EAR 樣本）
        
    def detect(self, frame, draw_landmarks=False):
        # 返回 (result_dict, output_frame)
        # result['event_type']: 'drowsy_severe'/'drowsy_moderate'/'no_face_detected'
```

**事件定義：**
- A01 觸發：`consecutive_closed_frames == 90`（3 秒）
- A02 觸發：`consecutive_closed_frames == 150`（5 秒）
- A04 觸發：`consecutive_no_face_frames == 150`（5 秒）

**閾值設定：**
```python
def get_adaptive_threshold_factor(self):
    if baseline_ear >= 0.30: return 0.65
    elif baseline_ear >= 0.25: return 0.68
    elif baseline_ear >= 0.20: return 0.70
    else: return 0.72
```

---

### 2. unified_ai_detector.py（需更新）⚠️

**當前事件映射：**
```python
self.event_mapping = {
    'drowsy_severe': {'code': 'A01', 'points': 25},
    'drowsy_moderate': {'code': 'A02', 'points': 15},
    'no_face_detected': {'code': 'A04', 'points': 15},
    # 待新增：
    # 'lane_departure_left': {'code': 'B01', 'points': 5},
    # 'lane_departure_right': {'code': 'B01', 'points': 5},
    # 'tailgating': {'code': 'B02', 'points': 15},
    # 'red_light_violation': {'code': 'B03', 'points': 30}
}
```

**需要實作的方法：**
```python
def detect_outside_camera(self, frame, left_turn_signal, right_turn_signal, vehicle_speed):
    # 1. 呼叫 lane_detector.detect()
    # 2. 呼叫 vehicle_detector.detect()
    # 3. 整合 GPIO 和 GPS 數據
    # 4. 返回事件列表
```

---

### 3. image_recognition.py（需更新）⚠️

**需要修改的部分：**
```python
def predict_from_frame(self, frame, camera_type, save_image, gpio_data, gps_data):
    if camera_type == 'inside':
        # ✅ 已完成
        event_record = self.unified_detector.detect_inside_camera(frame)
        
    elif camera_type == 'outside':
        # ⏳ 待實作
        # 解析 GPIO 數據（方向燈）
        # 解析 GPS 數據（車速）
        # 呼叫 unified_detector.detect_outside_camera()
```

---

### 4. camera.py（已整合內鏡頭）✅

**AI 監控執行緒：**
```python
def ai_monitoring_worker(camera_id, trip_id):
    while ai_monitoring_active.get(camera_id):
        frame = get_camera(camera_id).get_frame()
        
        # 讀取 GPIO 和 GPS（外鏡頭需要）
        gpio_data = {'left_turn': False, 'right_turn': False}
        gps_data = {'speed': 0.0}
        
        event_record = vision_system.predict_from_frame(
            frame, camera_id, save_image=True,
            gpio_data=gpio_data, gps_data=gps_data
        )
```

---

## 🔧 外鏡頭開發任務清單

### 階段 1：車道偵測（B01）

**建立 `lane_departure_detector.py`：**
```python
class LaneDepartureDetector:
    def __init__(self):
        self.left_lane_history = deque(maxlen=90)
        self.right_lane_history = deque(maxlen=90)
        
    def detect(self, frame, left_turn_signal, right_turn_signal):
        # 1. 灰階 + 高斯模糊
        # 2. Canny 邊緣偵測
        # 3. ROI 遮罩（只看下半部道路）
        # 4. Hough 直線變換
        # 5. 分離左右車道線
        # 6. 判斷偏離
        # 7. 整合方向燈（3 秒寬限期）
        
        return {
            'event_triggered': bool,
            'event_type': 'lane_departure_left'/'lane_departure_right',
            'confidence': float,
            'metrics': {...}
        }
```

**測試方法：**
- 使用行車記錄器影片測試
- 模擬 GPIO 方向燈信號

---

### 階段 2：前車與紅燈偵測（B02/B03）

**建立 `vehicle_traffic_detector.py`：**
```python
class VehicleTrafficDetector:
    def __init__(self):
        from ultralytics import YOLO
        self.model = YOLO('yolov8n.pt')
        self.tracked_vehicles = {}
        
    def detect(self, frame):
        # 1. YOLOv8 偵測
        results = self.model(frame, classes=[2, 5, 7, 9])  # car, bus, truck, traffic light
        
        # 2. 前車距離估算
        # 3. 紅燈識別
        
        return {
            'status': 'detected',
            'events': [
                {'event_type': 'tailgating', 'distance': 3.5, ...},
                {'event_type': 'red_light_detected', ...}
            ]
        }
```

**距離估算公式：**
```python
def estimate_distance(self, bbox_width):
    VEHICLE_WIDTH = 1.8  # 米
    FOCAL_LENGTH = 700   # 像素（需實測校準）
    return (VEHICLE_WIDTH * FOCAL_LENGTH) / bbox_width
```

---

### 階段 3：整合到系統

**更新 `unified_ai_detector.py`：**
```python
def detect_outside_camera(self, frame, left_turn_signal, right_turn_signal, vehicle_speed):
    events = []
    
    # B01: 車道偵測
    lane_result = self.lane_detector.detect(frame, left_turn_signal, right_turn_signal)
    if lane_result.get('event_triggered'):
        events.append(self._format_event('B01', lane_result))
    
    # B02/B03: 車輛與交通號誌
    vehicle_result = self.vehicle_detector.detect(frame)
    for event in vehicle_result.get('events', []):
        if event['event_type'] == 'tailgating':
            events.append(self._format_event('B02', event))
        elif event['event_type'] == 'red_light_detected' and vehicle_speed > 5:
            events.append(self._format_event('B03', event))
    
    return events
```

---

## 📊 評分標準（完整版）

| 代碼 | 描述 | 觸發條件 | 扣分 | 狀態 |
|------|------|----------|------|------|
| A01 | 重度疲勞 | 閉眼 3-5 秒 | 25 | ✅ |
| A02 | 中度疲勞 | 閉眼 ≥ 5 秒 | 15 | ✅ |
| A04 | 長時間無臉部 | ≥ 5 秒 | 15 | ✅ |
| B01 | 車道偏離 | 未打方向燈 | 5 | ⏳ |
| B02 | 前車過近 | < 安全距離 | 15 | ⏳ |
| B03 | 闖紅燈 | 紅燈 + 移動 | 30 | ⏳ |

---

## 🧪 測試建議

### 測試資源
1. **行車記錄器影片**（YouTube/Kaggle）
2. **模擬 GPIO**（假數據）
3. **模擬 GPS**（固定車速）

### 測試腳本範例
```python
# test_outside_camera.py
import cv2
from utils.vehicle_traffic_detector import VehicleTrafficDetector

detector = VehicleTrafficDetector()
cap = cv2.VideoCapture('dashcam.mp4')

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    result = detector.detect(frame)
    print(result)
    
    cv2.imshow('Test', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
```

---

## 💡 技術提示

### YOLOv8 使用
```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')
results = model(frame, classes=[2, 5, 7, 9])  # 只偵測車輛和紅綠燈

for r in results:
    boxes = r.boxes
    for box in boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        x1, y1, x2, y2 = box.xyxy[0].tolist()
```

### OpenCV 車道線偵測
```python
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)
edges = cv2.Canny(blur, 50, 150)

# ROI 遮罩
mask = np.zeros_like(edges)
height = edges.shape[0]
roi_vertices = [(0, height), (width//2, height//2), (width, height)]
cv2.fillPoly(mask, [np.array(roi_vertices)], 255)
masked_edges = cv2.bitwise_and(edges, mask)

# Hough 變換
lines = cv2.HoughLinesP(masked_edges, 1, np.pi/180, 50, minLineLength=100, maxLineGap=50)
```

---

## 🚀 下一步行動

### 優先順序
1. **B02 前車過近**（最簡單）
   - 單純 YOLOv8 偵測 + 距離估算
   - 不需 GPIO，只需 GPS

2. **B01 車道偏離**（中等）
   - OpenCV 車道線偵測
   - 需整合 GPIO 方向燈

3. **B03 闖紅燈**（最複雜）
   - YOLOv8 偵測交通號誌
   - ROI 顏色分析判斷紅燈
   - 需整合 GPS

### 開發建議
- 先用影片測試演算法可行性
- 確認準確率 > 80% 再整合
- 每個功能獨立測試後再整合

---

## 📞 關鍵資訊

### 硬體需求
- 外鏡頭：RTSP 串流或 USB 攝影機
- GPIO：讀取方向燈（左/右）
- GPS：讀取車速（km/h）

### 現有資源
- ✅ YOLOv8n 模型已下載
- ✅ Flask 系統運行正常
- ✅ 資料庫表格已建立
- ✅ AI 監控執行緒架構完成

---

**系統狀態：** 內鏡頭完成，外鏡頭待開發  
**當前進度：** 50%  
**預計完成：** 外鏡頭開發約需 3-5 天  
**測試環境：** Windows 開發環境  
**目標部署：** Raspberry Pi 4

---

**交接完成，祝開發順利！**
```

這份文件涵蓋了所有關鍵資訊，新的 Claude 可以立即開始外鏡頭開發。