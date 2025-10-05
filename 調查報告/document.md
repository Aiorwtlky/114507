
---

## **吾駕仙智慧交通系統 - 專案交接文件**

**文件版本**: 4.0 (後端 API 開發完成版)
**更新日期**: 2025-10-05

### 1. 專案總覽

「吾駕仙」是一套專注於駕駛行為的智慧分析系統，旨在透過即時監控、數據分析與 AI 回饋，提升職業駕駛員的行車安全。

本專案採用前後端分離的架構：
* **後端 (Backend)**：使用 **Django REST Framework** 開發，負責處理所有商業邏輯、資料庫互動、使用者認證、權限管理以及與外部 AI 服務的溝通。
* **前端 (Frontend)**：使用 **Flask** 框架作為伺服器，負責渲染使用者介面 (UI) 和處理與後端 API 的通訊。

### 2. 技術棧

| 類別 | 技術/函式庫 | 用途 |
| :--- | :--- | :--- |
| **後端** | Django, Django REST Framework | 核心框架，建構 RESTful API |
| | djangorestframework-simplejwt | 使用者認證 (JWT Token) |
| | MySQL / PostgreSQL | 資料庫 (由 `.env` 設定) |
| | django-environ | 環境變數管理 |
| | Hugging Face InferenceClient | AI 聊天與建議生成服務 |
| | WeasyPrint | 動態生成 PDF 安全報告 |
| | Pillow | 圖片處理 (用於頭像上傳) |
| **前端** | Flask | 網頁伺服器與模板渲染 |
| | Jinja2 | 模板引擎 |
| | requests | 與後端 API 通訊 |
| | HTML5 / CSS3 / JavaScript | 使用者介面 |
| | Chart.js | 數據視覺化圖表 |
| **環境** | Python (venv) | 虛擬環境 |
| | pip | 套件管理 |

### 3. 後端 (Django) 最終狀態

#### 3.1. 資料庫模型 (`api/models.py`)

所有資料庫模型皆已設計並遷移完成。關鍵模型與欄位包含：
* `PersonnelProfile`: 新增 `nfc_card_id` 欄位，用於綁定駕駛員的 NFC 卡。
* `Trip`: 新增 `in_car_score` 和 `out_car_score` 欄位，用以儲存獨立的車內/車外評分。
* `VideoRecord`: 新增 `video_url` 欄位，用於儲存影片在雲端儲存上的網址。
* `TripSuggestionFeedback`: 新增的模型，用於儲存駕駛員對 AI 行程建議的回饋。
* `ScoringStandard`: 沿用 `event_number` 欄位的前綴（'A'/'B'）來區分車內/車外事件。

#### 3.2. 核心評分邏輯 (`api/services.py`)

`calculate_trip_score` 函式已升級為全新的計分機制：
1.  **時間區間化**: 將整趟行程切分為數個 15 分鐘的區間。
2.  **事件分類**: 根據事件編號 (`event_number`) 的 'A' 或 'B' 前綴，將違規事件歸類為「車內」或「車外」。
3.  **區間計分**: 為每個 15 分鐘區間，獨立計算其車內與車外分數（從 100 分開始扣）。
4.  **最終計分**:
    * 若某類別（如車內）的所有區間分數都 `>= 60`，則該類別的最終分數為**所有區間的平均值**。
    * 若某類別有**任何一個**區間分數 `< 60`，則該類別的最終分數為**所有區間中的最低分**。
5.  **儲存**: 最終的 `in_car_score`, `out_car_score` 及兩者的平均 `score` 會一併存入 `Trip` 模型。

#### 3.3. API 開發現況

**所有後端 API 功能均已開發完畢**。API 功能涵蓋使用者、群組、公告、行程、NFC 綁定與識別、AI 互動與回饋等所有規劃中的功能。詳細列表請參考下方的 Postman 測試指南。

### 4. 核心資料流程：車機端互動 (混合模式)

車機端與後端的互動採用「小資料即時傳輸，大檔案上雲」的混合模式。

