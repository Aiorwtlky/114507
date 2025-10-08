# 智慧車隊安全系統 - 後端 API 伺服器 (Smart Dashcam - Backend)

## 1. 專案概述

本專案是「智慧車隊安全系統」的後端 API 伺服器。其核心職責是作為一個中央數據樞紐，負責接收來自邊緣運算裝置（Raspberry Pi）的數據、管理所有結構化資料，並透過一套標準化的 RESTful API，將數據提供給 Web 和 App 兩種前端客戶端使用。

**目前狀態**：專案處於初始開發階段。資料庫綱要（Schema）已設計完成並在開發環境中建立，但資料表中尚無正式內容。

## 2. 核心功能

- **人員與群組管理**：提供對駕駛員、管理員和車隊群組的 CRUD (增刪改查) 操作。
- **裝置管理**：註冊並管理車載硬體裝置（樹莓派）。
- **行程與數據記錄**：
    - 接收並記錄由裝置回報的完整行程資訊。
    - 儲存由 AI 視覺模組分析出的危險事件標籤 (`ai_vision_log`)。
    - 儲存行車記錄影片的雲端存放位置 (`video_record`)。
- **駕駛評分系統**：根據預設的評分標準 (`scoring_standard`)，對已完成的行程進行自動化評分。
- **身份驗證與授權**：透過 Token-based (JWT) 機制，確保 API 的存取安全。
- **自動化後台管理**：內建一個功能完整的 Admin Panel，供系統管理員直接進行數據維護。

## 3. 技術棧 (Technology Stack)

- **主要框架**: Django
- **API 框架**: Django REST Framework (DRF)
- **資料庫**: MySQL 8.0+ (生產環境) / PostgreSQL (備選)
- **資料庫連接器**: PyMySQL
- **程式語言**: Python

## 4. 本地開發環境設定指南

這份指南將引導新的開發者在本機電腦上，從零開始設定並運行後端專案。

### 步驟一：前置作業

1.  **安裝 Git**：確保您的電腦已安裝 Git 版本控制工具。
2.  **安裝 Python**：建議使用 Python 3.9 或更高版本。
3.  **安裝 MySQL**：確保您的電腦已安裝並**正在運行** MySQL 8.0+ 伺服器。
4.  **建立資料庫**：
    * 使用 DBeaver 或其他資料庫管理工具連接到您的本地 MySQL。
    * 建立一個新的、空的資料庫，指令如下：
      ```sql
      CREATE DATABASE my_driving_god CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
      ```

### 步驟二：專案初始化

1.  **Clone 儲存庫**：
    ```bash
    git clone [https://github.com/Aiorwtlky/114507.git](https://github.com/Aiorwtlky/114507.git)
    cd 114507/二評/後端
    ```

2.  **建立並啟用虛擬環境**：
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS / Linux
    # source venv/bin/activate
    ```

3.  **安裝依賴套件**：
    ```bash
    pip install -r requirements.txt
    ```

4.  **設定環境變數**：
    * 將 `.env.example` 檔案複製一份，並重新命名為 `.env`。
    * 打開 `.env` 檔案，填入您本地 MySQL 資料庫的正確密碼。

### 步驟三：資料庫與後台設定

1.  **執行資料庫遷移**：
    * 這個指令會讓 Django 根據 `api/models.py` 的定義，在您空的資料庫中建立所有必要的資料表。
    ```bash
    python manage.py migrate
    ```

2.  **建立後台管理員帳號**：
    ```bash
    python manage.py createsuperuser
    ```
    * 依照提示，輸入您想要設定的管理員使用者名稱、Email 和密碼。

### 步驟四：啟動並驗證

1.  **啟動開發伺服器**：
    ```bash
    python manage.py runserver
    ```

2.  **驗證**：
    * **後台驗證**：打開瀏覽器，訪問 `http://127.0.0.1:8000/admin/`。使用您剛建立的管理員帳號登入。您應該能看到所有資料表的管理介面。
    * **API 驗證**：訪問 `http://127.0.0.1:8000/api/personnel/`。您應該能看到 DRF 的 API 瀏覽介面。

## 5. 專案架構

本專案採用標準的 Django 專案結構，核心邏輯位於 `api` 這個 App 中。

- `manage.py`: Django 命令列工具。
- `my_driving_god_project/`: 專案全域設定資料夾。
    - `settings.py`: 專案的核心設定檔。
    - `urls.py`: 專案的總路由。
- `api/`: 核心應用程式。
    - `models.py`: 資料庫模型定義 (唯一的數據結構來源)。
    - `admin.py`: Django Admin 後台的顯示設定。
    - `serializers.py`: DRF 的序列化器，負責將 Model 轉換為 JSON。
    - `views.py`: API 的核心商業邏輯。
    - `urls.py`: `api` 應用內部的路由設定。

## 6. 核心 API 端點 (初期)

- `POST /api/auth/token`：使用者登入以獲取權杖。
- `GET /api/personnel/`：獲取人員列表。
- `POST /api/trips/start`：(供樹莓派) 開始一個新行程。
- `POST /api/events/dangerous`：(供樹莓派) 上報一個危險事件。
- `POST /api/videos/notify`：(供樹莓派) 通知一段影片已上傳。
- `GET /api/trips/`：(供前端) 獲取行程列表。
