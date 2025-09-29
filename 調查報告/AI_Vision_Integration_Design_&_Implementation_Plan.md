# Car Station — AI Vision Integration Design & Implementation Plan

目的
----
把「車機端 (car_station) 的內/外鏡頭事件偵測」整合到現有伺服器（Django `api` app），滿足你的需求：
- 內/外鏡頭各自偵測指定事件（以你提供的評分標準為依據）。
- 車端於行程期間在本地累積事件；於司機按「結束行程」後一次性上傳到伺服器，伺服器計分並生成 AI 建議。
- 支援離線容錯（離線時在本地 queue 儲存並自動重試上傳）。
- 隱私：預設內鏡頭「不上傳原始影像」，外鏡頭影像可上傳到 Cloudinary（選擇由伺服器負責上傳以更安全）。

本文件的讀者
----
具備良好後端與嵌入式/邊緣設備開發經驗（Python/Flask or similar、Django、SQLite、HTTP client、基本前端）。讀完此文件，開發者應能著手實作車機端與伺服器端必要變更。

前提（基於你提供的程式碼與回覆）
- 後端使用 Django (app `api`)，有模型 Trip、AiVisionLog、ScoringStandard、VideoRecord、VehicleDevice 等。認證採 TokenAuthentication。
- 已有 endpoints（api/urls.py）：
  - POST /api/trips/start/  (TripStartAPIView)
  - PATCH/PUT /api/trips/{id}/end/ (TripEndAPIView)
  - POST /api/events/ (AiVisionLogCreateAPIView) — currently supports single-event create
  - POST /api/videos/ (VideoRecordCreateAPIView)
  - Auth: POST /api/auth/login/ returns token
- 車端 (car_station) 使用 Flask blueprint 架構（你原先的 app.py），可新增 blueprints 與 utils。
- 行程啟動：手機掃 QR → 建議手機向伺服器呼叫 TripStartAPIView 建立 trip，取得 trip.id（整合最清楚的做法）。
- 事件粒度：每偵測到一次事件就一筆紀錄（AiVisionLog able to hold each event）。同時也建議上傳 per-trip summary。
- 影像隱私：內鏡頭預設不上傳原始影像；外鏡頭視情況上傳（建議由 server 代上傳到 Cloudinary）。

總體流程（步驟）
1. Trip 開始：
   - 使用者（駕駛）以手機掃 QR，手機呼叫 POST /api/trips/start/（Authenticated）：
     - Request body: fields required by TripStartSerializer (device, personnel, group, start_time, trip_number/name)
     - Server creates Trip, returns trip.id (integer) in response.
   - 車機收到 trip_id（手機可顯示或通過局域網 / BLE / QR payload 同步到車機），並把 current_trip_id 記到本地。

2. 車端偵測事件（內/外鏡頭）
   - Camera blueprint 或 capture service 抓 frame，將 frame 傳給 local inference utility。
   - inference 做判定、去重(debounce)、如果為新事件，寫入本地 SQLite events table（local mdg_car.db）。
   - 若為外鏡頭且需上傳影像，可先把外鏡頭的原始檔儲存在本地 tmp，並標示 event row 中 local_image_path；上傳策略由後端/或車機決定（下面說明）。

3. 行程結束：
   - 司機按車機介面「結束行程」：
     - 車機會：
       1. 呼叫 POST /api/trips/{trip_id}/events/bulk/ （或若你選單筆上傳，對每筆呼叫 /api/events/），將本次 trip 的 events 陣列上傳（包含 metadata 與 cloudinary_url 如果已獲得）。
       2. 呼叫 PATCH /api/trips/{trip_id}/end/ 更新 end_time（TripEndAPIView）。TripEndAPIView 會觸發 calculate_trip_score()，該函式會統計 AiVisionLog 並存 score 及 ai_suggestion。
     - 若網路不可用：把本次上傳任務加入 local upload_queue，排程重試（exponential backoff），直到成功。

建議的 API 與 Payload（符合你的 serializers / urls.py）
- TripStart (已有)
  - POST /api/trips/start/
  - Body (example JSON): { "trip_number":"UUID-or-string", "name":"Trip X", "group": <group_id>, "device": <device_id>, "personnel": <user_id>, "start_time":"2025-09-29T08:00:00Z" }
  - Response: TripDetail (contains id)
- Single AiVisionLog create (existing)
  - POST /api/events/
  - Body (AiVisionLogCreateSerializer):
    {
      "trip": <trip_id>,
      "event": <scoring_standard_id>,
      "timestamp": "2025-09-29T08:10:12Z",
      "event_details": "eye_closed:3.5s",
      "confidence_score": 0.92
    }
- Suggested Bulk events endpoint (recommended to add):
  - POST /api/trips/{trip_id}/events/bulk/
  - Payload:
    {
      "events": [
        { "event": <scoring_standard_id>, "timestamp":"...", "event_details":"...", "confidence_score":0.9, "image_url": "https://..." (optional) },
        ...
      ],
      "summary": { "total_deduction": 45, "counts": {"A01":{"count":1,"points":25}, "B02":{"count":1,"points":15}} }
    }
  - Server action: create AiVisionLog rows in transaction, respond 201 with created count.
  - Rationale: reduces HTTP calls, easier atomicity, simpler retry.

