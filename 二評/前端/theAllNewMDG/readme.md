好的，這是一份專為 GitHub 設計的 `README.md` 檔案，它結構清晰，包含了專案介紹、功能、技術棧、如何安裝執行以及專案結構說明。

您可以直接複製以下所有內容並貼到您 GitHub 儲存庫的 `README.md` 檔案中。

-----

# My Driving God 吾駕仙 - 智慧駕駛分析系統

**吾駕仙 (My Driving God)** 是一套專注於駕駛行為的智慧分析系統，旨在補足現行駕駛輔助技術的不足，解決因疲勞、分心等「人因風險」所帶來的潛在威脅。

本專案為國立臺北商業大學資訊管理系的畢業專題，我們期望建立一套能「理解並回應」駕駛狀態的智慧防線，集監控、分析與 AI 教練於一體，透過數據回饋與改善建議，實踐真正以人為本的主動式安全防護。

## ✨ 主要功能

  * **智慧儀表板 (Dashboard)**：整合顯示駕駛分數、違規事件、過往平均數據等核心資訊。
  * **AI 智慧教練 (AI Coaching)**：分析近期駕駛數據，自動生成摘要與個人化的改善建議。
  * **行程報告與地圖 (Trip Reports & Map)**：視覺化呈現單次行程的詳細路徑、時間與事件地點。
  * **群組管理 (Group Management)**：可建立群組、邀請成員，並查看組內成員的駕駛數據概覽。
  * **歷史紀錄 (Historical Data)**：提供所有行程報表、安全報告的查詢與列印功能。
  * **公告與客服系統 (Announcements & Chat)**：方便管理者發布公告，並提供使用者回饋管道。

## 🛠️ 技術棧

  * **後端 (Backend)**: Python, Flask
  * **前端 (Frontend)**: HTML5, CSS3, JavaScript
  * **前端框架/函式庫**: Google Fonts, Font Awesome, GSAP (用於動畫效果)
  * **模板引擎 (Template Engine)**: Jinja2

## 🚀 安裝與執行

請依照以下步驟在您的本機環境中設定並執行此專案。

### 必要條件

  * Python 3.8 或更高版本
  * pip (Python 套件安裝程式)

### 安裝步驟

1.  **複製儲存庫**

    ```bash
    git clone https://github.com/your-username/your-repository-name.git
    cd your-repository-name
    ```

2.  **建立並啟用虛擬環境 (建議)**

      * **MacOS / Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
      * **Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **安裝依賴套件**
    本專案主要依賴 Flask。

    ```bash
    pip install Flask
    ```

4.  **執行應用程式**

    ```bash
    python app.py
    ```

5.  **瀏覽網頁**
    打開您的瀏覽器，前往 `http://127.0.0.1:5000`，您將會看到應用程式首頁。

## 📁 專案結構

```
.
├── app.py              # Flask 主應用程式，包含所有路由邏輯
├── static/             # 存放靜態檔案
│   ├── css/            # CSS 樣式表
│   ├── js/             # JavaScript 檔案
│   └── images/         # 圖片資源
└── templates/          # 存放 HTML 模板
    ├── base.html       # 全站共用的基礎模板 (頁首、頁尾、側邊欄)
    ├── index.html      # 首頁
    ├── login.html      # 登入頁
    ├── dashboard.html  # 儀表板頁面
    └── ...             # 其他所有頁面的 HTML 檔案
```

### 程式碼概覽

  * **`app.py`**: 作為應用程式的核心，使用 Flask 的 `@app.route()` 裝飾器來定義每個 URL 端點對應的功能。它負責處理請求並使用 `render_template()` 函式將後端資料渲染到 HTML 頁面上。
  * **`templates/base.html`**: 這是父模板，定義了網站的共同版面配置。其他模板（如 `index.html`）會使用 `{% extends "base.html" %}` 來繼承它，並透過 `{% block content %}` 等標籤將自己的內容填入。
