# 吾駕仙 MDG — car_station (二評)

簡介
----
本專案為「吾駕仙 MDG」專案中的 car_station 子專案（位於 `二評/car_station/car_station`）。它是一個以 Flask 為主的 Web 應用，包含資料庫（SQLite）、模型與 Web 模板，提供車輛相關資料的管理與檢視（專案檔案與程式碼位於本資料夾）。

快速看點
- Flask 應用（app.py）
- SQLite db：`mdg_car.db`
- 模型邏輯放在 `models.py`
- 可擴充的 Blueprint 結構（`blueprints/`）
- 公用功能放在 `utils/`
- 前端模板放在 `templates/`

需求（建議）
----
- Python 3.8+
- 建議使用虛擬環境（venv / virtualenv / conda）
- 套件請參考 `requirements.txt`（若新增 AI 模型需額外加入 torch / tensorflow / opencv 等）

安裝與啟動
----
1. 取得程式碼
   - 直接 clone 或從已存在的 repo 使用該資料夾。

2. 建立虛擬環境並安裝相依
   - python -m venv venv
   - source venv/bin/activate  （Windows: venv\Scripts\activate）
   - pip install -r requirements.txt

3. 環境變數（視 app.py 需求）
   - 若 app.py 使用 Flask 內建啟動，可直接運行：
     - python app.py
   - 或使用 flask CLI（若 app.py 暴露 create_app 或 app 物件）：
     - export FLASK_APP=app.py
     - export FLASK_ENV=development
     - flask run

4. 上傳目錄與權限
   - 若應用會儲存上傳檔案，確保 instance/uploads（或 app 指定之資料夾）存在並可寫入。

資料庫（mdg_car.db）
----
- 資料庫檔案：`mdg_car.db`（SQLite）
- 若要檢視資料表，使用 sqlite3：
  - sqlite3 mdg_car.db
  - .tables
  - PRAGMA table_info(<table_name>);
- 若要在程式中初始化或遷移，請檢查 `models.py` 的定義與應用的初始化流程。

專案目錄結構（摘錄）
----
- app.py
- config.py
- models.py
- mdg_car.db
- requirements.txt
- document
- blueprints/
  -（各功能區的 blueprints）
- templates/
  -（HTML/Jinja 模板）
- utils/
  -（共用工具與函式）
- trip_data/
  -（旅程或測資資料）
- __pycache__/
- .DS_Store, __MACOSX（系統檔，可忽略）

如何新增 AI 影像辨識（建議）
----
若要在此專案加入影像辨識功能，建議採模組化方式：
1. 新增 Blueprint：`blueprints/image_recognition/`
   - `__init__.py`：建立 blueprint
   - `routes.py`：處理上傳、回傳結果的 API

2. 將推論邏輯放在 utils：`utils/image_recognition.py`
   - 在此處 load model、定義 transform、predict 函式
   - 若使用 pretrained model（torch/keras/onnx），請在 `requirements.txt` 加入對應套件

3. 模型檔放置位置
   - `ml_models/` 或 `static/models/`（將大檔放於此並加入 .gitignore 視需要）

4. 在 `app.py` 註冊 blueprint
   - 範例： app.register_blueprint(image_recognition_bp, url_prefix='/image_recognition')

5. 注意事項
   - 控制上傳檔案大小、檔案類型
   - 若需 GPU，部署環境需支援（Docker + GPU 驅動）
   - 若模型很大，建議使用外部模型儲存（S3、分離服務）

範例指引（快速參考）
----
- 安裝 PyTorch（若使用 torchvision pretrained）：
  - pip install torch torchvision Pillow
- 建立上傳 API（routes）呼叫 utils.image_recognition.predict_image(path) 並回傳 JSON 結果
- 前端簡單上傳表單放在 `templates/` 下：呈現上傳介面並呼叫 `/image_recognition/predict`

測試與偵錯
----
- 本機測試：先在 dev 模式下測試上傳、DB 讀寫、templates 渲染
- 日誌：檢視啟動時的例外訊息與權限錯誤
- 若遇到依賴問題，先確認 Python 版本與 requirements 中指定的版本相容
