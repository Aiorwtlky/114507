# 🚗 AI 視覺辨識車機系統 - 交接文件

> 最後更新：2025-10-02  
> 狀態：內鏡頭 AI 測試完成，節流機制待優化

---

## 📋 專案概況

**專案名稱：** 吾駕仙車隊管理系統 - AI 視覺辨識模組  
**開發階段：** 內鏡頭功能驗證完成（95%）  
**測試結果：** A01/A02 事件可正常觸發，需調整節流機制  
**技術棧：** Flask + MediaPipe + YOLOv8 + OpenCV  
**部署環境：** Windows 開發環境（目標：Raspberry Pi 4）

---

## 🎯 系統功能

### 已實作並測試通過
1. **內鏡頭 AI 偵測**（MediaPipe）
   - 個體化校準系統（適應不同眼睛大小）
   - 疲勞駕駛偵測（A01, A02）
   - 眨眼頻率分析
   - 校準數據持久化（30 天有效期）
   - 異常處理機制

### 待整合功能
2. **外鏡頭 AI 偵測**（OpenCV + YOLOv8）
   - 車道偏離偵測（整合 GPIO 方向燈）
   - 前車距離估計
   - 紅綠燈辨識
   - 事件：B01（車道偏離）、B02（前車過近）、B03（闖紅燈）

3. **資料流程**
   - 本地事件暫存（EventLogLocal）
   - 上傳佇列機制（UploadQueue）
   - 網路斷線容錯

---

## 📂 專案結構
car_station/
├── app.py                          ✅ Flask 主程式
├── models.py                       ✅ 資料庫模型
├── config.py                       ✅ 系統設定
├── requirements.txt                ✅ 依賴套件清單
│
├── blueprints/
│   ├── camera.py                   ✅ 攝影機串流 + AI 監控執行緒
│   ├── trip.py                     ✅ 行程管理 + AI 自動啟停
│   ├── image_recognition.py        ✅ AI 辨識 API
│   ├── gpio.py                     ✅ GPIO 讀取
│   └── video.py                    ✅ 錄影功能
│
├── utils/
│   ├── drowsiness_detector.py      ✅ 疲勞偵測核心（已優化）
│   ├── unified_ai_detector.py      ✅ 統一 AI 控制器
│   ├── image_recognition.py        ✅ 主要接口
│   ├── lane_departure_detector.py  ⏳ 車道偵測（待測試）
│   ├── vehicle_traffic_detector.py ⏳ YOLOv8 偵測（待測試）
│   ├── db_helper.py                ✅ 資料庫輔助
│   └── uploader.py                 ⏳ 上傳機制（待實作）
│
├── calibrations/                   ✅ 校準數據目錄
│   └── driver_TEST001.json         ✅ 駕駛員校準檔案
│
├── test_drowsiness.py              ✅ 測試腳本
└── a.py                            ✅ Flask 整合測試

---

## ✅ 已完成的步驟

1. ✅ 安裝所有 AI 依賴套件（mediapipe, ultralytics, opencv）
2. ✅ 建立核心 AI 模組（drowsiness_detector.py）
3. ✅ 完成個體化校準系統
4. ✅ 整合 Flask AI 監控執行緒
5. ✅ 實作事件代碼映射（A01, A02）
6. ✅ 完成完整異常處理
7. ✅ 測試驗證（test_drowsiness.py）
8. ✅ 停用頭部姿態偵測（解決誤報）

---

## 🔧 測試結果分析

### 測試數據
- **測試時長：** 34 秒（1032 幀）
- **基準 EAR：** 0.331（正常範圍）
- **偵測事件：** 15 次（包含重複觸發）
- **眨眼次數：** 3 次

### 成功項目
1. ✅ MediaPipe 初始化正常
2. ✅ 個體化校準成功
3. ✅ A02 事件可觸發（閉眼 1 秒）
4. ✅ A01 事件可觸發（閉眼 3 秒）
5. ✅ 攝影機讀取穩定
6. ✅ 眨眼偵測正常

### 需改進項目
1. ⚠️ **節流機制需強化**：同一閉眼動作觸發多次事件
2. ⚠️ **信心分數波動**：0.14 ~ 0.92 範圍變化大
3. ⚠️ **閾值待調整**：考慮提高到 40 幀（1.3 秒）

---

## 🎯 評分標準對照表