- Video upload (existing)
  - POST /api/videos/ (VideoRecordCreateSerializer) used for longer video records.

Server-side model changes (recommended)
- Add optional `image_url` (TextField nullable) to AiVisionLog to store external image evidence cloud URL.
  - Migration: add field `image_url = models.CharField(max_length=1000, blank=True, null=True)` or TextField.
- Optionally add `uploaded` flags or provenance fields (uploader, local_path) if you want traceability.

Car-side local DB schema (mdg_car.db suggestions)
- trips (local mirror)
  - trip_id TEXT PRIMARY KEY (use server trip.id or trip_number with mapping)
  - driver_id, device_id, start_time, end_time, uploaded BOOLEAN DEFAULT 0
- events
  - id INTEGER PRIMARY KEY AUTOINCREMENT
  - trip_id TEXT (FK to trips.trip_id)
  - camera_type TEXT ('inner'/'outer')
  - event_number TEXT (or server scoring_standard_id if known)
  - event_id_server INTEGER (optional, the server-side ScoringStandard id if known)
  - timestamp DATETIME
  - event_details TEXT
  - confidence_score REAL
  - local_image_path TEXT (nullable)
  - uploaded BOOLEAN DEFAULT 0
- upload_queue
  - id INTEGER PRIMARY KEY
  - trip_id TEXT
  - attempt_count INTEGER
  - last_attempt_at DATETIME
  - next_retry_at DATETIME
  - status TEXT ('pending'|'in-progress'|'failed'|'done')

Debounce / event merging logic (car-side)
- You requested "單一" for continuous events. Implement per-event debounce windows (defaults based on your scoring table):
  - A01 (重度疲勞 關眼>3s) → treat continuous closed-eyes >3s as 1 event; debounce 10s after event end.
  - A02 (中度疲勞 1-3s) → debounce 8s.
  - A03 (低頭/轉頭>5s) → debounce 15s.
  - A04 (使用手機) → debounce 5s.
  - B01/B02/B03 (外部) → debounce 5-8s.
- Implementation approach:
  - For each event_number keep last_event_end_ts. When detection triggers, if within debounce window, ignore. For duration-based detection, start timer when condition met; on condition clearance compute duration and produce single event with duration in event_details.
  - Save event_details to include duration (e.g., "duration:3.6s").

Image handling & Cloudinary (privacy & security)
- Default policy (recommended):
  - Inner camera: do NOT upload raw images. Keep only local evidence (local_image_path) for short retention (e.g., 7 days) and auto-delete.
  - Outer camera: images/frames that are evidence may be uploaded to server; server is responsible for uploading to Cloudinary and returning a secure URL; store that URL in AiVisionLog.image_url.
- Why server-side upload is recommended:
  - Avoid distributing Cloudinary API keys to many devices.
  - Centralize access control, transformations, and storage policies.
- If you prefer device direct upload (faster), use Cloudinary unsigned or signed upload with short-lived signatures served by server; only do this with strong device auth and secure storage of keys or signed URL issuance on demand.

Auth / Device identity
- Use TokenAuthentication (DRF `rest_framework.authtoken`). Flow:
  - Admin creates user accounts or device service account; generate Token.
  - Car uses that Token in Authorization header for API requests: `Authorization: Token <tokenkey>`.
- Recommended enhancement:
  - Issue a device-scoped token or one service account token per vehicle. If desired, implement an endpoint to exchange device credentials for a token (requires secure provisioning).

Server upload & scoring timing concerns
- Ensure TripEnd flow waits for events to have been ingested before calculate_trip_score runs:
  - Option A (recommended): Car uploads events first (bulk), then calls TripEnd (or TripEnd endpoint triggers calculate_trip_score, but only after events exist). Implementation detail: TripEndAPIView currently triggers calculate_trip_score on update; ensure you call TripEnd after the events upload succeeds.
  - If TripEnd is called first, server may compute score before events arrive. If that happens, you need either:
    - TripEnd triggers calculate_trip_score asynchronously with a short delay, or
    - Server supports a re-score endpoint or background worker to re-calc after events insertion.

Retry / offline handling
- On network failure, car stores events and adds trip to upload_queue with exponential backoff strategy (e.g., 1min, 5min, 15min, 1h).
- Ensure persistence across reboots (SQLite-based queue).
- When upload succeeds mark events.uploaded = True and trips.uploaded = True.

Detailed tasks for a developer (prioritized)
1. Server changes (Django `api`)
   - Add `image_url` field to `AiVisionLog` model + migration.
   - Implement optional bulk create endpoint:
     - URL: POST /api/trips/{trip_id}/events/bulk/
     - Serializer: BulkAiVisionLogCreateSerializer (validate events array).
     - View: create all AiVisionLog rows in a transaction, return created count.
   - Ensure AiVisionLogCreateAPIView and new bulk endpoint accept optional `image_url`.
   - Optionally add `uploaded_by`/`provenance` fields if traceability required.
   - Confirm TripEndAPIView ordering: update trip end_time only after events are received OR instruct car to upload events first then call TripEnd.

