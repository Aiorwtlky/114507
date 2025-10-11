# 🚗 Smart Vehicle Recorder System - 完整文檔

---

## 📋 系統概述

**吾駕仙 (My Driving God)** 是一個智慧車載錄影與駕駛行為分析系統，整合了：

- 🎥 **即時影像錄製**（內/外鏡頭）
- 🤖 **AI 駕駛行為分析**（疲勞、分心、ADAS）
- 📊 **自動評分系統**（15分鐘區間評分）
- ☁️ **雲端同步**（GCS + 後端 API）
- 💾 **本地資料快取**（離線可用）

---

## 🏗️ 系統架構

```
┌─────────────────────────────────────────────────────────┐
│                    車機端 (Raspberry Pi)                  │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  NFC Reader │  │  Camera 1   │  │  Camera 2   │     │
│  │   (Pico)    │  │   (內鏡頭)   │  │   (外鏡頭)   │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
│         │                 │                 │             │
│         └─────────────────┴─────────────────┘             │
│                           │                               │
│              ┌────────────▼────────────┐                  │
│              │   Main Application      │                  │
│              │   - PySide6 UI          │                  │
│              │   - Video Worker Thread │                  │
│              └────────┬────────────────┘                  │
│                       │                                   │
│         ┌─────────────┼─────────────┐                     │
│         │             │             │                     │
│  ┌──────▼──────┐ ┌───▼────┐ ┌─────▼─────┐               │
│  │ Trip Manager│ │Event   │ │Video      │               │
│  │ - 行程管理   │ │Detector│ │Recorder   │               │
│  │ - 評分計算   │ │- 疲勞  │ │- 錄影     │               │
│  └──────┬──────┘ │- 分心  │ └─────┬─────┘               │
│         │         │- ADAS  │       │                     │
│         │         └───┬────┘       │                     │
│         │             │            │                     │
│  ┌──────▼─────────────▼────────────▼─────┐               │
│  │      Local Database (SQLite)          │               │
│  │      - trips, events, videos          │               │
│  └──────┬────────────────────────────────┘               │
│         │                                                 │
│  ┌──────▼──────┐                                         │
│  │Sync Service │                                         │
│  │- Background │                                         │
│  │- Auto Retry │                                         │
│  └──────┬──────┘                                         │
│         │                                                 │
└─────────┼─────────────────────────────────────────────────┘
          │
          │ HTTPS
          │
┌─────────▼─────────────────────────────────────────────────┐
│                      雲端服務                               │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────┐         ┌──────────────────┐        │
│  │  Google Cloud   │         │   Backend API    │        │
│  │    Storage      │◄────────┤   (Django)       │        │
│  │  - 影片儲存      │         │   - 用戶管理      │        │
│  └─────────────────┘         │   - 行程記錄      │        │
│                              │   - AI 分析       │        │
│                              └──────────────────┘        │
└───────────────────────────────────────────────────────────┘
```

---

## 📦 核心模組說明

### **1. Database Layer (資料層)**

#### `database/models.py`
定義資料模型：
- **Trip**: 行程資料（開始/結束時間、評分、里程）
- **AIEvent**: AI 偵測事件（事件代碼、時間戳、扣分）
- **VideoRecord**: 影片記錄（本地路徑、GCS URL）
- **NFCMapping**: NFC 卡片與使用者對應（本地快取）
- **IntervalScore**: 15分鐘區間評分

#### `database/local_db.py`
SQLite 資料庫操作：
```python
db = LocalDatabase()
trip_id = db.create_trip(trip)
db.add_event(event)
db.get_unsynced_videos()
```

---

### **2. Core Modules (核心模組)**

#### `core/trip_manager.py`
行程管理器：
```python
trip_mgr = TripManager(db)

# 開始行程
trip_id = trip_mgr.start_trip(nfc_uid, user_info)

# 新增事件
trip_mgr.add_event("A01: 重度疲勞", "inner", 0.95)

# 結束行程
result = trip_mgr.end_trip(total_mileage=15.3)
# result = {score: 85.5, in_car_score: 90, out_car_score: 81, ...}
```

#### `core/score_calculator.py`
評分計算引擎：
- 將行程分割為 15 分鐘區間
- 每個區間獨立計算 A 類 / B 類扣分
- 根據規則計算最終分數：
  - 若任何區間 ≤ 60 分 → 取最低分
  - 否則 → 取平均分

#### `core/video_recorder.py`
影片錄製：
```python
recorder = VideoRecorder()
recorder.start_recording(inner_path, outer_path)
recorder.write_frame(inner_frame, outer_frame)
recorder.stop_recording()
```

#### `core/storage_manager.py`
檔案管理：
- 自動建立日期資料夾 (`2025-10-12/`)
- 磁碟空間檢查
- 舊影片自動清理

---

### **3. Event Detectors (事件偵測器)**

#### `event_detectors/advanced_fatigue_detector.py`
疲勞偵測：
- **A01**: 重度疲勞（閉眼 >5 秒）- 扣 40 分
- **A02**: 中度疲勞（閉眼 >3 秒）- 扣 30 分

