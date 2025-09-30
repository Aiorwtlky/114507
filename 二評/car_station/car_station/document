# 🚗 AI 視覺辨識車機系統 - 現況接軌文件

> 給新 Claude 對話：這是一個已經開發到 90% 的生產級 AI 車機系統

## 📋 專案概況

**專案名稱：** 吾駕仙車隊管理系統 - AI 視覺辨識模組  
**開發階段：** 整合測試中（90% 完成）  
**技術棧：** Flask + MediaPipe + YOLOv8 + OpenCV  
**部署環境：** Windows 開發環境（目標：Raspberry Pi 4）

## 🎯 系統功能

### 已實作功能
1. **內鏡頭 AI 偵測**（MediaPipe）
   - 疲勞駕駛偵測（個體化校準）
   - 支援眼睛大小不同的駕駛
   - 事件：A01（重度疲勞）、A02（中度疲勞）、A03（分心）

2. **外鏡頭 AI 偵測**（OpenCV + YOLOv8）
   - 車道偏離偵測（整合 GPIO 方向燈）
   - 前車距離估計
   - 紅綠燈辨識
   - 事件：B01（車道偏離）、B02（前車過近）、B03（闖紅燈）

3. **資料流程**
   - 本地事件暫存（EventLogLocal）
   - 上傳佇列機制（UploadQueue）
   - 網路斷線容錯

## 📂 專案結構

```
car_station/
├── app.py                          ✅ 已更新（註冊 recognition_bp）
├── models.py                       ✅ 已更新（加 3 個新表格）
├── config.py                       ✅ 原有（需確認 CAMERA_URLS）
├── requirements.txt                ✅ 已提供（完整 AI 套件）
│
├── blueprints/
│   ├── camera.py                   ✅ 已更新（加 AI 監控）
│   ├── trip.py                     ✅ 已更新（自動啟動/停止 AI）
│   ├── image_recognition.py        ✅ 已建立
│   ├── gpio.py                     ✅ 原有（讀取方向燈）
│   └── video.py                    ✅ 原有（錄影功能）
│
└── utils/
    ├── drowsiness_detector.py      ✅ 已建立（MediaPipe 疲勞偵測）
    ├── lane_departure_detector.py  ✅ 已建立（車道偵離 + GPIO）
    ├── vehicle_traffic_detector.py ✅ 已建立（YOLOv8 前車/紅燈）
    ├── unified_ai_detector.py      ✅ 已建立（統一控制器）
    ├── image_recognition.py        ✅ 已建立（主要接口）
    ├── db_helper.py                ✅ 已建立
    └── uploader.py                 ✅ 已建立（簡化版）
```

## ✅ 已完成的步驟

1. ✅ 安裝所有 AI 依賴套件（mediapipe, ultralytics, opencv）
2. ✅ 建立 5 個核心 AI 模組
3. ✅ 更新 models.py（EventLogLocal, UploadQueue, TripLocal）
4. ✅ 更新 camera.py（AI 監控執行緒）
5. ✅ 更新 trip.py（自動啟動/停止 AI）
6. ✅ 建立 recognition blueprint
7. ✅ 下載 YOLOv8n 模型
8. ✅ Flask 可正常啟動

## 🔧 當前狀態

**運行狀態：**
- Flask 服務：✅ 正常運行（port 5003）
- 錄影功能：✅ 正常
- API 端點：✅ 可呼叫
- 資料庫：✅ 表格已建立

**待解決問題：**
- ⚠️ AI 監控執行緒啟動但沒有輸出偵測訊息
- ⚠️ 需要驗證 MediaPipe 校準是否正常運作
- ⚠️ 內鏡頭設為 camera index 0（需測試）

## 🎯 評分標準對照表

| 代碼 | 描述 | 扣分 | AI 模型 |
|------|------|------|---------|
| A01 | 重度疲勞駕駛（閉眼>3秒） | 25 | MediaPipe |
| A02 | 中度疲勞駕駛（閉眼1-3秒） | 15 | MediaPipe |
| A03 | 長時間分心（低頭>5秒） | 20 | MediaPipe |
| B01 | 車道偏離（未打方向燈） | 5 | OpenCV |
| B02 | 前車過近 | 15 | YOLOv8 |
| B03 | 闖紅燈 | 30 | YOLOv8 |

## 🧪 測試腳本

```python
# a.py - 完整測試流程
import requests
import time

response = requests.post("http://localhost:5003/trip/api/start_trip")
print("開始行程:", response.json())
trip_id = response.json().get('trip_id')

print("等待 30 秒進行 AI 偵測...")
time.sleep(30)

response = requests.post("http://localhost:5003/trip/api/end_trip")
print("結束行程:", response.json())

if trip_id:
    response = requests.get(f"http://localhost:5003/recognition/trip/{trip_id}/events/summary")
    print("事件摘要:", response.json())
```

