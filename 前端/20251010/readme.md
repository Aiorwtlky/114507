MDG Pro - 前端平台 (Frontend Platform)
1. 總覽
本系統是使用者（駕駛員、車隊管理者）與 MDG Pro 平台互動的主要介面。採用 Flask 作為網頁伺服器，原生 JavaScript 作為前端動態功能的驅動核心。

其架構為標準的前後端分離模式，所有頁面內容皆透過 fetch API 向後端請求 JSON 資料，並在瀏覽器端進行動態渲染。

2. 系統架構圖
graph LR
    A[使用者] -- 操作 --> B[瀏覽器];
    subgraph Browser
        C[HTML 骨架]
        D[CSS 樣式]
        E[JavaScript 邏輯]
    end
    B <--> C;
    B <--> D;
    B <--> E;
    
    E -- fetchWithAuth(Token) --> F[後端 API];
    F -- 回傳 JSON 資料 --> E;
    E -- 更新/渲染 --> C;

