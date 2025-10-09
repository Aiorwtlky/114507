# 吾駕仙 - AI 駕駛行為分析模擬器 (含硬體互動原型)
**WuJia-Xian - AI Driver Behavior Analysis Simulator (with Hardware Interaction Prototype)**

本專案是「吾駕仙」系統的桌面端全功能原型模擬器。它透過一個以 PySide6 建構的圖形化介面，完整展示了系統的核心能力，包括讀取內部與外部行車影像進行即時 AI 分析、提供動態視覺化回饋，並透過鍵盤模擬硬體互動（NFC 登入、方向燈訊號）。

![UI Screenshot](https://i.imgur.com/39w8X93.png)
*(專案運行示意圖)*

## 核心功能 (Features)

- **雙模式智慧切換介面 (Dual-Mode GUI)**:
    - **內部偵測模式**: 分析駕駛員的疲勞與分心狀態。
    - **外部偵測模式**: 分析前方路況與駕駛行為。
    - 包含主影像顯示區、即時事件警示列，以及駕駛員登入狀態列。

- **硬體模擬系統 (Hardware Simulation)**:
    - **NFC 刷卡模擬**: 使用鍵盤 `n` 鍵模擬駕駛員透過 NFC 進行登入與登出。
    - **模式切換模擬**: 使用鍵盤 `Tab` 鍵在「內部偵測」與「外部偵測」模式間循環切換。
    - **方向燈 GPIO 模擬**: 使用鍵盤 `l` 和 `r` 鍵**按住時開啟、放開時關閉**來模擬左、右方向燈訊號。

- **模組化 AI 事件偵測器 (Modular AI Event Detectors)**:
    - **疲勞偵測 (`advanced_fatigue_detector.py`)**: 透過 MediaPipe 分析眼部開合度 (EAR)、頭部姿態等特徵，實現自動基準線校準，並偵測長時間閉眼 (A01/A02) 與**微睡眠**等危險行為。
    - **分心偵測 (`advanced_distraction_detector.py`)**: 透過多模態分析（手部與臉部相對位置），並引入時間連續性判斷，過濾短暫無害的動作，準確偵測手持通話、操作手機 (A03) 與視線長時間偏離 (A04) 等分心行為。
    - **先進駕駛輔助 (`advanced_adas_detector.py`)**: 使用 YOLOv8 模型偵測前方車輛，判斷未保持安全車距 (B03)，並**結合方向燈模擬訊號**來警示未打方向燈的車道偏離行為 (B01/B02)。

- **多執行緒架構 (Multi-threaded Architecture)**: 核心 AI 分析與硬體監聽在獨立的背景執行緒 (`worker.py`) 中運行，確保圖形化介面永遠保持流暢、不卡頓。

## 檔案架構 (File Structure)

```
wujia_xian_simulator/
├── assets/
│   ├── models/
│   │   └── yolov8n.pt
│   └── videos/
│       └── road_video.mp4
├── event_detectors/
│   ├── __init__.py
│   ├── adas_detector.py
│   ├── distraction_detector.py
│   └── fatigue_detector.py
├── utils/
│   └── api_client.py
├── main.py               # 程式主入口，請執行此檔案
├── main_window.py        # Qt 主視窗 UI 定義
├── worker.py             # 背景影像處理與硬體整合執行緒
├── dummy_gpio.py         # 鍵盤模擬 GPIO 硬體的模組
├── config.ini            # 專案設定檔
├── requirements.txt      # 依賴套件列表
└── README.md
```

## 安裝與設定 (Installation & Setup)

**1. 複製專案並進入目錄**
```bash
git clone <your-repository-url>
cd wujia_xian_simulator
```

**2. 建立 Python 虛擬環境並啟用**
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**3. 建立 `requirements.txt` 檔案**

在專案根目錄手動建立一個名為 `requirements.txt` 的文字檔，並將以下內容貼入：
```
PySide6
opencv-python
mediapipe
ultralytics
numpy
pynput
scipy
scikit-learn
```

**4. 安裝依賴套件**
```bash
pip install -r requirements.txt
```

**5. 放置資源檔案**
- **模型**: 請將預先下載好的 `yolov8n.pt` 模型檔放入 `assets/models/` 資料夾。
- **影片**: 將您的外部攝影機展示影片 (e.g., `road_video.mp4`) 放入 `assets/videos/` 資料夾。

**6. 設定 `config.ini`**
打開 `config.ini` 檔案，確保外部影片的路徑設定正確：
```ini
[DataSource]
road_video_path = assets/videos/road_video.mp4
```

## 如何執行與互動 (How to Run & Interact)

**1. 執行程式**

在已啟用虛擬環境的終端機中，於專案根目錄執行以下指令：
```bash
python main.py
```

**2. 互動操作**

程式執行後，會彈出 GUI 視窗。**請先用滑鼠點擊一下視窗，確保焦點在應用程式上**，然後您就可以使用鍵盤來模擬硬體事件：

- **`n` 鍵**: 模擬 **NFC 刷卡**，用於駕駛員**登入/登出**。
    - 第一次按下：登入，影像分析開始。
    - 第二次按下：登出，影像分析暫停。

- **`Tab` 鍵**: 在**「內部偵測」**與**「外部偵測」**兩種模式之間切換。

- **`l` 鍵**: **按住**以開啟左方向燈，**放開**以關閉。

- **`r` 鍵**: **按住**以開啟右方向燈，**放開**以關閉。

- **退出程式**: 直接點擊視窗的**關閉按鈕**即可安全退出程式。