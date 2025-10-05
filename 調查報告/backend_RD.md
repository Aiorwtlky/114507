吾駕仙智慧交通系統 - 開發接軌文件 (v3.1)
文件版本: 3.1
目標: 闡明剩餘功能的開發任務分工，確保車機端與後端 API 的順利對接。

1. 總覽與架構 (Overview & Architecture)
我們將採用混合模式進行開發，其核心思想為：
小資料 (Metadata)：如行程開始/結束、駕駛員是誰、危險事件等文字或數字資料，透過 API 即時傳輸。
大檔案 (Large Files)：如行車影片，由車機直接上傳至雲端儲存 (Google Cloud Storage)，再將檔案的網址透過 API 告知後端。
2. 前置作業：NFC 卡片與駕駛員的綁定
此為一次性設定，目的是讓後端資料庫知道「哪張 NFC 卡對應哪位駕駛員」。
後端資料庫狀態:
在 PersonnelProfile 模型中，已包含 nfc_card_id 欄位，用來儲存 NFC 卡的唯一識別碼。
後端 API 任務 (待開發):
開發一支新的 API，供管理者綁定卡片。
Endpoint: PATCH /api/personnel/<user_id>/bind-nfc/
Request Body: { "nfc_id": "ABCDEF1234" }
功能: 後端接收到請求後，找到對應的 user_id，並將 nfc_id 存入其 PersonnelProfile 的 nfc_card_id 欄位。
3. 核心流程：一趟完整行程的生命週期
3.1 開始行程
觸發事件: 駕駛員在車機上掃描自己的 NFC 卡。
車機端任務:
讀取 NFC 卡的唯一 ID。
呼叫新的查詢 API，用 NFC ID 換取駕駛員的 user_id。
拿到 user_id 後，再呼叫已有的 start_trip API，正式開始一趟行程。
後端 API 任務:
【需開發】使用者查詢 API:
Endpoint: GET /api/users/by-nfc/?nfc_id=<NFC_ID>
功能: 後端根據傳入的 nfc_id 查詢 PersonnelProfile 表，回傳對應的 User 資訊。
【已完成】開始行程 API:
Endpoint: POST /api/trips/start/
Request Body: { "personnel": <user_id>, "device": <device_id>, "start_time": "...", "name": "行程名稱" }
3.2 回報事件 (行程中)
觸發事件: 車機上的 AI 模型偵測到危險駕駛行為。
車機端任務: 即時呼叫 events API，回報事件。
後端 API 任務 (已完成):
Endpoint: POST /api/events/
Request Body: { "trip": <trip_id>, "event": <event_type_id>, ... }
3.3 結束行程
觸發事件: 駕駛員熄火或手動結束行程。
車機端任務: 呼叫 end_trip API。
後端 API 任務 (已完成):
Endpoint: PATCH /api/trips/<trip_id>/end/
Request Body: { "end_time": "...", "total_mileage": ... }
3.4 上傳與註冊影片
觸發事件: 行程結束後，車機開始處理影片檔案。
車機端任務:
將影片檔案直接上傳到 Google Cloud Storage (GCS)。
上傳成功後，獲取檔案的 URL。
呼叫新的影片註冊 API，將影片 URL 與行程進行綁定。
後端資料庫狀態:
在 VideoRecord 模型中，已包含 video_url 欄位。
後端 API 任務:
【需開發】影片註冊 API:
Endpoint: POST /api/videos/register/
Request Body: { "trip": <trip_id>, "video_url": "https://gcs...", "file_size": ... }
功能: 在 VideoRecord 表中建立一筆紀錄，將行程與影片的雲端網址關聯起來。
4. 其他待開發 API
4.1 AI 客服回饋儲存
觸發事件: 使用者在聊天室點擊「喜歡/不喜歡」按鈕。
後端 API 任務:
【需開發】回饋儲存 API:
Endpoint: POST /api/chatbot/feedback/
Request Body: { "chat_history": [...], "ai_response": "...", "feedback_type": -1, "comment": "..." }
功能: 將回饋內容存入 ChatbotFeedback 資料表。
5. 前端頁面串接任務
以下頁面所需的主要後端 API 皆已完成，等待前端 (app.py 及對應的 .html) 進行串接開發。
單趟行程詳細報告 (F項):
前端路由: /trip_report/<trip_id>
主要 API: GET /api/trips/<trip_id>/
成員儀表板 (D項延伸):
前端路由: /member_dashboard/<member_id>
主要 API: GET /api/trips/?user_id=<member_id>