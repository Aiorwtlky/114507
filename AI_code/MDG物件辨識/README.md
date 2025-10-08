# MDG - 內輪差警示系統

本專案為大型車輛內輪差死角主動即時警示系統，結合 YOLOv8n 物件偵測與 OpenCV 影像處理，部署於 Raspberry Pi 與 Flask 伺服器端。

## 功能特色

- 即時攝影機影像擷取與 YOLOv8n 物件偵測
- 根據內輪差數學模型計算危險區域 ROI
- 判斷物件是否落入危險區域並觸發警示事件
- 事件錄影、截圖與資料同步
- Flask Web 介面提供事件瀏覽與管理

## 環境需求

- Python 3.8+
- ultralytics (YOLOv8n)
- opencv-python
- flask

## 專案架構

請參考專案根目錄下的資料夾與模組劃分。

## 使用說明

1. 安裝必要套件：
pip install -r requirements.txt

2. 啟動邊緣端模組：
python edge_device/run.py

3. 啟動伺服器端
python server/app.py
