# 專案交接文件：吾駕仙智慧交通系統

**文件版本**：2.2
**更新日期**：2025-10-04

## 1. 專案總覽

[cite_start]「吾駕仙」是一套專注於駕駛行為的智慧分析系統，旨在透過即時監控、數據分析與 AI 回饋，提升職業駕駛員的行車安全 。

[cite_start]本專案採用前後端分離的架構 ：
-   [cite_start]**後端 (Backend)**：使用 **Django REST Framework** 開發，負責處理所有商業邏輯、資料庫互動、使用者認證、權限管理以及與 AI 服務的溝通 。
-   [cite_start]**前端 (Frontend)**：使用 **Flask** 框架作為伺服器，負責渲染使用者介面 (UI) 和處理與後端 API 的通訊 。

## 2. 技術棧

| 類別 | 技術/函式庫 | 用途 |
| :--- | :--- | :--- |
| **後端** | Django, Django REST Framework | [cite_start]核心框架，建構 RESTful API  |
| | djangorestframework-simplejwt | [cite_start]使用者認證 (JWT Token)  |
| | MySQL / PostgreSQL | [cite_start]資料庫 (由 `.env` 設定)  |
| | django-environ | [cite_start]環境變數管理  |
| | Hugging Face InferenceClient | [cite_start]AI 聊天與建議生成服務  |
| | WeasyPrint | [cite_start]動態生成 PDF 安全報告  |
| | Pillow | [cite_start]圖片處理 (用於頭像上傳)  |
| **前端** | Flask | [cite_start]網頁伺服器與模板渲染  |
| | Jinja2 | [cite_start]模板引擎  |
| | requests | [cite_start]與後端 API 通訊  |
| | HTML5 / CSS3 / JavaScript | [cite_start]使用者介面  |
| | Chart.js | [cite_start]數據視覺化圖表  |
| **環境** | Python (venv) | [cite_start]虛擬環境  |
| | pip | [cite_start]套件管理  |

## 3. 後端 (Django) 架構與現況

### 3.1. 資料庫模型 (`api/models.py`)

[cite_start]核心資料庫結構如下 ：

-   **使用者與權限**：
    -   [cite_start]`User`: Django 內建使用者模型 。
    -   [cite_start]`PersonnelProfile`: 一對一擴充 `User`，包含頭像 (`avatar`)、電話、駕照等級等 。
-   **群組與角色**：
    -   [cite_start]`Group`: 定義一個群組，包含 `created_by` 欄位來標示「群組建立者」。
    -   [cite_start]`GroupMember`: 作為 `User` 和 `Group` 之間的多對多關聯橋樑。**擁有 `role` 欄位**，區分 `MEMBER` (一般成員) 和 `ADMIN` (群組管理員) 。
    -   [cite_start]`InvitationCode`: 用於儲存有時效性、一次性的群組邀請碼 。
-   **核心數據**：
    -   [cite_start]`Trip`: 記錄每一趟行程的完整資訊 。
    -   [cite_start]`AiVisionLog`: 記錄行程中的 AI 視覺偵測事件 。
    -   [cite_start]`VideoRecord`: 記錄影片相關資訊 。
-   **其他**：
    -   [cite_start]`GroupAnnouncement`: 儲存群組內的公告 。

### 3.2. 核心 API 端點 (`api/urls.py` & `api/views.py`)

| 功能模組 | HTTP 方法 | 端點 | 說明與權限 |
| :--- | :--- | :--- | :--- |
| **認證** | `POST` | `/api/token/` | [cite_start]使用者登入，獲取 JWT Token 。 |
| | `POST` | `/api/auth/register/` | [cite_start]註冊新使用者，支援**頭像上傳**與**邀請碼** 。 |
| | `GET`, `PATCH` | `/api/auth/profile/` | [cite_start]讀取/更新個人資料。回傳包含 `is_group_leader` 和 `administered_groups` 列表 。 |
| **群組管理** | `POST` | `/api/groups/` | [cite_start]建立新群組，會自動將建立者設為第一位成員 。 |
| | `GET` | `/api/me/groups/` | [cite_start]獲取當前使用者**所屬或建立**的所有群組列表 。 |
| | `GET` | `/api/groups/<id>/members/` | [cite_start]獲取群組成員列表 (含平均分、**角色**與**頭像**路徑) 。 |
| | `POST` | `/api/groups/<id>/invitations/` | [cite_start]**群組建立者或管理員**可為群組生成邀請碼 。 |
| | `PATCH` | `/api/groups/<gid>/members/<uid>/role/` | [cite_start]**群組建立者或管理員**可變更成員角色 。 |
| **公告管理**| `GET` | `/api/groups/<id>/announcements/` | 獲取特定群組的公告列表。 |
| | `POST` | `/api/groups/<id>/announcements/` | [cite_start]**群組建立者或管理員**可發布公告 。 |
| | `GET`, `PUT`, `DELETE`| `/api/announcements/<id>/` | 讀取、更新、刪除單則公告。 |
| **數據查詢** | `GET` | `/api/trips/`, `/api/videos/` | [cite_start]獲取行程/影片列表 (支援 `?user_id=` 參數) 。 |
| **AI 功能** | `POST` | `/api/chatbot/` | [cite_start]AI 智慧客服 。 |

