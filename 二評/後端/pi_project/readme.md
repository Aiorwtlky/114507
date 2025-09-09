# Pi Project - 車載安全監控系統

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

基於 Raspberry Pi 的智慧車載安全監控系統，整合 AI 視覺辨識技術，提供駕駛員疲勞檢測、ADAS 輔助駕駛功能與雲端資料管理。

## 功能特色

### 駕駛員監控 (內鏡頭)
- **A01**: 重度疲勞駕駛 (閉眼超過3秒) - 25分
- **A02**: 中度疲勞駕駛 (閉眼1-3秒) - 15分  
- **A03**: 長時間分心 (低頭/轉頭超過5秒) - 20分
- **A04**: 駕駛中使用手機 - 20分

### ADAS 輔助駕駛 (外鏡頭)
- **B01**: 車道偏離 (未打方向燈) - 5分
- **B02**: 前車過近 - 15分
- **B03**: 闖紅燈 - 30分

### 個人化校準系統
- 適應不同駕駛員的眼型差異
- 個人化疲勞檢測閾值
- 智慧型動態調整
- 解決眼睛大小導致的誤判問題

### 雲端整合
- 每分鐘自動錄影
- 即時上傳至 Cloudinary
- 本地緩存與離線支援
- 自動清理舊檔案

## 快速開始

### 系統需求

- **硬體**: Raspberry Pi 4B (4GB RAM 以上)
- **作業系統**: Raspberry Pi OS Bullseye 64-bit 或 macOS/Linux
- **Python**: 3.8 以上
- **攝影機**: USB 攝影機 x2 (內外鏡頭)
- **網路**: WiFi 或有線網路連接

### 1. 環境設定

```bash
# 克隆或下載專案
git clone <repository_url>
cd pi_project

# 建立虛擬環境 (推薦)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 安裝依賴套件
pip install -r requirements.txt
```

### 2. 環境配置

```bash
# 複製環境變數範本
cp .env.example .env

# 編輯環境變數檔案
nano .env
```

**重要**: 請在 `.env` 檔案中設定您的 Cloudinary 帳戶資訊：
- `CLOUDINARY_CLOUD_NAME`: 您的 Cloudinary 雲端名稱
- `CLOUDINARY_API_KEY`: API 金鑰
- `CLOUDINARY_API_SECRET`: API 密鑰

### 3. 系統檢查

```bash
# 執行系統健康檢查
python scripts/system_check.py

# 測試攝影機功能
python scripts/test_cameras.py
```

### 4. 駕駛員校準

```bash
# 首次使用必須進行個人化校準
python scripts/calibrate_driver.py --name "您的姓名"

# 或在主程式中校準
python main.py --calibrate --driver-name "您的姓名"
```

### 5. 啟動系統

```bash
# 正常啟動 (會提示選擇駕駛員)
python main.py

# 指定駕駛員啟動
python main.py --driver-id "driver_1693507210"

# 除錯模式
python main.py --debug
```

## 專案架構

```
pi_project/
├── main.py                         # 主程式進入點
├── config.py                       # 配置管理
├── utils.py                        # 工具函式
│
├── driver_monitor.py               # 駕駛員監控 (基礎版)
├── improved_driver_monitor.py      # 駕駛員監控 (個人化版)
├── driver_calibration.py           # 個人化校準系統
├── adas_analyzer.py                # ADAS 分析系統
│
├── dashcam_recorder.py             # 影像錄製系統
├── cloudinary_uploader.py          # 雲端上傳服務
├── database_manager.py             # 資料庫管理
├── hardware_manager.py             # 硬體介面
│
├── data/                           # 資料目錄
│   ├── driver_profiles.json        # 駕駛員個人檔案
│   ├── system.db                   # 本地資料庫
│   └── logs/                       # 系統日誌
│
├── temp_videos/                    # 暫存影片目錄
├── models/                         # AI 模型目錄
├── scripts/                        # 工具腳本
└── tests/                          # 測試檔案
```

## 使用指南

### 個人化校準流程

1. **環境準備**
   - 確保良好的光線條件
   - 調整攝影機角度
   - 坐在正常駕駛位置

2. **校準階段**
   - **正常狀態校準** (30秒): 保持正常眼睛狀態，直視前方
   - **眨眼模式校準** (15次): 進行正常眨眼，每次稍作停頓
   - **頭部姿態校準** (20秒): 保持正常駕駛姿勢

3. **結果評估**
   - 系統會計算個人化閾值
   - 顯示校準品質評分
   - 建議每月重新校準

### 警報評分系統

| 代碼 | 警報類型 | 分數 | 檢測來源 | 觸發條件 |
|------|----------|------|----------|----------|
| A01  | 重度疲勞駕駛 | 25分 | 內鏡頭 | 閉眼超過3秒 |
| A02  | 中度疲勞駕駛 | 15分 | 內鏡頭 | 閉眼1-3秒 |
| A03  | 長時間分心 | 20分 | 內鏡頭 | 低頭/轉頭超過5秒 |
| A04  | 駕駛中使用手機 | 20分 | 內鏡頭 | 手機使用手勢1秒 |
| B01  | 車道偏離 | 5分 | 外鏡頭 | 未打方向燈偏離2秒 |
| B02  | 前車過近 | 15分 | 外鏡頭 | 小於安全距離3秒 |
| B03  | 闖紅燈 | 30分 | 外鏡頭 | 紅燈時繼續行駛 |

