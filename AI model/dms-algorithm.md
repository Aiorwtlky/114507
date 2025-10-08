# 核心思路（Hailo 加速的任務分工）

* **Hailo 上跑：**

  1. 臉部偵測（face detector）→ 給出穩定 face ROI
  2. 眼睛狀態分類（eye open/closed classifier，輸入雙眼小圖）
  3. （可選）嘴部開合/哈欠分類（mouth open/yawn classifier；或用嘴部關鍵點後續再上）

* **CPU 上跑（成本低、頻率不高）：**

  * Face Mesh/landmark（若你要高精度頭姿，可先 CPU 跑簡化 landmarks）
  * Head pose（solvePnP）+ Gaze 簡化
  * 特徵平滑、狀態機、多因子融合與事件輸出（超輕）

> 這樣把「重推論」丟給 Hailo，剩下運動學與規則在 CPU，整管線 10–15 FPS 沒問題。

---

# 模型與輸出規格（建議）

你可以先用 **現成 ONNX** 小模型，之後再換自己的蒐集/訓練版。以下是輸出需求（不綁死特定模型）：

1. **Face Detector（Hailo）**

   * 輸入：RGB 640×640（或 512×512）
   * 輸出：`[x,y,w,h,score]`（NMS 後 top‑1 或 top‑k，僅一張臉即可）
   * 需求：中近距離、容忍偏頭與口罩/墨鏡

2. **Eye State Classifier（Hailo）**

   * 輸入：從 face ROI 裁兩眼 ROI，拼成 96×48 或 128×64（雙眼並排）；或各眼 64×64 兩路輸入（看你模型）
   * 輸出：`p_closed ∈ [0,1]`（建議同時輸出 `p_open` 方便校驗）
   * 需求：強光/逆光/墨鏡下仍穩；此分支用來彌補 EAR 失效

3. **（可選）Mouth/Yawn Classifier（Hailo）**

   * 輸入：嘴部 ROI 64×64
   * 輸出：`p_yawn`, `p_mouth_open`（至少其一）
   * 需求：連續高值持續 ≥ `t_yawn_hold_sec` 判定哈欠

> 若你要 landmarks 作為幾何依據：先用 **CPU 的輕量 68/98‑landmark**（例如 PFLD 類），頻率可降到 5–10 FPS，介於面偵測後做；或先上 **眼睛/嘴巴分類**就能跑 MVP。

---

# 轉 Hailo 的標準流程（ONNX → HEF）

> 由 **模型工程師**一次走完；之後給邊緣工程師「.hef + 前處理參數 + 後處理解碼邏輯」。

1. 取得/訓練你的 **ONNX** 模型（face、eye、mouth）。
2. 準備 **校正資料集**（Calibration set，約數百～數千張，來源要接近實際車內）。
3. 用 **Hailo Dataflow Compiler** / **Model Zoo 工具** 做：

   * 前處理對齊（resize、mean/std、色彩空間）
   * 量化（INT8 或混合精度）＋ 編譯目標 **Hailo‑8**
   * 產出 **.hef**（每個模型一個檔）
4. 在 x86 或 RPi 上用 **hailortcli**／Python HailoRT SDK 驗證輸出與精度：

   * `hailortcli run -hef face_detector.hef --input input_tensor:npy/or/stream`
   * 對 100～1000 張驗證，量化後 mAP/accuracy 在可接受範圍
5. 封裝：`face_detector.hef`, `eye_cls.hef`, `mouth_cls.hef`，並提供：

   * **輸入尺寸/通道順序**、**前處理公式**、**輸出張量解碼方式**、**NMS 門檻**
   * 版本與 checksum（方便邊緣端核對）

---

# 邊緣端推論節點（Python，HailoRT）——執行流程（演算法級）

> 下面是**演算法邏輯**的寫法重點；邊緣工程師會把它換成實碼。你只需交付 `.hef` 與假碼接口。

### 初始化

* 載入 `face_detector.hef`，建立 Input/Output VStream
* 載入 `eye_cls.hef`（與 mouth\_cls.hef，如有）
* 設定 policy（門檻與視窗）
* 啟動簡單緩衝佇列，讓 face → ROI → eye/mouth 有流水線

### 每幀

1. **前處理**

   * RTSP frame → RGB → resize 至 detector 輸入大小 → normalize（跟編譯一致）
2. **臉偵測（Hailo）**

   * VStream 輸入 detector → 取輸出 → decode boxes → NMS → 取信心最高的人臉
   * 更新 `face_track`（簡易卡爾曼或 IOU 跟蹤即可）
