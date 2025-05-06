
# 🧠 軟體技術架構與使用流程設計（完整版）

## 📦 系統總覽流程

```
📁 系統啟動
└─ Raspberry Pi 開機 → systemd 啟動主程式（main_detector）
    └─ C++ 程式執行 YOLO 辨識邏輯 + 控制模組
```

## 🎥 影像來源處理模組

```
📷 多路影像來源接收
└─ OpenCV（C++）搭配 FFmpeg 後端
    ├─ rtsp://admin:123456@192.168.100.10/stream1（左鏡頭）
    ├─ rtsp://admin:123456@192.168.100.12/stream1（右鏡頭）
    └─ 本地 USB CAM /dev/video0（測試用）

💡 技術細節：
    ➝ 使用 VideoCapture 呼叫 FFmpeg 擷取影像流
    ➝ 每秒讀取 frame ➝ 傳給 AI 模型進行分析
```

## 🎯 AI 辨識與邏輯模組（C++）

```
🧠 YOLOv5s 模型推論
└─ 載入 ONNX 模型（輕量化）
    ├─ Hailo-8 AI Kit 進行推論加速（搭配 SDK）
    └─ 得出物件框（class、confidence、bbox）

🧠 內輪差區域判斷
└─ 自訂 ROI（危險區）
    ├─ 若人員或車輛進入該區域
    │   └─ 觸發警報流程
    └─ 否 ➝ 持續監控
```

## 📢 GPIO 控制模組（C++）

```
🔊 蜂鳴器 / 燈號觸發
└─ 使用 wiringPi / pigpio 操作 GPIO 腳位
    ├─ 警報 ON ➝ digitalWrite(pin, HIGH)
    ├─ 延遲後自動關閉或持續響
    └─ 可擴充 LED 燈號、方向指示
```

## 🎬 FFmpeg 串流與事件錄影模組

```
🎥 事件錄影：
└─ 當偵測觸發時，C++ 呼叫：
    ffmpeg -i rtsp_url -t 10 -c copy ./record/event_001.mp4

🌐 串流功能（可選）：
└─ 本地 USB CAM 串流推送：
    ffmpeg -f v4l2 -i /dev/video0 -f hls ./static/stream.m3u8
    ➝ 或推送至 RTMP Server 供多用戶觀看

💡 作用：
    - 提供警示影片備存
    - 可延伸 Web 預覽實況畫面
```

## 🌐 API 與前端整合模組（Python Flask）

```
🛰 Flask 伺服器模組
└─ 提供以下功能：
    ├─ /report ➝ 接收事件 POST（來自 C++）
    ├─ /video_feed ➝ 顯示即時畫面（如有串流）
    └─ Web 頁面顯示事件列表、歷史紀錄

📝 事件儲存：
└─ SQLite or JSON
    ├─ 偵測時間
    ├─ 鏡頭位置
    ├─ 類別（人 / 車）
    └─ 狀態（警告 or 清除）
```

## 🔧 容錯與穩定機制

```
🛡 Watchdog
└─ 自訂 C++ 執行緒監控：
    ├─ 若攝影機斷線 ➝ 重啟串流
    ├─ 程式異常 ➝ 自動重啟 main_detector
    └─ 可記錄錯誤 Log 供除錯

🛠 系統保護
└─ 限制記憶體使用與 CPU 使用率
    ➝ 可設定 ulimit 或 background 優先序
```

## 📌 總結：模組角色分工

| 功能類別         | 語言   | 工具 / 函式庫            | 備註                         |
|------------------|--------|---------------------------|------------------------------|
| RTSP 擷取        | C++    | OpenCV + FFmpeg           | 支援多攝影機來源             |
| AI 推論          | C++    | YOLOv5s + Hailo-8 SDK     | 輕量模型，支援即時辨識       |
| 危險區判斷       | C++    | 自訂 ROI 判斷邏輯         | 判斷是否進入警戒區           |
| 控制輸出         | C++    | wiringPi / pigpio         | 控制蜂鳴器與 GPIO 燈號       |
| 事件錄影         | Shell  | FFmpeg                    | 偵測到事件後錄製 10 秒影片  |
| 串流顯示（可選） | Shell  | FFmpeg ➝ RTMP/HLS         | 可讓監控頁觀看現場實況       |
| API 接收         | Python | Flask                     | 顯示畫面與記錄資訊           |
| 資料儲存         | Python | SQLite or JSON            | 本地資料保留，可備份上傳     |