#### `event_detectors/advanced_distraction_detector.py`
分心偵測：
- **A03**: 使用手機 - 扣 15 分
- **A04**: 臉部離開 - 扣 40 分
- **A05**: 視線偏離 - 扣 5 分

#### `event_detectors/presentation_adas_detector.py`
ADAS 偵測：
- **B01**: 切換車道未打方向燈 - 扣 15 分
- **B02**: 轉彎未打方向燈 - 扣 15 分
- **B03**: 未保持適當車距 - 扣 15 分

---

### **4. Sync Services (同步服務)**

#### `sync/gcs_uploader.py`
Google Cloud Storage 上傳：
```python
gcs = GCSUploader()
video_url = gcs.upload_video(
    local_path, 
    progress_callback=lambda p: print(f"{p}%")
)
# → https://storage.googleapis.com/bucket/videos/2025-10-12/video.mp4
```

#### `sync/api_client.py`
後端 API 客戶端：
```python
api = APIClient()

# NFC 查詢
user = api.lookup_nfc("AA:BB:CC:DD")

# 開始行程
backend_trip = api.start_trip({
    "trip_number": "TRIP_20251012_120000",
    "device": 1,
    "personnel": 123,
    ...
})

# 上傳事件
event_id = api.upload_event({
    "trip": backend_trip['id'],
    "event": 1,
    "timestamp": "2025-10-12T12:15:00Z",
    ...
})
```

#### `sync/sync_service.py`
背景同步服務：
- 每 60 秒自動同步
- 失敗自動重試
- 同步順序：Trip → Event → Video

```python
sync_service = SyncService(db, api, gcs)
sync_service.start()  # 背景執行緒啟動
```

---

### **5. UI Layer (使用者介面)**

#### `main_window.py`
PySide6 圖形介面：
```
┌─────────────────────────────────────────────┐
│  吾駕仙 - AI 駕駛行為分析系統                 │
├──────────────────┬──────────────────────────┤
│                  │  📊 行程資訊             │
│                  │  🚗 行程進行中            │
│   即時影像        │  行程編號: TRIP_xxx      │
│   (內鏡頭顯示)    │  行程時長: 05:23         │
│                  │  事件數量: 3             │
│                  │  錄影狀態: 🔴 錄影中      │
│                  │                          │
│                  │  🏆 評分                 │
│                  │  總分: 85.5              │
│                  │  車內: 90.0              │
│                  │  車外: 81.0              │
│                  │                          │
│                  │  📝 事件記錄             │
│                  │  [12:15] A01: 重度疲勞   │
│                  │  [12:20] B03: 車距過近   │
│                  │                          │
│                  │  [模擬刷卡] [清除記錄]   │
└──────────────────┴──────────────────────────┘
```

#### `worker.py`
影像處理執行緒：
- 即時讀取攝影機畫面
- 執行 AI 事件偵測
- 更新 UI 顯示
- 記錄事件到資料庫

---

### **6. GPIO Handler**

#### `gpio_handler.py`
與 Raspberry Pi Pico 通訊：
```python
gpio = GPIOHandler("/dev/ttyACM0")

def on_card_detected(nfc_uid):
    print(f"NFC detected: {nfc_uid}")
    # 開始或結束行程

gpio.on_nfc_detected = on_card_detected
gpio.start()
```

---

## 🔄 完整工作流程

### **1. 系統啟動**
```python
# main.py
db = LocalDatabase()
api = APIClient()
gcs = GCSUploader()
sync_service = SyncService(db, api, gcs)
gpio = GPIOHandler()

app = QApplication(sys.argv)
window = MainWindow()
window.show()

gpio.start()
sync_service.start()
```

### **2. 開始行程（NFC 刷卡）**
```
NFC Reader (Pico)
     ↓
GPIO Handler 偵測到卡片
     ↓
API 查詢使用者資訊
     ↓
Trip Manager 建立行程
     ↓
Video Recorder 開始錄影
     ↓
本地資料庫寫入 Trip
```

### **3. 行程進行中**
```
Camera → Video Worker
            ↓
         AI Detectors
    (疲勞/分心/ADAS)
            ↓
    偵測到事件？
            ↓ Yes
    Trip Manager.add_event()
            ↓
    本地資料庫寫入 Event
            ↓
    UI 顯示事件記錄
```

### **4. 結束行程（再次刷卡）**
```
NFC 再次刷卡
     ↓
Trip Manager.end_trip()
     ↓
Video Recorder 停止錄影
     ↓
Score Calculator 計算評分
  - 分割 15 分鐘區間
  - 計算 A/B 類扣分
  - 生成 AI 建議
     ↓
更新資料庫 (score, end_time)
     ↓
UI 顯示評分結果
```

### **5. 背景同步**
```
Sync Service (每 60 秒)
     ↓
查詢未同步的資料
     ↓
┌─────────────────────┐
│ 1. 同步 Trip         │
│    → API.start_trip()│
│    → API.end_trip()  │
│                     │
│ 2. 同步 Event       │
│    → API.upload_event()│
│                     │
│ 3. 同步 Video       │
│    → GCS.upload()    │
│    → API.register_video()│
└─────────────────────┘
     ↓
更新本地 sync_status
```