3. **ROI 擷取**

   * 由臉框計算眼睛/嘴巴 ROI（用**幾何比例**或 landmarks）
   * 眼 ROI 調整至 eye\_cls 輸入尺寸，執行 **eye state (Hailo)** → 得 `p_closed`
   * 若 mouth\_cls 存在，擷取口 ROI，執行 → `p_yawn` / `p_mouth_open`
4. **（可選）landmarks + 頭姿（CPU）**

   * 每 2～3 幀跑一次 landmarks（降頻）
   * 用眼角/鼻尖/嘴角等點 `solvePnP` → yaw/pitch/roll
5. **特徵融合**

   * **眼睛閉合指標**：`eye_closed_score = max( I(EAR<T_EAR), p_closed )`
   * **PERCLOS**：滑窗內 `eye_closed_score > 0.5` 的比例
   * **哈欠**：`p_yawn` 或由 MAR（若 landmarks 有）估出
   * **低頭/回頭**：pitch/yaw 門檻 + 持續時間
6. **狀態機**

   * 微睡：`eye_closed_score` 連續 ≥ `micro_sleep_sec` → 事件
   * 低頭/回頭：持續 3/6/10 秒 → 事件（分級）
   * 哈欠：持續 ≥ `t_yawn_hold_sec` → 事件
   * PERCLOS：比例高於門檻並持續 → 事件
7. **多因子疲勞分 R**

   * 依 `fusion_weights` + 眼部可靠度自適應
   * 跨 R1/R2/R3 並持續 → `fatigue_risk_*` 事件（可本地僅提示，不必即刻上傳）
8. **輸出**

   * 行程中：只本地提示 & 事件寫 JSONL
   * 行程結束：批次上傳（照你前面要求）

---

# 延遲/效能與資源配置（Raspberry Pi 5B）

* **Det（Hailo）**：\~2–4ms（依模型）
* **Eye/Mouth（Hailo）**：\~1–2ms/支
* **Landmarks（CPU，降頻）**：5–15ms/幀（依模型與解析度，可每 2–3 幀跑一次）
* **總體**：10–15 FPS 綽綽有餘；若 landmarks 拖慢，可先不上 landmarks，用幾何 ROI + eye/mouth 分類器先跑。

---

# 你需要交付給邊緣開發者的「AI 成果包」

1. `face_detector.hef`、`eye_cls.hef`（+ `mouth_cls.hef` 如有）
2. `model_meta.yaml`（**非常重要**，寫清楚）：

   ```yaml
   face_detector:
     input: {w:640,h:640,format:RGB,normalize:{mean:[0.5,0.5,0.5],std:[0.5,0.5,0.5]}}
     output: {layout:"boxes+scores", anchors:..., strides:[8,16,32], nms:{iou:0.5,score:0.4}}
   eye_cls:
     input: {w:96,h:48,format:RGB,normalize:{mean:[0.5,0.5,0.5],std:[0.5,0.5,0.5]}}
     output: {labels:["open","closed"]}
   mouth_cls:
     input: {w:64,h:64,format:RGB,normalize:{mean:[0.5,0.5,0.5],std:[0.5,0.5,0.5]}}
     output: {labels:["neutral","yawn"]}
   policy: policy.json
   ```
3. `policy.json`
4. 簡短 README：怎麼跑 hailortcli 測試、前處理範例、輸出解碼說明
5. 一小包 **校正影像**（10–20 張）供現場快速 sanity check

---

# 風險點與替代方案

* **landmarks 模型 on Hailo？** 現況多半是 CPU 跑（也足夠）。等你有更好的 ONNX（如 PFLD）再轉 Hailo。
* **墨鏡/逆光**：眼睛分類器能顯著降低 EAR 失效的誤報（務必納入 Hailo 路徑）。
* **模型變更**：只要維持同樣 I/O 介面（input 尺寸與輸出語義），邊緣端無需改程式。

---

# 最小 PoC 路線

1. 先把 **face detector + eye classifier** 兩個 ONNX 轉成 **.hef**，在 RPi5 上用 `hailortcli` 跑通。
2. 用 CPU 計簡化 head pose（可不跑 landmarks，先用臉框幾何預估）→ 低頭/回頭事件。
3. 完成 **微睡/低頭/回頭/PERCLOS** 的狀態機與事件輸出（JSONL）。
4. 覺得穩定後再加 **mouth/yawn**、簡化 gaze、與 landmarks 精緻化。

