MDG Pro - 後端系統 (Backend System)
1. 總覽
本後端系統是 MDG Pro 平台的核心中樞，採用 Django 搭配 Django REST Framework (DRF) 建構，資料庫使用 MySQL。其主要職責是處理所有商業邏輯、管理資料庫，並提供一套安全、高效的 RESTful API 供給前端平台與車機端設備使用。

2. 系統架構圖
graph TD
    subgraph Browser & Onboard Device
        A[前端 Web 平台]
        B[車機端設備]
    end

    subgraph Backend Server (Django/DRF)
        C[API Endpoints]
        D[Views]
        E[Serializers]
        F[Services]
        G[Models]
    end

    subgraph Databases & Services
        H[MySQL Database]
        I[Google Gemini AI]
        J[WeasyPrint PDF]
    end

    A -- JSON/API Request --> C
    B -- JSON/API Request --> C
    C <--> D
    D <--> E
    D -- 呼叫商業邏輯 --> F
    F -- 執行計分/生成建議 --> F
    F -- 呼叫外部服務 --> I
    F -- 呼叫外部服務 --> J
    F <--> G
    G <--> H