## 🐛 除錯要點

### 如果 AI 沒有輸出

**檢查 1：camera.py 的 ai_monitoring_worker 是否執行**
在函數開頭加入：
```python
print(f"[DEBUG] AI worker 啟動: {camera_id}")
```

**檢查 2：模組導入是否成功**
```python
try:
    from utils.image_recognition import get_vision_system
    print("[DEBUG] 模組導入成功")
except Exception as e:
    print(f"[ERROR] 模組導入失敗: {e}")
```

**檢查 3：攝影機是否可讀取**
```python
camera = get_camera(camera_id)
if camera:
    frame = camera.get_frame()
    print(f"[DEBUG] 攝影機畫面大小: {frame.shape if frame is not None else 'None'}")
```

### 如果 MediaPipe 無法初始化

確認已安裝：
```bash
pip install mediapipe==0.10.9
```

### 如果 YOLOv8 找不到模型

下載模型：
```python
from ultralytics import YOLO
model = YOLO('yolov8n.pt')  # 自動下載
```

## 📊 系統架構流程

```
行程開始
  ↓
自動啟動雙鏡頭 AI 監控
  ├─ 內鏡頭執行緒
  │   ├─ 校準（30 樣本，約 3 秒）
  │   ├─ MediaPipe 偵測
  │   └─ 偵測到事件 → EventLogLocal
  │
  └─ 外鏡頭執行緒
      ├─ 讀取 GPIO（方向燈）
      ├─ OpenCV 車道線偵測
      ├─ YOLOv8 車輛/紅燈偵測
      └─ 偵測到事件 → EventLogLocal
  ↓
行程結束
  ↓
停止 AI 監控
  ↓
（未來）批次上傳到後端
```

## 🔑 關鍵程式碼位置

### 1. AI 監控啟動
**檔案：** `blueprints/trip.py`  
**位置：** `api_start_trip` 函數，return 之前
```python
# 🤖 自動啟動 AI 監控
from blueprints.camera import ai_monitoring_active, ai_monitoring_worker
```

### 2. AI 偵測邏輯
**檔案：** `utils/image_recognition.py`  
**函數：** `predict_from_frame()`

### 3. 事件儲存
**檔案：** `utils/db_helper.py`  
**函數：** `LocalEventHelper.create_event()`

### 4. 疲勞偵測核心
**檔案：** `utils/drowsiness_detector.py`  
**類別：** `PersonalizedDrowsinessDetector`

## 💡 下一步行動

1. **驗證 AI 是否真的在運作**
   - 加入 debug 輸出
   - 檢查終端是否有「🤖 AI 監控啟動」訊息

2. **測試內鏡頭偵測**
   - 確認 camera index 0 可讀取
   - 觀察校準過程
   - 模擬閉眼測試

3. **修復任何錯誤**
   - 檢查 traceback
   - 確認模組導入

4. **完整測試流程**
   - 內鏡頭偵測疲勞
   - 外鏡頭偵測車道偏離
   - 事件正確儲存到資料庫

## 📞 常見問題快速解答

**Q: AI 沒有任何輸出？**  
A: 在 `camera.py` 的 `ai_monitoring_worker` 加入 debug print

**Q: ModuleNotFoundError?**  
A: 檢查 utils/ 目錄是否有所有檔案，特別是 `__init__.py`

**Q: MediaPipe 找不到臉部？**  
A: 確認攝影機角度、光線充足、臉部在畫面中央

**Q: YOLOv8 太慢？**  
A: 使用 `yolov8n.pt`（最輕量），調整 `PROCESS_EVERY_N_FRAMES = 5`

**Q: 資料庫錯誤？**  
A: 確認已執行建表指令並成功建立 EventLogLocal 等表格

## 🎓 技術細節

### MediaPipe 個體化校準原理
- 收集 30 個正常睜眼樣本
- 計算基準 EAR（眼睛縱橫比）
- 閉眼閾值 = 基準 × 0.7
- 完全適應個體差異

### GPIO 整合邏輯
- 持續讀取方向燈狀態
- 打方向燈 + 偏離 = 正常變換車道
- 未打方向燈 + 偏離 = 警告
- 3 秒寬限期

### YOLOv8 距離估計
```
distance = (real_width × focal_length) / pixel_width
標準車寬 = 1.8m
焦距 = 700 像素（需校準）
```

---

**系統狀態：** 90% 完成，主要功能已實作，進入整合測試階段  
**最後更新：** 2025/09/30  
**開發者：** 透過 Claude 協助開發