### 命令列選項

```bash
# 系統相關
python main.py --help                    # 顯示說明
python main.py --debug                   # 除錯模式
python main.py --test-cameras            # 測試攝影機

# 駕駛員管理
python main.py --calibrate              # 進入校準模式
python main.py --driver-name "姓名"     # 指定駕駛員姓名
python main.py --driver-id "ID"         # 指定駕駛員ID

# 工具腳本
python scripts/system_check.py          # 系統健康檢查
python scripts/test_cameras.py          # 攝影機測試
python scripts/calibrate_driver.py      # 獨立校準工具
```

## 配置參數

### 攝影機設定

```python
# config.py
internal_camera_index = 0        # 內鏡頭索引
external_camera_index = 1        # 外鏡頭索引
internal_camera_width = 640      # 內鏡頭解析度
internal_camera_height = 480
external_camera_width = 1280     # 外鏡頭解析度
external_camera_height = 720
```

### AI 模型參數

```python
# 疲勞檢測
default_ear_threshold = 0.25             # 預設 EAR 閾值
mp_detection_confidence = 0.5            # MediaPipe 偵測信心度

# ADAS 分析
yolo_confidence = 0.5                   # YOLO 偵測信心度
lane_departure_threshold = 50           # 車道偏離閾值 (像素)
```

### 錄影設定

```python
# 錄影參數
duration_seconds = 60                   # 錄影時長 (秒)
video_quality = 'medium'                # 影片品質
max_local_files = 10                    # 最大本地檔案數
```

## 開發工具

### 獨立測試

```bash
# 測試各個模組
python driver_monitor.py               # 基礎駕駛監控測試
python improved_driver_monitor.py      # 個人化監控測試
python adas_analyzer.py               # ADAS 功能測試
python cloudinary_uploader.py         # 上傳服務測試
python dashcam_recorder.py           # 錄影功能測試
```

### 系統診斷

```bash
# 完整系統檢查
python scripts/system_check.py

# 攝影機診斷
python scripts/test_cameras.py

# 駕駛員檔案管理
python -c "
from driver_calibration import DriverCalibration
from config import config
cal = DriverCalibration(config)
print(cal.list_driver_profiles())
"
```

## 故障排除

### 常見問題

**Q: 攝影機無法開啟**
```bash
# 檢查攝影機連接
python scripts/test_cameras.py

# 檢查權限 (Linux)
sudo usermod -a -G video $USER
```

**Q: 校準失敗**
```bash
# 確保良好光線
# 檢查攝影機角度
# 重新執行校準
python scripts/calibrate_driver.py --name "您的姓名"
```

**Q: 上傳失敗**
```bash
# 檢查網路連接
# 驗證 Cloudinary 配置
python cloudinary_uploader.py
```

**Q: 頻繁誤報**
```bash
# 重新校準駕駛員檔案
# 檢查環境光線變化
# 調整攝影機位置
```

### 效能優化

1. **Raspberry Pi 優化**
   ```bash
   # 增加 GPU 記憶體
   sudo raspi-config
   # Advanced Options > Memory Split > 128
   
   # 啟用硬體加速
   sudo apt install python3-opencv-headless
   ```

2. **系統監控**
   ```bash
   # 監控系統資源
   python -c "
   from utils import get_system_info
   print(get_system_info())
   "
   ```

## API 參考

### 駕駛員監控

```python
from improved_driver_monitor import AdaptiveDriverMonitor

# 初始化
monitor = AdaptiveDriverMonitor(driver_id="driver_123")

# 分析影像
result = monitor.analyze_frame(frame)

# 獲取警報
alerts = result['alerts']
for alert in alerts:
    print(f"{alert['code']}: {alert['name']} (分數: {alert['score']})")
```

### ADAS 分析

```python
from adas_analyzer import AdasAnalyzer

# 初始化
analyzer = AdasAnalyzer()

# 分析影像 (包含車速和方向燈狀態)
result = analyzer.analyze_frame(frame, speed_kmh=60, 
                               turn_signal_left=False, 
                               turn_signal_right=True)
```

### 雲端上傳

```python
from cloudinary_uploader import CloudinaryUploader

# 初始化
uploader = CloudinaryUploader()
uploader.start()

# 上傳影片
alerts = [{'code': 'A01', 'score': 25}]
uploader.upload_video_segment('video.mp4', alerts)
```

## 更新日誌

### v1.0.0 (2025-08-31)
- 初始版本發布
- 完整的駕駛員監控系統
- ADAS 輔助駕駛功能
- 個人化校準系統
- Cloudinary 雲端整合
- 自動錄影和上傳