1.  **行程開始**:
    * 駕駛員掃描 NFC 卡/手機，車機讀取 NFC ID。
    * 車機呼叫 `GET /api/users/by-nfc/`，用 NFC ID 換取 `user_id`。
    * 車機呼叫 `POST /api/trips/start/`，傳入 `user_id` 等資訊，正式開始行程並獲取 `trip_id`。
2.  **行程中**:
    * 車機偵測到危險事件時，即時呼叫 `POST /api/events/` 回報。
3.  **行程結束**:
    * 車機呼叫 `PATCH /api/trips/<trip_id>/end/`，後端自動觸發計分與 AI 建議生成。
4.  **影片上傳**:
    * 行程結束後，車機將影片檔**直接上傳至 Google Cloud Storage (GCS)**。
    * 上傳成功後，車機呼叫 `POST /api/videos/register/`，將 `trip_id` 和影片在 GCS 上的 `video_url` 告知後端，由後端寫入資料庫。

### 5. 前端 (Flask) 現況與剩餘整合任務

#### 5.1. 已完成的整合

* **核心功能**: 使用者註冊、登入/登出、個人資料編輯、儀表板 (`dashboard`) 皆已完成串接。
* **群組管理**: 組長儀表板 (`group_leader_view`) 的核心功能，包含成員列表、公告管理、邀請成員、權限變更、移除成員等，皆已完成串接。
* **AI 客服**: 聊天室 (`chat`) 頁面已能與後端 AI 進行即時、有上下文的對話，並包含回饋按鈕的初步 UI。

#### 5.2. **待辦事項：** 剩餘頁面串接

以下是前端需要完成的主要整合任務，對應的後端 API 都已準備就緒。

* **任務一：單趟行程詳細報告**
    * **目標頁面**: `safety_report.html`
    * **前端路由**: 需實作 `app.py` 中的 `trip_report(trip_id)` 函式。
    * **需呼叫 API**: `GET /api/trips/<trip_id>/`
    * **任務描述**: 呼叫 API 獲取單趟行程的完整資料（包含新的 `in_car_score`, `out_car_score`），並動態渲染到頁面中。同時，需在 AI 建議 (`ai_suggestion`) 旁加上「有幫助/沒幫助」的回饋按鈕，並將點擊事件串接到 `POST /api/trips/feedback/` API。

* **任務二：成員儀表板**
    * **目標頁面**: `member_dashboard.html`
    * **前端路由**: 需實作 `app.py` 中的 `member_dashboard(member_id)` 函式。
    * **需呼叫 API**:
        * `GET /api/trips/?user_id=<member_id>` (獲取該成員所有行程)
        * `GET /api/statistics/trends/?user_id=<member_id>` (獲取該成員分數趨勢)
    * **任務描述**: 獲取特定成員的駕駛數據總覽並渲染到頁面中。

* **任務三：行車影片頁面**
    * **目標頁面**: `member_videos.html`
    * **前端路由**: 需實作 `app.py` 中的 `member_videos(member_id)` 函式。
    * **需呼叫 API**: `GET /api/videos/?user_id=<member_id>`
    * **任務描述**: 呼叫 API 獲取特定成員的影片紀錄列表，並將 `video_url` 欄位作為影片播放器或下載按鈕的連結。

### 6. Postman 測試指南

為確保後端功能正常，可依循以下流程使用 Postman 進行測試。

1.  **建立環境**: 建立 Postman 環境，並設定變數 `base_url` 為 `http://127.0.0.1:8000`。
2.  **註冊與登入**:
    * **註冊**: `POST {{base_url}}/api/auth/register/` (使用 `form-data`，可選傳 `avatar` 檔案)。
    * **登入**: `POST {{base_url}}/api/token/` (使用 `raw(JSON)`，傳入 `username` 和 `password`)。在 "Tests" 頁籤加入腳本，可自動儲存回傳的 `access_token`。
3.  **測試授權API**:
    * 建立新請求，例如 `GET {{base_url}}/api/auth/profile/`。
    * 在 "Authorization" 頁籤，選擇 Type 為 `Bearer Token`，並在 Token 欄位填入 `{{access_token}}`。
    * 發送請求，應可看到 `200 OK` 及個人資料。後續所有需要登入的 API 皆採用此授權方式。

---