## 4. 前端 (Flask) 架構與現況

### 4.1. 核心邏輯 (`app.py`)

-   [cite_start]**`make_api_request()`**: 作為 API 請求的統一出口，自動處理 `Authorization` 標頭和 JWT Token 的過期刷新 。
-   **登入與跳轉邏輯**:
    -   [cite_start]**群組建立者** (`is_group_leader: true`) 登入後，會被 `admin_logic_redirect` 直接導向到功能最完整的 `group_leader_view` 。
    -   [cite_start]**被指派的管理員** (`role: 'ADMIN'`) 登入後進入個人 `dashboard`，儀表板上會額外顯示「群組管理面板」，提供管理功能的快速入口 。
    -   [cite_start]**一般使用者** (`role: 'MEMBER'`) 登入後一律進入 `dashboard` 。

### 4.2. 已完成的主要功能與使用者流程

-   [cite_start]**使用者註冊**：支援包含頭像上傳的完整註冊流程 。
-   **登入/登出**：基於 JWT 的完整認證機制。
-   **雙層級權限系統**：
    1.  [cite_start]**群組建立者 (`created_by`)**：擁有群組的最高權限 。
    2.  [cite_start]**群組管理員 (`ADMIN`)**：由建立者指派，擁有大部分管理權限（如邀請成員、發布/刪除公告）。
-   **群組管理**：
    -   [cite_start]群組建立者可以建立群組、指派管理員 。
    -   [cite_start]建立者與管理員可以生成邀請碼邀請新成員 。
-   **儀表板 (`dashboard` & `group_leader_view`)**:
    -   [cite_start]使用者登入後可查看個人資料、所屬群組、行程記錄等 。
    -   [cite_start]組長與管理員有各自的管理入口與介面 。
    -   [cite_start]所有頁面的**頭像皆已動態化**，可正確顯示使用者上傳的圖片 。

## 5. 待辦事項 (下一步開發計畫)

### **計畫一：完成個人資料編輯**
-   **目標**: 讓使用者可以修改自己的個人資料，並上傳新的頭像來覆蓋舊的。
-   **前端串接 (`edit_profile.html`)**:
    -   **GET**: 實作 `edit_profile` 路由，載入頁面時呼叫 `GET /api/auth/profile/` API，將使用者當前的資料預先填入表單。
    -   **POST**: 當使用者提交表單時，收集所有文字資料和**可能上傳的新頭像檔案**，以 `multipart/form-data` 格式 `PATCH` 到 `/api/auth/profile/` 端點。
-   **後端測試**:
    -   後端 `UserProfileAPIView` 已具備接收 `PATCH` 請求的功能，主要任務是配合前端進行串接測試，確保能正確處理包含圖片的更新請求。

### **計畫二：完成公告管理功能**
-   **目標**: 讓組長與管理員可以「編輯」與「刪除」已發布的公告。
-   **前端串接 (`group_leader_view.html` & `create_announcement.html`)**:
    -   **刪除功能**: 為「垃圾桶」圖示加上 JavaScript 事件或表單，點擊後跳出確認對話框，確認後呼叫後端 `DELETE /api/announcements/<id>/`。
    -   **編輯功能**: 將「鉛筆」圖示改為連結，點擊後跳轉到公告編輯頁面 (`create_announcement.html`)，並預先填入該公告的現有內容。提交後呼叫後端 `PUT /api/announcements/<id>/`。
-   **後端測試**:
    -   後端 `GroupAnnouncementDetailAPIView` 已提供 `PUT` 和 `DELETE` 方法，且權限已設定為允許組長與管理員操作。主要任務是配合前端進行串接測試。

### **其他待辦事項**
-   **前端**:
    -   [cite_start]實現 `dashboard.html` 中「近期行程」的點擊跳轉功能 (連到 `trip_report` 路由) 。
    -   [cite_start]完成 `member_dashboard.html` 等使用者詳情頁面的開發 。
-   **後端**:
    -   [cite_start]為刪除成員等敏感操作增加後端 API 。
-   **測試**:
    -   [cite_start]為後端的 `api/` app 編寫單元測試與整合測試 (`tests.py` 目前為空) 。