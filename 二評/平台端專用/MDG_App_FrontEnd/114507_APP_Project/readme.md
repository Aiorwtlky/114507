# 智慧行車記錄器系統 (MDG-App) - 前後端交接文件

## 1. 專案概覽

本專案為一個智慧行車安全管理系統的 Android 客戶端 App。系統主要服務兩種角色：**駕駛員**與**管理者**，旨在透過 AI 視覺辨識、行程記錄與數據分析，提升駕駛安全與車隊管理效率。

前端目前已完成所有主要功能的 UI/UX 實作與畫面流程，並使用模擬數據 (Mock Data) 進行畫面呈現。後端工程師的主要任務是開發對應的 API，以真實數據取代前端的模擬數據。

## 2. 前端技術棧

* **語言**: [Kotlin](https://kotlinlang.org/)
* **UI 框架**: [Jetpack Compose](https://developer.android.com/jetpack/compose)
* **架構模式**: MVVM (Model-View-ViewModel)
* **導覽**: [Jetpack Navigation](https://developer.android.com/guide/navigation)
* **非同步處理**: Kotlin Coroutines & Flow

## 3. 核心功能模組

系統依使用者角色分為兩大功能主軸：

### 駕駛員 (Driver)

* **主頁儀表板**: 顯示個人即時駕駛分數、平均分數與分數趨勢圖。
* **歷史數據儀表板**: 查看個人長期的彙總數據，如總里程、總時長、生涯平均分、風險行為分析等。
* **行程報表**: 查看歷史行程列表及單一行程的詳細報告（包含路線圖、危險事件紀錄等）。
* **帳號管理**: 管理個人資料、App 設定與登出。
* **公告查看**: 查看由管理者發佈的公告。
* **QR Code 打卡**: 模擬上班打卡功能。
* **行駛軌跡 (開發中)**: 顯示即時行車地圖與數據。

### 管理者 (Manager)

* **主頁儀表板**: 顯示所屬團隊的宏觀數據，如團隊平均分、在線人數、今日異常等。
* **歷史數據儀表板**: 查看團隊的彙總數據、駕駛員表現排名與團隊風險趨勢分析。
* **群組管理**:
    * 查看群組設定與組內成員列表。
    * 管理群組資訊（名稱、組長等）。
    * 新增成員（透過 QR Code 或邀請連結）。
    * 查看單一成員的詳細數據。
* **公告管理**:
    * 查看已發佈的公告列表。
    * 新增、發佈公告（可選擇即時或排程發佈）。
* **帳號管理**: 管理個人資料與 App 設定。

## 4. 前端畫面與後端 API 需求

這是本文件最重要的部分。以下列出了前端各個畫面期望從後端獲取的數據結構，請後端工程師依此規劃 API 端點 (Endpoint) 與 JSON 格式。

### 4.1 認證 (Authentication)

* **`POST /api/login`**
    * **用途**: 使用者登入。
    * **Request Body**: `{ "username": "...", "password": "..." }`
    * **Response Body**: 成功時回傳使用者基本資訊與 Token，前端需根據回傳的角色 (`role`) 來決定進入駕駛員主頁 (`home`) 或管理者主頁 (`managerHome`)。
        ```json
        {
          "token": "your_auth_token",
          "user": {
            "id": "personnel_id",
            "name": "王大明",
            "role": "driver" // or "manager"
          }
        }
        ```

### 4.2 駕駛員 App

* **`GET /api/driver/profile`**
    * **用途**: 獲取駕駛員個人檔案資料，用於「個人帳號管理」頁面。
    * **Response Body**:
        ```json
        {
          "fullName": "林美麗",
          "employeeId": "D-007",
          "email": "driver.lin@example.com",
          "phone": "0912-345-678",
          "currentVehiclePlate": "ABC-1234",
          "groupName": "總部第一車隊",
          "licenseNumber": "B87654321",
          "licenseClass": "職業大客車",
          "avatarUrl": "[https://example.com/avatar.png](https://example.com/avatar.png)",
          "linkedAccounts": [
            { "platform": "Google", "username": "lin@gmail.com" }
          ],
          "notificationSettings": {
            "receiveDangerousEvent": true,
            "receiveSystemAnnouncements": true,
            "downloadOnlyOnWifi": true
          }
        }
        ```

* **`GET /api/driver/history`**
    * **用途**: 獲取駕駛員「歷史數據儀表板」所需的彙總數據。
    * **Response Body**:
        ```json
        {
          "totalMileage": 12850,
          "totalDurationHours": 315,
          "totalTrips": 241,
          "lifetimeAverageScore": 88,
          "topEvents": [
            { "event": "疲勞駕駛", "count": 15 },
            { "event": "使用手機", "count": 9 }
          ],
          "totalEvents": 29 
        }
        ```

* **`GET /api/announcements`**
    * **用途**: 獲取駕駛員可見的所有公告列表。
    * **Response Body**:
        ```json
        [
          {
            "id": 1,
            "subject": "系統維護通知",
            "content": "...",
            "publishDate": "2025-09-14"
          }
        ]
        ```

### 4.3 管理者 App

* **`GET /api/manager/dashboard`**
    * **用途**: 獲取管理者主頁儀表板的即時數據。
    * **Response Body**:
        ```json
        {
          "onlineDrivers": 15,
          "fleetAverageScore": 82,
          "tripsToday": 128,
          "eventsToday": 3
        }
        ```

* **`GET /api/manager/history`**
    * **用途**: 獲取管理者「歷史數據儀表板」的彙總數據。
    * **Response Body**:
        ```json
        {
          "fleetAverageScore": 82,
          "topRiskFactor": "疲勞駕駛",
          "highRiskDriverCount": 1,
          "criticalEventsThisMonth": 4,
          "bestPerformingDrivers": [
            { "driverId": "D-008", "name": "張偉強", "averageScore": 95 }
          ],
          "driversNeedingAttention": [
            { "driverId": "D-024", "name": "黃小玲", "averageScore": 68 }
          ]
        }
        ```

* **`GET /api/manager/group`**
    * **用途**: 獲取管理者「群組管理」頁面的基本資訊。
    * **Response Body**:
        ```json
        {
          "groupName": "總部第一車隊",
          "unitName": "運輸部",
          "leaderName": "王大明",
          "members": [
            {
              "id": "MGR-001",
              "avatarUrl": "...",
              "memberId": "MGR-001",
              "name": "王大明",
              "averageScore": 92,
              "joinDate": "2024-01-15"
            },
            {
              "id": "D-007",
              "avatarUrl": "...",
              "memberId": "D-007",
              "name": "林美麗",
              "averageScore": 84,
              "joinDate": "2024-03-22"
            }
          ]
        }
        ```

* **`POST /api/manager/announcements`**
    * **用途**: 管理者發佈新公告。
    * **Request Body**:
        ```json
        {
          "subject": "新的公告主旨",
          "content": "這是公告的詳細內容。",
          "isScheduled": true,
          "scheduledDate": "2025-10-01" 
        }
        ```
    * **Response Body**: `201 Created` 或成功訊息。

## 5. 資料庫綱要回顧

所有前端的資料模型 (位於 `app/src/main/java/com/example/mdgapp/data/model/`) 皆是基於先前提供的 `my_driving_god` SQL schema 進行設計。該 SQL 檔案應作為後端資料庫建置的唯一參考標準。

## 6. 專案結構 (前端)

後端工程師在需要時，可參考以下前端專案的關鍵目錄結構：

* `app/src/main/java/com/example/mdgapp/data/model/`: 存放所有資料類別 (Data Class)，是前後端溝通的 JSON 格式基礎。
* `app/src/main/java/com/example/mdgapp/data/viewmodel/`: 存放所有畫面的 ViewModel，負責業務邏輯與狀態管理。
* `app/src/main/java/com/example/mdgapp/ui/screen/`: 存放各個獨立的畫面 (Screen) Composable。
* `app/src/main/java/com/example/mdgapp/ui/component/`: 存放可在多個畫面間重用的 UI 元件。
* `app/src/main/java/com/example/mdgapp/navigation/AppNavGraph.kt`: 定義了所有畫面的導覽路徑與流程。

7. API 錯誤回應格式

為了讓前端能一致處理錯誤情境，建議後端所有 API 在發生錯誤時使用統一的錯誤回傳格式：

{
  "status": "error",
  "code": "INVALID_TOKEN",
  "message": "Token 已失效，請重新登入。"
}

常見錯誤碼範例

INVALID_TOKEN: Token 無效或過期

UNAUTHORIZED: 使用者無權限存取該資源

NOT_FOUND: 找不到指定的資源

VALIDATION_ERROR: 參數驗證錯誤

SERVER_ERROR: 伺服器內部錯誤

8. 認證與授權

登入機制: 使用 JWT (JSON Web Token)。

Token 傳遞方式: 前端每次呼叫 API 時，需在 Header 中帶入：

Authorization: Bearer <token>


Token 有效時間: 例如 2 小時 (由後端設定)。

Refresh 機制: 可規劃 POST /api/refresh 來換取新 Token，避免頻繁登入。

9. 日誌與監控

為了方便後端與運維追蹤系統狀況，建議後端實作以下功能：

API Log: 記錄所有 API 呼叫的時間、參數、回應狀態。

錯誤追蹤: 使用如 Sentry 或 ELK Stack 追蹤異常。

駕駛行為事件紀錄: 除了前端呈現，也應存入資料庫，供日後分析與審查。

10. API 版本控管

考量到未來功能擴充，建議在 API 路徑加上版本號：

範例：/api/v1/driver/profile

未來若有變動，可新增 /api/v2/...，而不影響舊版本使用者。

11. 前後端協作流程建議

Mock API 驗證: 後端可先提供 Swagger 或 Postman Collection，讓前端驗證資料格式。

CI/CD 測試環境: 建立測試環境 API，前端能即時驗證功能是否正確。

資料一致性: 前後端以 app/src/main/java/com/example/mdgapp/data/model/ 的資料模型為準，任何異動需同步更新。

12. 未來擴充方向

AI 視覺模組串接: 後端需規劃上傳行車影像與分析結果的 API，例如：

POST /api/driver/events
Content-Type: multipart/form-data


用於上傳危險事件的影像與 AI 偵測結果。

通知系統: 透過 WebSocket 或 Firebase Cloud Messaging (FCM) 實現即時推播，例如：危險駕駛警告、公告通知。

多語系支援: API 建議保留多語系欄位（如公告 subject_en, subject_zh），前端可根據使用者語系切換。

13. 資料安全性

使用 HTTPS (TLS 1.2 以上) 加密所有傳輸。

密碼需經過雜湊 (建議 bcrypt 或 Argon2)，不可明碼存放。

重要隱私資料（如駕照號碼、電話）需有存取權限控管。

14. 檔案上傳規範

上傳檔案格式：.jpg, .png, .mp4。

單檔大小上限：影像 20MB，圖片 5MB。

檔案需存放至 CDN 或雲端儲存，API 回傳檔案 URL。

15. 系統時區與格式

系統統一使用 UTC+8 (台北時區)。

所有時間以 ISO 8601 格式回傳：2025-10-05T14:30:00+08:00。

16. 分頁與查詢

列表型 API 須支援分頁參數：

page: 當前頁數 (預設 1)

pageSize: 每頁筆數 (預設 20, 最大 100)

Response Body 範例：

{
  "total": 125,
  "page": 1,
  "pageSize": 20,
  "items": [ ... ]
}

17. 測試帳號與範例資料

建議後端建立 測試帳號：

駕駛員帳號：driver@test.com / 123456

管理者帳號：manager@test.com / 123456

系統啟動後，預先插入部分測試數據（公告、歷史行程、群組成員）。

18. 部署與環境規劃

開發環境: dev.api.mydrivinggod.com

測試環境: staging.api.mydrivinggod.com

正式環境: api.mydrivinggod.com

建議使用 Docker 與 CI/CD 自動化部署。