2. Car-side changes (car_station)
   - Add new blueprint: `blueprints/image_recognition/` with routes:
     - GET /image_recognition/ (status / UI)
     - POST /image_recognition/predict (for manual uploads; optional)
     - POST /image_recognition/capture_and_queue?camera=inner|outer (capture & run inference) — or integrate with existing camera blueprint.
   - Add utils: `utils/image_recognition.py` with:
     - model loading (lightweight models or ONNX quantized).
     - predict_image_from_frame(frame, camera_type) → (event_number, confidence, details)
     - debounce manager
   - Add local DB schema and helpers (sqlite access functions).
   - Add upload client module: `utils/uploader.py` that:
     - Reads upload_queue, attempts POST to server (bulk endpoint), handles authentication, exponential backoff, and marking rows as uploaded.
     - If local images must be uploaded: POST image files to server endpoint (or to server's temp upload endpoint); server will upload to Cloudinary and return URL.
   - Modify camera blueprint: on capture call predict, record event in local DB if new.
   - Add UI change: on End Trip button:
     - Invoke uploader to flush events to server (first upload events, then call TripEnd endpoint).
     - Provide success/failure feedback on screen, but core requirement is background reliability.

3. Devops & config
   - Ensure HTTPS on server (settings.py already supports secure options).
   - Add environment variables for Cloudinary / HF token in server `.env`.
   - Limit permitted CORS origins to deployed domains.

API examples (curl)
- Login:
  curl -X POST https://server/api/auth/login/ -d "username=driver&password=pass"
  → returns token
- Upload events (bulk, recommended):
  curl -H "Authorization: Token <token>" -X POST https://server/api/trips/123/events/bulk/ -H "Content-Type: application/json" -d '{"events":[{...}], "summary": {...}}'
- Trip end:
  curl -H "Authorization: Token <token>" -X PATCH https://server/api/trips/123/end/ -d '{"end_time":"2025-09-29T09:00:00Z"}'

Testing & acceptance
- Unit tests for:
  - Car-side debounce logic (simulate continuous detections).
  - Server bulk endpoint and single create endpoint (validate saved AiVisionLog entries).
  - TripEnd ordering: verify server calculates score including events uploaded immediately before TripEnd.
- Integration tests:
  - Emulate a full trip: start trip → simulated detection events (inner/outer) stored locally → upload events → call TripEnd → assert Trip.score populated and ai_suggestion present.
- Manual verification:
  - Upload sample outer-camera image and ensure server stores image_url (Cloudinary) & AiVisionLog row references it.
  - Confirm inner-camera events do not upload raw images by default.

Security & privacy checklist
- Use HTTPS for all car↔server communications.
- Use TokenAuthentication; limit each token scope (device-specific tokens).
- Do not store inner-camera images on server by default. If evidence images are required, apply anonymization on car before upload (face blur) and limit retention.
- Cloudinary keys: keep on server only; if device direct upload is needed, use signed upload tokens issued by server per request.
- Protect logs and local storage: rotate and purge old images, enforce disk quotas.

Configuration & tunables (place in config.py / environment)
- DEBOUNCE windows per event_number (seconds)
- MAX_UPLOAD_RETRIES / BACKOFF strategy
- IMAGE_RETENTION_DAYS (local)
- UPLOAD_BATCH_SIZE (events per request)
- CLOUDINARY / HF tokens (server env)

Deliverables I will produce next (on your confirmation)
- A. Concrete server patch files (Django):
  - migration to add `image_url` to `AiVisionLog`
  - new serializer & view for bulk events endpoint
  - small view helper for server-side image upload to Cloudinary (if you want server to upload)
- B. Car-side blueprint + utils code skeletons (Flask):
  - blueprints/image_recognition/{__init__.py, routes.py}
  - utils/image_recognition.py (predict + debounce)
  - utils/uploader.py (queue processing & bulk upload)
  - SQL schema migration for local mdg_car.db
- C. Full DESIGN_DOC.md (this file) + a compact TASK CHECKLIST (what to implement first)
- D. Example curl requests and sample payload JSON (in separate file if you want)

Questions / confirmations required from you (short)
1. Do you want me to implement/upload external images via server-side upload to Cloudinary (recommended) or device direct upload? (recommended answer: server-side)
2. Bulk events endpoint OK? (recommended yes)
3. Do you want me to generate the server-side patch (models/serializers/views) and a pull request for your repo, or only provide patch files for you to apply manually?
4. Any constraints on local storage retention for inner-camera files (days / auto-delete)? If not supplied, default to 7 days.

If you confirm 1-2 and tell me whether you want a PR or patch, I will:
- produce the code patches and the car-side skeleton code (ready to paste into your repo),
- include SQL migration snippet for AiVisionLog.image_url,
- and a prioritized developer task list with estimated effort.
