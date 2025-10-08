streamlit run app/streamlit_app.py

# Driver Drowsiness Detection using Mediapipe in Python

本專案利用 Mediapipe 的 Face Mesh 技術結合 OpenCV，實現駕駛疲勞偵測系統。  
系統透過計算眼睛張開比例（Eye Aspect Ratio, EAR）判斷駕駛是否疲勞，並提供即時影像串流與警報。

---

## 主要功能

- 使用 Mediapipe 偵測臉部與眼睛關鍵點
- 計算 EAR 值判斷眼睛是否閉合
- 透過 Streamlit 建立簡易網頁介面調整參數與顯示結果
- 即時影像串流與警報聲音提示
- 輕量化設計，適合嵌入式與邊緣運算平台

---

## 專案架構
DD/
├── app/
│ └── streamlit_app.py # Streamlit 網頁入口程式
├── detection/
│ ├── drowsy_detection.py # Mediapipe 與疲勞偵測邏輯
│ ├── audio_handling.py # 警報音效處理
│ └── init.py # 模組初始化檔 (可空)
├── assets/
│ ├── audio/
│ │ └── wake_up.wav # 警報音效檔
│ └── images/
│ ├── test-open-eyes.jpg # 測試用圖片
│ └── test-close-eyes.jpg # 測試用圖片
├── requirements.txt # 依賴套件列表
└── README.md # 專案說明文件

---

## 安裝與執行

1. 安裝 Python 3.7 以上版本  
2. 安裝依賴套件  
   ```bash
   pip install -r requirements.txt
