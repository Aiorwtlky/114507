# 🚗 Car Distance Estimation System

使用三顆 IP Camera ＋ YOLOv8n 模型，進行前、中、後方車距即時偵測、警告與紀錄。

---

## 📦 專案結構

car_distance_estimation/
├── main.py                 # 主程式
├── requirements.txt        # 套件需求清單
├── models/
│   └── yolov8n.pt           # YOLOv8 Nano 預訓練模型
├── utils/
│   ├── camera_reader.py     # IP Camera 串流讀取
│   ├── distance_estimator.py# 影像推估距離
│   ├── visualizer.py        # 畫出車框、距離與警告燈泡
│   └── logger.py            # 危險事件紀錄
├── logs/
│   └── warning_log.txt      # 自動產生的警告紀錄
└── README.md                # 本文件
