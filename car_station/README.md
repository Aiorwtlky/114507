# Car Station Dashboard 車機影像辨識系統

## 📦 簡介

本專項為一個部署於車機端的多鏡頭影像辨識系統，使用 Flask 製作前後端介面，  
搭配 Raspberry Pi 與 USB / IP CAM，實現三畫面顯示、警示狀態互動、安裝設定流程與資訊顯示功能。  
設計風格統一，背景採用奶茶系柔色調，支援觸控與全螢幕 Kiosk 模式使用。

---

## 💥 Mac 開發階段（本機測試）

1. 進入專項資料夾：

   ```bash
   cd car_station
   ```

2. 安裝必要套件：

   ```bash
   pip3 install -r requirements.txt
   ```

3. 啟動伺服器（可指定 port）：

   ```bash
   python3 app.py
   ```

4. 瀏覽器開啟： [http://localhost:5001](http://localhost:5001)

---

## 🍓 Raspberry Pi 部署方式

1. 傳送整個資料夾至樹莓比：

   ```bash
   scp -r ./car_station pi@<Pi_IP>:/home/pi/
   ```

2. 連線進入 Raspberry Pi 並切換目錄：

   ```bash
   ssh pi@<Pi_IP>
   cd car_station
   ```

3. 安裝必要套件：

   ```bash
   pip3 install -r requirements.txt
   ```

4. 啟動伺服器（背景執行可另行設定 systemd）：

   ```bash
   python3 app.py
   ```

5. 啟動全螢幕 Kiosk 模式（建議使用 Chromium）：

   ```bash
   chromium-browser --noerrdialogs --disable-infobars --kiosk http://localhost:5001
   ```

---

## 📂 專項目錄結構

```
car_station/
├── app.py                     # 主伺服器程式
├── camera_config.py          # 鏡頭 URL 與預設設定
├── init_db.py                # 建立 SQLite 資料庫
├── requirements.txt
├── README.md
├── templates/
│   ├── index.html            # 主畫面
│   ├── install.html          # 安裝設定頁面
│   ├── install_success.html  # 安裝成功提示頁
│   ├── reset_success.html    # 重設成功提示頁
├── static/
│   ├── css/
│   │   ├── style.css         # 主畫面樣式
│   │   ├── install.css       # 安裝畫面樣式
│   │   └── transition_page.css # 跳轉提示樣式（圈圈動畫+ 倒數）
│   └── js/
│       ├── script.js         # 主畫面控制邏輯
│       └── transition_page.js # 跳轉頁倒數動畫
├── routes/
│   ├── install.py            # 安裝流程後端
│   ├── device.py             # 裝置資訊查詢 API
│   └── reset.py              # 重設裝置資料 API
└── device.db                 # SQLite 資料庫（安裝後自動產生）
```

---

## ✨ 系統功能特色

1. **三畫面鏡頭顯示（左／後／右）**  
   支援 RTSP / USB 攝影機輸入，並以 Grid Layout 並排顯示，預設「左大右疊」模式。

2. **狀態切換按鈕與互動動畫**  
   按下「左燈 / 右燈 / 倒車」按鈕時，畫面動態切換主畫面為該方向攝影機，附狀態提示欄。

3. **裝置資訊查看與重設**  
   主畫面可隊時開啟裝置資訊視窗，顯示裝置序號、車牌與安裝狀態，並提供一鍵重設功能。

4. **首次開機安裝設定頁面**  
   系統啟動若偵測未完成設定，將自動跳轉至 `/install` 進行車輛資料輸入。

5. **跳轉提示動畫頁**  
   提供安裝成功與重設成功提示頁，內含圈圈動畫與倒數 3 秒自動跳轉 UX。

6. **Kiosk 全螢幕支援**  
   支援 Chromium 無框啟動，可部署於車機上實現開機即用。

---

## 🔧 其他提醒

- 請確保 `camera_config.py` 中的鏡頭來源（CAMERA_URLS）已依現場環境配置完成
- 若部署於 Linux 環境建議設定 `systemd` 開機自動執行 `app.py`
- 若需支援多臺設備，可擴充 SQLite 結構或改為 REST API 中央伺服端統一管理

---

## 🧑‍💻 開發者資訊

由 [NTUB 資管系第114507組] 開發  
作者群：吳佳憲、李冠彣、吳柏丞、黃庭毅、陳廷軒  
開發時程：2025 年 2 月 ～ 2025 年 10 月

