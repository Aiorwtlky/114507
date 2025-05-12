# Driver Monitoring System (駕駛狀態監控系統)

本專案為一套基於 OpenCV 的即時駕駛監控系統，可檢測駕駛是否打瞌睡或姿勢異常，適用於行車安全輔助用途。

---

## 專案結構
dms/
├── CMakeLists.txt # 編譯設定檔
├── models/ # 模型檔案（DNN）
│ ├── face_detection.caffemodel
│ ├── face_detection.prototxt
│ ├── eye_state.caffemodel
│ └── eye_state.prototxt
├── src/
│ ├── main.cpp # 主程式
│ ├── camera.cpp/.hpp # 相機擷取模組
│ ├── face_detector.cpp/.hpp # 臉部與眼睛偵測
│ ├── drowsiness_detector.cpp/.hpp # 打瞌睡偵測
│ └── posture_analyzer.cpp/.hpp # 駕駛姿態分析
└── README.md # 本文件

---

## 依賴與編譯方式

### 依賴項目

- CMake ≥ 3.10
- C++14 支援的編譯器（如 g++）
- OpenCV ≥ 4.x

### 編譯步驟

```bash
mkdir build
cd build
cmake ..
make