| 代碼 | 描述 | 觸發條件 | 扣分 | 測試狀態 | AI 模型 |
|------|------|----------|------|----------|---------|
| A01 | 重度疲勞駕駛 | 閉眼 ≥ 3 秒 | 25 | ✅ 通過 | MediaPipe |
| A02 | 中度疲勞駕駛 | 閉眼 1-3 秒 | 15 | ✅ 通過 | MediaPipe |
| A03 | 長時間分心 | 低頭 > 5 秒 | 20 | ⚠️ 停用 | MediaPipe |
| B01 | 車道偏離 | 未打方向燈 | 5 | ⏳ 待測 | OpenCV |
| B02 | 前車過近 | 距離 < 安全值 | 15 | ⏳ 待測 | YOLOv8 |
| B03 | 闖紅燈 | 紅燈 + 移動 | 30 | ⏳ 待測 | YOLOv8 |

---

## 🧪 測試方式

### 方法 1：單獨測試內鏡頭 AI（推薦）
```bash
python test_drowsiness.py
測試流程：

系統啟動，載入校準數據或開始校準
前 1-2 秒保持正常睜眼（校準階段）
校準完成後開始偵測
測試動作：

閉眼 1-2 秒 → 應觸發 A02
閉眼 3+ 秒 → 應觸發 A01


按 'q' 退出測試

方法 2：完整系統測試
bash# Terminal 1: 啟動 Flask
python app.py

# Terminal 2: 執行測試腳本
python a.py
注意事項：

需先修改 config.py 設定內鏡頭為攝影機索引 0
確認 Flask 服務運行在 port 5003
測試時長建議 30 秒以上


🔑 關鍵程式碼位置
1. 核心偵測邏輯
檔案： utils/drowsiness_detector.py
類別： PersonalizedDrowsinessDetector
關鍵參數：
pythonear_threshold_factor = 0.75        # 閉眼閾值因子
A02_frames = 30                    # 中度疲勞觸發（1 秒）
A01_frames = 90                    # 重度疲勞觸發（3 秒）
2. AI 監控啟動
檔案： blueprints/trip.py
函數： api_start_trip()
位置： return 之前
pythonfrom blueprints.camera import ai_monitoring_active, ai_monitoring_worker
3. AI 偵測執行緒
檔案： blueprints/camera.py
函數： ai_monitoring_worker()
說明： 每 2 秒執行一次 AI 偵測
4. 事件儲存
檔案： utils/db_helper.py
函數： LocalEventHelper.create_event()
說明： 將偵測結果儲存到 EventLogLocal 表
5. 事件代碼映射
檔案： utils/unified_ai_detector.py
字典： event_mapping
說明： 將偵測結果轉換為標準事件代碼

🐛 已知問題與解決方案
問題 1：事件重複觸發
現象： 一次閉眼動作觸發 2-3 個相同事件
原因： 節流機制未在「剛達到閾值」時觸發
影響： 資料庫會有重複記錄
解決方案： 修改 detect() 方法中的節流邏輯
python# 只在剛達到 30 或 90 幀時觸發
if self.consecutive_closed_frames == 30:  # A02
    should_trigger_event = True
elif self.consecutive_closed_frames == 90:  # A01
    should_trigger_event = True
問題 2：頭部姿態誤判（已解決）
現象： 大量 A03 假警報
原因： 筆電攝影機角度計算不準確
解決： 已完全停用頭部姿態偵測
狀態： ✅ 已修正
問題 3：校準數據異常
現象： EAR 超出合理範圍（< 0.15 或 > 0.45）
原因： 光線不足、攝影機角度不佳
解決： 系統自動拒絕異常數據並重新校準
狀態： ✅ 已實作

🎓 技術細節
MediaPipe 個體化校準原理
1. 收集 30 個正常睜眼樣本（約 1 秒）
2. 計算中位數作為基準 EAR
3. 驗證合理性（0.15 ~ 0.45 範圍）
4. 儲存到 calibrations/driver_XXX.json
5. 設定 30 天有效期
6. 動態計算閉眼閾值 = baseline_ear × 0.75
EAR（Eye Aspect Ratio）計算公式
EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)

其中：
- p1-p4：眼睛水平寬度
- p2-p6, p3-p5：眼睛垂直高度

典型數值：
- 正常睜眼：EAR ≈ 0.25 ~ 0.35
- 閉眼：EAR < 閾值（baseline × 0.75）
眼睛大小適應性說明
駕駛員 A（大眼）：baseline_ear = 0.35 → 閉眼閾值 = 0.263
駕駛員 B（中等）：baseline_ear = 0.30 → 閉眼閾值 = 0.225
駕駛員 C（小眼）：baseline_ear = 0.25 → 閉眼閾值 = 0.188
結論： 系統會自動適應不同眼睛大小，無需手動調整。
節流機制邏輯
1. 檢查 consecutive_closed_frames
2. 只在「剛達到」30 或 90 幀時觸發事件
3. 記錄觸發時間戳
4. 3 秒內抑制相同類型事件

📊 系統架構流程
行程開始 (api_start_trip)
  ↓
自動啟動雙鏡頭 AI 監控
  ├─ 內鏡頭執行緒
  │   ├─ 校準（30 樣本，約 1 秒）
  │   ├─ MediaPipe 疲勞偵測
  │   │   ├─ 計算 EAR
  │   │   ├─ 判斷閉眼狀態
  │   │   ├─ 計數閉眼幀數
  │   │   └─ 觸發事件（A01, A02）
  │   └─ 偵測到事件 → LocalEventHelper.create_event()
  │
  └─ 外鏡頭執行緒（待整合）
      ├─ 讀取 GPIO（方向燈）
      ├─ OpenCV 車道線偵測
      ├─ YOLOv8 車輛/紅燈偵測
      └─ 偵測到事件 → EventLogLocal
  ↓
行程結束 (api_end_trip)
  ↓
停止 AI 監控
  ↓
更新影片記錄狀態
  ↓
（未來）批次上傳到後端

💡 下一步行動
立即執行（高優先）

⚠️ 套用節流機制修正
⚠️ 重新測試確認單次閉眼只觸發一個事件
⚠️ 調整閾值參數（考慮提高到 40 幀）

短期計畫（1-2 週）

⏳ 測試外鏡頭功能（B01, B02, B03）
⏳ 完整 Flask 系統整合測試
⏳ 驗證事件正確儲存到資料庫

中期計畫（1 個月）

⏳ 實作上傳佇列機制
⏳ 部署到 Raspberry Pi 4
⏳ 長時間穩定性測試
⏳ 實車道路測試


📞 常見問題快速解答
Q: AI 沒有任何輸出？
A: 檢查以下項目：

camera.py 的 ai_monitoring_worker 是否有 debug 輸出
模組導入是否成功
攝影機是否可讀取畫面

Q: MediaPipe 找不到臉部？
A: 確認以下條件：

攝影機角度：臉部正對鏡頭
光線充足：避免背光或過暗
距離適當：約 50cm 為佳
臉部在畫面中央

Q: 校準一直無法完成？
A: 可能原因：

眨眼過於頻繁（收集不到 30 個睜眼樣本）
光線問題（EAR 計算異常）
攝影機解析度過低

解決方案：
bash# 刪除舊校準數據重新開始
rm -rf calibrations/
Q: 閉眼沒有觸發事件？
A: 檢查以下數值：

觀察終端輸出的 EAR 值
閉眼時 EAR 應明顯下降（< 0.2）
確認閉眼時間達到 1 秒以上

Q: 事件重複觸發怎麼辦？
A: 這是已知問題，需套用節流機制修正（詳見問題 1）

🔄 緊急除錯指令
bash# 檢查 MediaPipe 是否正常
python -c "import mediapipe; print('MediaPipe OK')"

# 檢查 OpenCV 是否正常
python -c "import cv2; print('OpenCV OK')"

# 測試攝影機（檢查多個索引）
python -c "import cv2; [print(f'Camera {i}: {'OK' if cv2.VideoCapture(i).isOpened() else 'Failed'}') for i in range(3)]"

# 刪除舊校準數據（重新校準）
rm -rf calibrations/

# 檢查 Flask 服務
curl http://localhost:5003/camera/test

# 查看資料庫事件記錄
python -c "from models import EventLogLocal, db; from app import app; app.app_context().push(); print(EventLogLocal.query.count())"

📈 性能指標

校準時間： 1-2 秒（30 幀 @ 30 FPS）
偵測延遲： < 100ms
CPU 使用率： 約 30%（單鏡頭 MediaPipe）
記憶體佔用： 約 200MB
幀率： 穩定 30 FPS


🎯 生產環境建議參數
推薦配置
python# drowsiness_detector.py
ear_threshold_factor = 0.72        # 降低到 72%（更嚴格）
A02_frames = 40                    # 提高到 1.3 秒
A01_frames = 90                    # 維持 3 秒

# camera.py
ai_monitoring_interval = 2         # 每 2 秒偵測一次
校準策略

每位駕駛員首次使用時校準
校準數據 30 天自動過期
光線充足環境下進行
校準時保持正常坐姿


系統狀態： 內鏡頭 AI 測試完成，節流機制待優化
完成度： 95%（內鏡頭）/ 60%（整體）
最後測試： 2025-10-02
開發者： 透過 Claude 協助開發