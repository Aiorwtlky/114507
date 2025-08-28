# 114507 My Driving God
本系統為一套**雙平台架構**的智慧交通應用系統，整合：
- Android App（使用 Android Studio 開發）
- Web 平台（使用 Django 建構）
- 共用 Django 後端 API，供前後端與 App 存取

##  系統架構概述
    ┌──────────────┐        ┌──────────────┐
    │  Web 前端    │        │ Android App  │
    └─────┬────────┘        └─────┬────────┘
          │                         │
     HTTP 請求 (JSON)           HTTP 請求 (JSON)
          │                         │
      ┌───▼─────────────────────────▼───┐
      │         Django 後端 API         │
      └──────────┬────────────┬────────┘
                 │            │
       ┌─────────▼───┐   ┌────▼────────┐
       │ 資料庫       │   │ 靜態檔 / 圖片 │
       └─────────┬──┘   └─────────────┘
                 │            
       ┌─────────▼───┐   
       │ 雲端資料庫    │   
       └─────────────┘ 

---

##  技術架構與工具

| 元件 | 技術 |
|------|------|
| Web 後端 | Python + Django |
| API 傳輸格式 | JSON |
| Web 前端 | Django templates（或可改為 Vue/React） |
| App | Android Studio（Java/Kotlin） |
| 跨來源支援 | flask-cors |
| 資料庫 | SQLite /  MySQL/P|

---

##  Android 端設計

- 使用 Retrofit 或 Volley 發送 API 請求
- 所有請求皆透過 JSON 傳遞
- API Base URL 指向 Flask 伺服器
- 請確保 Android 設定了：
  ```xml
  <uses-permission android:name="android.permission.INTERNET" />