---

## 📊 評分規則詳解

### **15 分鐘區間評分**

```python
# 範例：30 分鐘行程
行程: 12:00 - 12:30

區間 1: 12:00 - 12:15
  - A01 (扣40) + A03 (扣15) = 扣55分 → A類得分 = 45
  - B01 (扣15) = 扣15分 → B類得分 = 85

區間 2: 12:15 - 12:30
  - A02 (扣30) = 扣30分 → A類得分 = 70
  - B03 (扣15) + B01 (扣15) = 扣30分 → B類得分 = 70

最終計算:
  - A類總分 = (45 + 70) / 2 = 57.5  # 有區間 ≤60，取最低 = 45
  - B類總分 = (85 + 70) / 2 = 77.5
  - 總分 = (45 * 0.5) + (77.5 * 0.5) = 61.25
```

---

## 🛠️ 設定檔說明

### `config.ini`

```ini
[device]
device_id = MAC_DEV_001          # 車機唯一 ID
device_name = 測試車機_Mac

[api]
base_url = http://mdgitrc.ntub.edu.tw:8000  # 後端 API
timeout = 30

[gcs]
bucket_name = mdg-itrc-videos    # GCS Bucket
credentials_path = credentials/gcs-service-account.json
video_folder = videos
upload_chunk_size = 5242880      # 5MB

[recording]
record_inner_camera = false      # 是否錄內鏡頭
record_outer_camera = true       # 是否錄外鏡頭
fps = 30
resolution_width = 1920
resolution_height = 1080

[database]
db_file = car_recorder.db        # SQLite 檔案

[sync]
auto_sync = true
sync_on_wifi_only = false        # 是否只在 WiFi 下同步
retry_attempts = 3
retry_delay = 5
```

---

## 🧪 測試腳本

### **test_system.py** - 完整系統測試
```bash
python3 test_system.py
```


---

## 🚀 部署指南

### **1. 樹莓派環境設定**
```bash
# 更新系統
sudo apt update && sudo apt upgrade -y

# 安裝相依套件
sudo apt install python3-pip python3-opencv -y

# 安裝 Python 套件
pip3 install PySide6 mediapipe requests google-cloud-storage pyserial
```

### **2. 設定 GCS 認證**
```bash
mkdir -p credentials
# 將 GCS service account JSON 放到 credentials/
```

### **3. 設定自動啟動**
```bash
# 建立服務檔
sudo nano /etc/systemd/system/car-recorder.service
```

```ini
[Unit]
Description=Smart Vehicle Recorder System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/car_recorder
ExecStart=/usr/bin/python3 /home/pi/car_recorder/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 啟用服務
sudo systemctl enable car-recorder
sudo systemctl start car-recorder
```

---

## 📈 系統監控

### **查看即時日誌**
```bash
tail -f car_recorder.log
```

### **檢查資料庫狀態**
```bash
sqlite3 car_recorder.db "SELECT * FROM trips ORDER BY trip_id DESC LIMIT 5;"
```

### **檢查同步狀態**
```bash
sqlite3 car_recorder.db "SELECT sync_status, COUNT(*) FROM trips GROUP BY sync_status;"
```

---

## 🐛 故障排除

### **問題 1：攝影機無法開啟**
```python
# 檢查可用攝影機
import cv2
cap = cv2.VideoCapture(0)
print(cap.isOpened())
```

### **問題 2：GCS 上傳失敗**
```bash
# 檢查認證檔
ls -l credentials/gcs-service-account.json
# 測試連線
python3 -c "from sync.gcs_uploader import GCSUploader; gcs = GCSUploader(); print(gcs.check_connection())"
```

### **問題 3：後端 API 連線失敗**
```bash
curl http://mdgitrc.ntub.edu.tw:8000/api/health/
```

---

## 📝 API 端點文檔

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/health/` | GET | 健康檢查 |
| `/api/token/` | POST | 取得 JWT Token |
| `/api/users/by-nfc/` | GET | NFC 查詢使用者 |
| `/api/trips/start/` | POST | 開始行程 |
| `/api/trips/{id}/end/` | PATCH | 結束行程 |
| `/api/events/` | POST | 上傳事件 |
| `/api/videos/register/` | POST | 註冊影片 |

---

## 🎯 效能指標

- **事件偵測延遲**: < 100ms
- **評分計算時間**: < 1s
- **影片上傳速度**: 依網路頻寬
- **本地儲存空間**: 約 1GB/小時 (1080p@30fps)
- **同步頻率**: 60 秒/次

---

## 📚 未來擴充

- [ ] 多鏡頭同時錄影
- [ ] 即時串流到後端
- [ ] GPS 軌跡記錄
- [ ] OBD-II 車輛數據整合
- [ ] 語音警示系統
- [ ] 雲端 AI 模型更新

---

**系統版本**: v1.0.0  
**最後更新**: 2025-10-12  
**維護者**: NTUB MDG-ITRC Team