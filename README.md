
-----

# My Driving God 吾駕仙 - 駕駛行為記錄系統

**一個專為提升大型車輛行車安全，以 AI 影像辨識為核心，實現駕駛行為量化分析與風險管理的智慧平台。**

-----

## 專案背景與動機

[cite\_start]台灣的交通環境常被稱為「交通地獄」 [cite: 104][cite\_start]，其中大型車輛因視野盲區和內輪差造成的死傷事故比例尤其嚴重 [cite: 121, 122][cite\_start]。根據交通部近五年的數據，大型車事故雖僅佔總數不到3%，卻造成了超過13%的死亡案例 [cite: 122]。

[cite\_start]現有的行車記錄器多為事後佐證 [cite: 113][cite\_start]，而先進駕駛輔助系統（ADAS）則專注於偵測車外危險，對於駕駛者本身因疲勞、分心等「人為風險」因素缺乏有效的監測與預防機制 [cite: 113]。

[cite\_start]為填補此一「人因風險」的數據缺口，「My Driving God 吾駕仙」系統應運而生 [cite: 114][cite\_start]。本系統旨在將抽象的「駕駛習慣」轉化為具體的數據與分數，實現事前預防與事後教育的目標，從根本改善風險來源 [cite: 115, 117]。

## 系統目標

[cite\_start]本專案的核心目的在於對「駕駛者」這個最關鍵的角色進行深度理解與正向引導 [cite: 155]，具體目標如下：

1.  [cite\_start]**實現駕駛行為的全面數據化與量化**：透過 AI 影像辨識，將疲勞駕駛、分心、未使用方向燈等行為轉化為結構化數據 [cite: 158, 159, 160]。
2.  [cite\_start]**建立客觀、透明的駕駛安全評分模型**：開發類比特斯拉「安全分數」的機制，讓駕駛與管理者能客觀追蹤改善進度 [cite: 162, 163, 164, 165]。
3.  [cite\_start]**打造個人化的駕駛數據儀表板**：提供駕駛專屬的網頁入口，將「被動監管」轉化為「主動學習」 [cite: 168, 169, 170]。
4.  [cite\_start]**提供車隊管理者高效的數據管理工具**：設計強大的後台，讓管理者能綜觀車隊安全趨勢，進行科學化管理 [cite: 171, 172, 173, 174]。
5.  [cite\_start]**導入AI智慧教練提供深度行車建議**：整合生成式 AI 模型，分析駕駛行為並提供具體、有溫度的改善建議，形成自我改善的閉環 [cite: 176, 177, 178, 179]。

## 系統架構

[cite\_start]本系統採用 AI 邊緣運算架構，主要分為「記錄器端」與「平台伺服器端」兩大部分，透過 `HTTP REST API` 進行通訊 [cite: 345, 347][cite\_start]。所有影像的 AI 辨識與推論皆在車載裝置本地完成，有效降低延遲，實現高即時性 [cite: 347]。

  - **記錄器端 (Device/Edge)**：
      - [cite\_start]**硬體**：以 Raspberry Pi 5B 搭配 Raspberry Pi AI HAT+ (Hailo-8) 作為邊緣運算核心 [cite: 235, 353]。
      - [cite\_start]**軟體**：使用 Flask 框架處理影像串流與本地資料儲存 (SQLite) [cite: 339, 338][cite\_start]，並整合 YOLOv8n、MediaPipe Face Mesh 與 OpenCV 進行即時影像辨識 [cite: 235, 341, 342, 361]。
  - **平台伺服器端 (Cloud/Server)**：
      - [cite\_start]**軟體**：使用 Django 框架搭建後台管理系統 [cite: 334][cite\_start]，搭配 MySQL 資料庫 [cite: 333, 361][cite\_start]。同時整合 Gemini API 提供 AI 智慧教練的建議生成功能 [cite: 335, 361]。
  - **手機應用程式 (Mobile App)**：
      - [cite\_start]提供駕駛員綁定感應卡或手機 NFC 以登入行車記錄器 [cite: 2108, 2105, 2111]。

[cite\_start]*圖說：系統架構圖* [cite: 346]

## 技術棧 (Tech Stack)

| 類別 | 技術 |
| :--- | :--- |
| **硬體** | [cite\_start]Raspberry Pi 5B [cite: 361][cite\_start], Raspberry Pi AI HAT+ (Hailo-8) [cite: 361][cite\_start], IP攝影機 [cite: 240] |
| **記錄器端 (後端)** | [cite\_start]Python, Flask [cite: 361][cite\_start], SQLite [cite: 361] |
| **伺服器端 (後端)** | [cite\_start]Python, Django [cite: 361][cite\_start], Flask [cite: 361][cite\_start], MySQL [cite: 361] |
| **前端** | [cite\_start]HTML, CSS, JavaScript [cite: 361] |
| **AI / 影像處理** | [cite\_start]YOLO v8n [cite: 361][cite\_start], MediaPipe Face Mesh [cite: 361][cite\_start], OpenCV [cite: 361][cite\_start], Gemini API [cite: 361] |
| **開發工具** | [cite\_start]Visual Studio Code [cite: 361][cite\_start], MySQL Workbench [cite: 361][cite\_start], Git/GitHub [cite: 429] |
