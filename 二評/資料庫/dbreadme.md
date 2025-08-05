# 智慧行車紀錄器系統資料庫設計文件

## 1. 專案概述
- **專案名稱**: 智慧行車紀錄器系統 (Smart Dashcam System)
- **版本**: 1.0
- **最後更新**: 2025-08-05
- **負責人**: 吳佳憲

## 2. 系統架構概述

### 2.1 系統模組
- **紀錄器端 (Edge Device)**: 影像擷取、AI辨識、危險警示
- **資料處理端 (Data Processing)**: 資料上傳、群組管理、設備管理
- **平台端 (Platform)**: 評分系統、報表分析

### 2.2 資料庫基本資訊
- **資料庫類型**: MySQL 8.0+
- **字符集**: UTF-8 (utf8mb4)
- **排序規則**: utf8mb4_unicode_ci

## 3. 資料表設計

### 3.1 駕駛個案相關表

#### 3.1.1 駕駛個案資料表 (driving_cases)
**用途**: 儲存每次駕駛行程的基本資訊

| 欄位名稱 | 資料型態 | 長度 | 允許NULL | 預設值 | 說明 |
|----------|----------|------|----------|--------|------|
| case_id | BIGINT | - | NO | AUTO_INCREMENT | 駕駛個案ID (主鍵) |
| driver_id | BIGINT | - | NO | - | 駕駛者ID (外鍵) |
| vehicle_id | BIGINT | - | NO | - | 車輛ID (外鍵) |
| device_id | BIGINT | - | NO | - | 紀錄器設備ID (外鍵) |
| start_time | DATETIME | - | NO | - | 行程開始時間 |
| end_time | DATETIME | - | YES | NULL | 行程結束時間 |
| total_distance | DECIMAL | 10,2 | YES | NULL | 總行駛距離(公里) |
| total_duration | INT | - | YES | NULL | 總行駛時間(秒) |
| case_status | ENUM | - | NO | 'active' | 個案狀態(active,completed,cancelled) |
| created_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP | 建立時間 |
| updated_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP ON UPDATE | 更新時間 |

#### 3.1.2 駕駛配對金鑰表 (driver_pairing_keys)
**用途**: 儲存駕駛者與設備配對的金鑰資訊

| 欄位名稱 | 資料型態 | 長度 | 允許NULL | 預設值 | 說明 |
|----------|----------|------|----------|--------|------|
| pairing_id | BIGINT | - | NO | AUTO_INCREMENT | 配對ID (主鍵) |
| driver_id | BIGINT | - | NO | - | 駕駛者ID (外鍵) |
| device_id | BIGINT | - | NO | - | 設備ID (外鍵) |
| pairing_token | VARCHAR | 255 | NO | - | 配對Token |
| qr_code | TEXT | - | YES | NULL | QR Code資料 |
| token_status | ENUM | - | NO | 'active' | Token狀態(active,used,expired) |
| expires_at | DATETIME | - | NO | - | Token過期時間 |
| created_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP | 建立時間 |

### 3.2 影像資料相關表

#### 3.2.1 原始影像資料表 (raw_video_data)
**用途**: 儲存原始影像檔案資訊

| 欄位名稱 | 資料型態 | 長度 | 允許NULL | 預設值 | 說明 |
|----------|----------|------|----------|--------|------|
| video_id | BIGINT | - | NO | AUTO_INCREMENT | 影像ID (主鍵) |
| case_id | BIGINT | - | NO | - | 駕駛個案ID (外鍵) |
| camera_type | ENUM | - | NO | - | 鏡頭類型(interior,exterior_front,exterior_rear) |
| file_path | VARCHAR | 500 | NO | - | 檔案儲存路徑 |
| file_name | VARCHAR | 255 | NO | - | 檔案名稱 |
| file_size | BIGINT | - | NO | - | 檔案大小(bytes) |
| duration | INT | - | NO | - | 影片長度(秒) |
| resolution | VARCHAR | 20 | YES | NULL | 解析度(例:1920x1080) |
| fps | INT | - | YES | NULL | 影格率 |
| start_timestamp | DATETIME | - | NO | - | 影片開始時間戳 |
| end_timestamp | DATETIME | - | NO | - | 影片結束時間戳 |
| upload_status | ENUM | - | NO | 'pending' | 上傳狀態(pending,uploaded,failed) |
| created_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP | 建立時間 |

### 3.3 AI辨識資料相關表

#### 3.3.1 物件資料表 (object_detection_data)
**用途**: 儲存物件辨識結果

| 欄位名稱 | 資料型態 | 長度 | 允許NULL | 預設值 | 說明 |
|----------|----------|------|----------|--------|------|
| detection_id | BIGINT | - | NO | AUTO_INCREMENT | 辨識ID (主鍵) |
| case_id | BIGINT | - | NO | - | 駕駛個案ID (外鍵) |
| video_id | BIGINT | - | YES | NULL | 相關影像ID (外鍵) |
| timestamp | DATETIME | - | NO | - | 辨識時間戳 |
| object_type | VARCHAR | 50 | NO | - | 物件類型(car,truck,pedestrian,motorcycle,bicycle) |
| confidence | DECIMAL | 5,4 | NO | - | 信心度(0-1) |
| bbox_x | INT | - | NO | - | 邊界框X座標 |
| bbox_y | INT | - | NO | - | 邊界框Y座標 |
| bbox_width | INT | - | NO | - | 邊界框寬度 |
| bbox_height | INT | - | NO | - | 邊界框高度 |
| distance | DECIMAL | 8,2 | YES | NULL | 距離(公尺) |
| relative_speed | DECIMAL | 8,2 | YES | NULL | 相對速度(km/h) |
| is_in_blind_spot | BOOLEAN | - | NO | FALSE | 是否在盲區 |
| created_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP | 建立時間 |

#### 3.3.2 車道線資料表 (lane_detection_data)
**用途**: 儲存車道線辨識結果

| 欄位名稱 | 資料型態 | 長度 | 允許NULL | 預設值 | 說明 |
|----------|----------|------|----------|--------|------|
| lane_id | BIGINT | - | NO | AUTO_INCREMENT | 車道線ID (主鍵) |
| case_id | BIGINT | - | NO | - | 駕駛個案ID (外鍵) |
| video_id | BIGINT | - | YES | NULL | 相關影像ID (外鍵) |
| timestamp | DATETIME | - | NO | - | 辨識時間戳 |
| lane_type | ENUM | - | NO | - | 車道線類型(left,right,center) |
| lane_status | ENUM | - | NO | - | 車道線狀態(detected,missing,unclear) |
| deviation_distance | DECIMAL | 8,2 | YES | NULL | 偏離距離(公分) |
| lane_confidence | DECIMAL | 5,4 | NO | - | 辨識信心度 |
| lane_curvature | DECIMAL | 10,6 | YES | NULL | 車道曲率 |
| is_crossing | BOOLEAN | - | NO | FALSE | 是否正在跨越 |
| created_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP | 建立時間 |

#### 3.3.3 燈號資料表 (traffic_light_data)
**用途**: 儲存交通號誌辨識結果

| 欄位名稱 | 資料型態 | 長度 | 允許NULL | 預設值 | 說明 |
|----------|----------|------|----------|--------|------|
| light_id | BIGINT | - | NO | AUTO_INCREMENT | 燈號ID (主鍵) |
| case_id | BIGINT | - | NO | - | 駕駛個案ID (外鍵) |
| video_id | BIGINT | - | YES | NULL | 相關影像ID (外鍵) |
| timestamp | DATETIME | - | NO | - | 辨識時間戳 |
| light_type | ENUM | - | NO | - | 燈號類型(traffic_light,turn_signal,reverse_light) |
| light_color | ENUM | - | NO | - | 燈號顏色(red,yellow,green,off) |
| light_status | ENUM | - | NO | - | 燈號狀態(on,off,blinking) |
| confidence | DECIMAL | 5,4 | NO | - | 辨識信心度 |
| distance | DECIMAL | 8,2 | YES | NULL | 距離(公尺) |
| turn_signal_status | ENUM | - | YES | NULL | 方向燈狀態(left,right,hazard,off) |
| reverse_gear_status | BOOLEAN | - | YES | NULL | 倒車檔狀態 |
| created_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP | 建立時間 |

#### 3.3.4 臉部資料表 (facial_detection_data)
**用途**: 儲存駕駛者臉部狀態辨識結果

| 欄位名稱 | 資料型態 | 長度 | 允許NULL | 預設值 | 說明 |
|----------|----------|------|----------|--------|------|
| facial_id | BIGINT | - | NO | AUTO_INCREMENT | 臉部辨識ID (主鍵) |
| case_id | BIGINT | - | NO | - | 駕駛個案ID (外鍵) |
| video_id | BIGINT | - | YES | NULL | 相關影像ID (外鍵) |
| timestamp | DATETIME | - | NO | - | 辨識時間戳 |
| face_detected | BOOLEAN | - | NO | - | 是否偵測到臉部 |
| drowsiness_level | DECIMAL | 5,4 | YES | NULL | 疲勞程度(0-1) |
| attention_level | DECIMAL | 5,4 | YES | NULL | 專注度(0-1) |
| eye_closure_duration | INT | - | YES | NULL | 閉眼持續時間(毫秒) |
| head_pose_yaw | DECIMAL | 8,2 | YES | NULL | 頭部偏航角度 |
| head_pose_pitch | DECIMAL | 8,2 | YES | NULL | 頭部俯仰角度 |
| head_pose_roll | DECIMAL | 8,2 | YES | NULL | 頭部翻滾角度 |
| emotion_state | VARCHAR | 50 | YES | NULL | 情緒狀態 |
| is_using_phone | BOOLEAN | - | NO | FALSE | 是否使用手機 |
| created_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP | 建立時間 |

### 3.4 危險事件相關表

#### 3.4.1 危險事件資料表 (dangerous_events)
**用途**: 儲存系統偵測到的危險事件

| 欄位名稱 | 資料型態 | 長度 | 允許NULL | 預設值 | 說明 |
|----------|----------|------|----------|--------|------|
| event_id | BIGINT | - | NO | AUTO_INCREMENT | 事件ID (主鍵) |
| case_id | BIGINT | - | NO | - | 駕駛個案ID (外鍵) |
| event_type | ENUM | - | NO | - | 事件類型(collision_risk,lane_departure,drowsy_driving,distracted_driving,speeding,harsh_braking,harsh_acceleration) |
| severity_level | ENUM | - | NO | - | 嚴重程度(low,medium,high,critical) |
| start_timestamp | DATETIME | - | NO | - | 事件開始時間 |
| end_timestamp | DATETIME | - | YES | NULL | 事件結束時間 |
| duration | INT | - | YES | NULL | 持續時間(秒) |
| location_lat | DECIMAL | 10,8 | YES | NULL | 緯度 |
| location_lng | DECIMAL | 11,8 | YES | NULL | 經度 |
| speed_kmh | DECIMAL | 6,2 | YES | NULL | 當時車速(km/h) |
| acceleration | DECIMAL | 8,4 | YES | NULL | 加速度(m/s²) |
| warning_issued | BOOLEAN | - | NO | FALSE | 是否已發出警告 |
| warning_timestamp | DATETIME | - | YES | NULL | 警告發出時間 |
| event_description | TEXT | - | YES | NULL | 事件描述 |
| confidence_score | DECIMAL | 5,4 | NO | - | 事件信心度 |
| created_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP | 建立時間 |

### 3.5 用戶管理相關表

#### 3.5.1 駕駛者資料表 (drivers)
**用途**: 儲存駕駛者基本資訊

| 欄位名稱 | 資料型態 | 長度 | 允許NULL | 預設值 | 說明 |
|----------|----------|------|----------|--------|------|
| driver_id | BIGINT | - | NO | AUTO_INCREMENT | 駕駛者ID (主鍵) |
| employee_id | VARCHAR | 50 | YES | NULL | 員工編號 |
| full_name | VARCHAR | 100 | NO | - | 姓名 |
| email | VARCHAR | 100 | YES | NULL | 電子郵件 |
| phone | VARCHAR | 20 | YES | NULL | 電話號碼 |
| license_number | VARCHAR | 50 | YES | NULL | 駕照號碼 |
| license_class | VARCHAR | 10 | YES | NULL | 駕照等級 |
| hire_date | DATE | - | YES | NULL | 聘僱日期 |
| group_id | BIGINT | - | YES | NULL | 所屬群組ID (外鍵) |
| is_active | BOOLEAN | - | NO | TRUE | 是否啟用 |
| created_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP | 建立時間 |
| updated_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP ON UPDATE | 更新時間 |

#### 3.5.2 人員管理表 (personnel_management)
**用途**: 儲存系統管理人員資訊

| 欄位名稱 | 資料型態 | 長度 | 允許NULL | 預設值 | 說明 |
|----------|----------|------|----------|--------|------|
| personnel_id | BIGINT | - | NO | AUTO_INCREMENT | 人員ID (主鍵) |
| username | VARCHAR | 50 | NO | - | 使用者帳號 |
| password_hash | VARCHAR | 255 | NO | - | 密碼雜湊 |
| full_name | VARCHAR | 100 | NO | - | 姓名 |
| email | VARCHAR | 100 | NO | - | 電子郵件 |
| role | ENUM | - | NO | - | 角色(admin,manager,device_operator,mdg_engineer) |
| permissions | JSON | - | YES | NULL | 權限設定 |
| last_login_at | DATETIME | - | YES | NULL | 最後登入時間 |
| is_active | BOOLEAN | - | NO | TRUE | 是否啟用 |
| created_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP | 建立時間 |
| updated_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP ON UPDATE | 更新時間 |

### 3.6 群組管理相關表

#### 3.6.1 群組資料表 (groups)
**用途**: 儲存駕駛者群組資訊

| 欄位名稱 | 資料型態 | 長度 | 允許NULL | 預設值 | 說明 |
|----------|----------|------|----------|--------|------|
| group_id | BIGINT | - | NO | AUTO_INCREMENT | 群組ID (主鍵) |
| group_name | VARCHAR | 100 | NO | - | 群組名稱 |
| group_description | TEXT | - | YES | NULL | 群組描述 |
| manager_id | BIGINT | - | NO | - | 群組管理者ID (外鍵) |
| max_members | INT | - | YES | NULL | 最大成員數 |
| current_members | INT | - | NO | 0 | 目前成員數 |
| group_settings | JSON | - | YES | NULL | 群組設定 |
| is_active | BOOLEAN | - | NO | TRUE | 是否啟用 |
| created_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP | 建立時間 |
| updated_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP ON UPDATE | 更新時間 |

### 3.7 設備管理相關表

#### 3.7.1 車機資料表 (vehicle_devices)
**用途**: 儲存車載紀錄器設備資訊

| 欄位名稱 | 資料型態 | 長度 | 允許NULL | 預設值 | 說明 |
|----------|----------|------|----------|--------|------|
| device_id | BIGINT | - | NO | AUTO_INCREMENT | 設備ID (主鍵) |
| device_serial | VARCHAR | 100 | NO | - | 設備序號 |
| device_model | VARCHAR | 50 | NO | - | 設備型號 |
| firmware_version | VARCHAR | 20 | YES | NULL | 韌體版本 |
| installation_date | DATE | - | YES | NULL | 安裝日期 |
| last_maintenance | DATE | - | YES | NULL | 最後維護日期 |
| device_status | ENUM | - | NO | 'inactive' | 設備狀態(active,inactive,maintenance,error) |
| network_status | ENUM | - | NO | 'offline' | 網路狀態(online,offline,weak_signal) |
| storage_capacity | BIGINT | - | YES | NULL | 儲存容量(bytes) |
| storage_used | BIGINT | - | YES | NULL | 已使用儲存(bytes) |
| battery_level | INT | - | YES | NULL | 電池電量(%) |
| gps_enabled | BOOLEAN | - | NO | TRUE | GPS是否啟用 |
| created_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP | 建立時間 |
| updated_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP ON UPDATE | 更新時間 |

#### 3.7.2 車輛資料表 (vehicles)
**用途**: 儲存車輛基本資訊

| 欄位名稱 | 資料型態 | 長度 | 允許NULL | 預設值 | 說明 |
|----------|----------|------|----------|--------|------|
| vehicle_id | BIGINT | - | NO | AUTO_INCREMENT | 車輛ID (主鍵) |
| license_plate | VARCHAR | 20 | NO | - | 車牌號碼 |
| vehicle_make | VARCHAR | 50 | YES | NULL | 車輛廠牌 |
| vehicle_model | VARCHAR | 50 | YES | NULL | 車輛型號 |
| vehicle_year | INT | - | YES | NULL | 出廠年份 |
| vehicle_type | ENUM | - | YES | NULL | 車輛類型(sedan,suv,truck,bus,motorcycle) |
| device_id | BIGINT | - | YES | NULL | 安裝的設備ID (外鍵) |
| current_driver_id | BIGINT | - | YES | NULL | 目前駕駛者ID (外鍵) |
| group_id | BIGINT | - | YES | NULL | 所屬群組ID (外鍵) |
| is_active | BOOLEAN | - | NO | TRUE | 是否啟用 |
| created_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP | 建立時間 |
| updated_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP ON UPDATE | 更新時間 |

### 3.8 評分系統相關表

#### 3.8.1 評分標準表 (scoring_criteria)
**用途**: 儲存評分標準設定

| 欄位名稱 | 資料型態 | 長度 | 允許NULL | 預設值 | 說明 |
|----------|----------|------|----------|--------|------|
| criteria_id | BIGINT | - | NO | AUTO_INCREMENT | 標準ID (主鍵) |
| criteria_name | VARCHAR | 100 | NO | - | 標準名稱 |
| criteria_category | ENUM | - | NO | - | 標準類別(safety,efficiency,compliance,behavior) |
| base_score | INT | - | NO | 100 | 基礎分數 |
| weight | DECIMAL | 5,4 | NO | 1.0000 | 權重 |
| description | TEXT | - | YES | NULL | 標準描述 |
| formula | TEXT | - | YES | NULL | 計算公式 |
| is_active | BOOLEAN | - | NO | TRUE | 是否啟用 |
| created_by | BIGINT | - | NO | - | 建立者ID (外鍵) |
| created_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP | 建立時間 |
| updated_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP ON UPDATE | 更新時間 |

#### 3.8.2 扣分標準表 (deduction_criteria)
**用途**: 儲存扣分標準設定

| 欄位名稱 | 資料型態 | 長度 | 允許NULL | 預設值 | 說明 |
|----------|----------|------|----------|--------|------|
| deduction_id | BIGINT | - | NO | AUTO_INCREMENT | 扣分標準ID (主鍵) |
| event_type | ENUM | - | NO | - | 事件類型(對應危險事件類型) |
| severity_level | ENUM | - | NO | - | 嚴重程度(low,medium,high,critical) |
| deduction_points | INT | - | NO | - | 扣分分數 |
| max_daily_deduction | INT | - | YES | NULL | 每日最大扣分 |
| description | TEXT | - | YES | NULL | 扣分描述 |
| is_active | BOOLEAN | - | NO | TRUE | 是否啟用 |
| created_by | BIGINT | - | NO | - | 建立者ID (外鍵) |
| created_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP | 建立時間 |
| updated_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP ON UPDATE | 更新時間 |

#### 3.8.3 駕駛個案評分資料表 (driving_case_scores)
**用途**: 儲存每個駕駛個案的評分結果

| 欄位名稱 | 資料型態 | 長度 | 允許NULL | 預設值 | 說明 |
|----------|----------|------|----------|--------|------|
| score_id | BIGINT | - | NO | AUTO_INCREMENT | 評分ID (主鍵) |
| case_id | BIGINT | - | NO | - | 駕駛個案ID (外鍵) |
| total_score | DECIMAL | 6,2 | NO | - | 總分 |
| safety_score | DECIMAL | 6,2 | YES | NULL | 安全分數 |
| efficiency_score | DECIMAL | 6,2 | YES | NULL | 效率分數 |
| compliance_score | DECIMAL | 6,2 | YES | NULL | 合規分數 |
| behavior_score | DECIMAL | 6,2 | YES | NULL | 行為分數 |
| total_deductions | INT | - | NO | 0 | 總扣分 |
| gemini_feedback | TEXT | - | YES | NULL | AI回饋建議 |
| score_status | ENUM | - | NO | 'calculated' | 評分狀態(pending,calculated,reviewed) |
| calculated_at | DATETIME | - | NO | - | 計算時間 |
| reviewed_by | BIGINT | - | YES | NULL | 審核者ID (外鍵) |
| reviewed_at | DATETIME | - | YES | NULL | 審核時間 |
| created_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP | 建立時間 |

#### 3.8.4 駕駛個案評分細節表 (driving_case_score_details)
**用途**: 儲存評分的詳細分解資訊

| 欄位名稱 | 資料型態 | 長度 | 允許NULL | 預設值 | 說明 |
|----------|----------|------|----------|--------|------|
| detail_id | BIGINT | - | NO | AUTO_INCREMENT | 明細ID (主鍵) |
| score_id | BIGINT | - | NO | - | 評分ID (外鍵) |
| criteria_id | BIGINT | - | YES | NULL | 評分標準ID (外鍵) |
| deduction_id | BIGINT | - | YES | NULL | 扣分標準ID (外鍵) |
| event_id | BIGINT | - | YES | NULL | 相關事件ID (外鍵) |
| item_type | ENUM | - | NO | - | 項目類型(score,deduction) |
| points | DECIMAL | 6,2 | NO | - | 得分/扣分 |
| description | VARCHAR | 200 | YES | NULL | 項目描述 |
| calculation_note | TEXT | - | YES | NULL | 計算說明 |
| created_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP | 建立時間 |

## 4. 資料關聯圖

```
drivers (1) ----< driving_cases (M)
vehicles (1) ----< driving_cases (M)
vehicle_devices (1) ----< driving_cases (M)
groups (1) ----< drivers (M)
groups (1) ----< vehicles (M)

driving_cases (1) ----< raw_video_data (M)
driving_cases (1) ----< object_detection_data (M)
driving_cases (1) ----< lane_detection_data (M)
driving_cases (1) ----< traffic_light_data (M)
driving_cases (1) ----< facial_detection_data (M)
driving_cases (1) ----< dangerous_events (M)

driving_cases (1) ----< driving_case_scores (1)
driving_case_scores (1) ----< driving_case_score_details (M)

scoring_criteria (1) ----< driving_case_score_details (M)
deduction_criteria (1) ----< driving_case_score_details (M)
dangerous_events (1) ----< driving_case_score_details (M)

personnel_management (1) ----< groups (M) [manager]
personnel_management (1) ----< scoring_criteria (M) [creator]
personnel_management (1) ----< deduction_criteria (M) [creator]
```

### 3.9 正規化改進 - 新增參考資料表

#### 3.9.1 事件類型表 (event_types)
**用途**: 標準化危險事件類型

| 欄位名稱 | 資料型態 | 長度 | 允許NULL | 預設值 | 說明 |
|----------|----------|------|----------|--------|------|
| event_type_id | INT | - | NO | AUTO_INCREMENT | 事件類型ID (主鍵) |
| event_code | VARCHAR | 50 | NO | - | 事件代碼 |
| event_name | VARCHAR | 100 | NO | - | 事件名稱 |
| event_category | VARCHAR | 50 | NO | - | 事件分類 |
| description | TEXT | - | YES | NULL | 事件描述 |
| is_active | BOOLEAN | - | NO | TRUE | 是否啟用 |

#### 3.9.2 嚴重程度表 (severity_levels)
**用途**: 標準化嚴重程度等級

| 欄位名稱 | 資料型態 | 長度 | 允許NULL | 預設值 | 說明 |
|----------|----------|------|----------|--------|------|
| severity_id | INT | - | NO | AUTO_INCREMENT | 嚴重程度ID (主鍵) |
| severity_code | VARCHAR | 20 | NO | - | 程度代碼 |
| severity_name | VARCHAR | 50 | NO | - | 程度名稱 |
| severity_weight | DECIMAL | 3,2 | NO | - | 嚴重程度權重 |
| color_code | VARCHAR | 7 | YES | NULL | 顯示顏色代碼 |

#### 3.9.3 物件類型表 (object_types)
**用途**: 標準化可辨識物件類型

| 欄位名稱 | 資料型態 | 長度 | 允許NULL | 預設值 | 說明 |
|----------|----------|------|----------|--------|------|
| object_type_id | INT | - | NO | AUTO_INCREMENT | 物件類型ID (主鍵) |
| type_code | VARCHAR | 30 | NO | - | 類型代碼 |
| type_name | VARCHAR | 50 | NO | - | 類型名稱 |
| category | VARCHAR | 30 | NO | - | 物件分類 |
| risk_level | INT | - | NO | 1 | 風險等級(1-5) |

### 3.10 修正後的主要資料表

#### 3.10.1 危險事件資料表 (危險事件資料表 - 修正版)

| 欄位名稱 | 資料型態 | 長度 | 允許NULL | 預設值 | 說明 |
|----------|----------|------|----------|--------|------|
| event_id | BIGINT | - | NO | AUTO_INCREMENT | 事件ID (主鍵) |
| case_id | BIGINT | - | NO | - | 駕駛個案ID (外鍵) |
| event_type_id | INT | - | NO | - | 事件類型ID (外鍵) |
| severity_id | INT | - | NO | - | 嚴重程度ID (外鍵) |
| start_timestamp | DATETIME | - | NO | - | 事件開始時間 |
| end_timestamp | DATETIME | - | YES | NULL | 事件結束時間 |
| duration | INT | - | YES | NULL | 持續時間(秒) |
| location_lat | DECIMAL | 10,8 | YES | NULL | 緯度 |
| location_lng | DECIMAL | 11,8 | YES | NULL | 經度 |
| speed_kmh | DECIMAL | 6,2 | YES | NULL | 當時車速(km/h) |
| acceleration | DECIMAL | 8,4 | YES | NULL | 加速度(m/s²) |
| confidence_score | DECIMAL | 5,4 | NO | - | 事件信心度 |
| warning_issued | BOOLEAN | - | NO | FALSE | 是否已發出警告 |
| warning_timestamp | DATETIME | - | YES | NULL | 警告發出時間 |
| event_description | TEXT | - | YES | NULL | 事件描述 |
| created_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP | 建立時間 |

#### 3.10.2 物件資料表 (物件資料表 - 修正版)

| 欄位名稱 | 資料型態 | 長度 | 允許NULL | 預設值 | 說明 |
|----------|----------|------|----------|--------|------|
| detection_id | BIGINT | - | NO | AUTO_INCREMENT | 辨識ID (主鍵) |
| case_id | BIGINT | - | NO | - | 駕駛個案ID (外鍵) |
| video_id | BIGINT | - | YES | NULL | 相關影像ID (外鍵) |
| object_type_id | INT | - | NO | - | 物件類型ID (外鍵) |
| timestamp | DATETIME | - | NO | - | 辨識時間戳 |
| confidence | DECIMAL | 5,4 | NO | - | 信心度(0-1) |
| bbox_x | INT | - | NO | - | 邊界框X座標 |
| bbox_y | INT | - | NO | - | 邊界框Y座標 |
| bbox_width | INT | - | NO | - | 邊界框寬度 |
| bbox_height | INT | - | NO | - | 邊界框高度 |
| distance | DECIMAL | 8,2 | YES | NULL | 距離(公尺) |
| relative_speed | DECIMAL | 8,2 | YES | NULL | 相對速度(km/h) |
| is_in_blind_spot | BOOLEAN | - | NO | FALSE | 是否在盲區 |
| created_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP | 建立時間 |

#### 3.10.3 扣分標準表 (扣分標準表 - 修正版)

| 欄位名稱 | 資料型態 | 長度 | 允許NULL | 預設值 | 說明 |
|----------|----------|------|----------|--------|------|
| deduction_id | BIGINT | - | NO | AUTO_INCREMENT | 扣分標準ID (主鍵) |
| event_type_id | INT | - | NO | - | 事件類型ID (外鍵) |
| severity_id | INT | - | NO | - | 嚴重程度ID (外鍵) |
| deduction_points | INT | - | NO | - | 扣分分數 |
| max_daily_deduction | INT | - | YES | NULL | 每日最大扣分 |
| description | TEXT | - | YES | NULL | 扣分描述 |
| is_active | BOOLEAN | - | NO | TRUE | 是否啟用 |
| created_by | BIGINT | - | NO | - | 建立者ID (外鍵) |
| created_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP | 建立時間 |
| updated_at | TIMESTAMP | - | NO | CURRENT_TIMESTAMP ON UPDATE | 更新時間 |

## 4. 正規化分析

### 4.1 第一正規化 (1NF)
✅ **符合**: 所有欄位都是原子值，沒有重複的群組或陣列

### 4.2 第二正規化 (2NF) 
✅ **符合**: 
- 所有資料表都有適當的主鍵
- 非鍵屬性完全依賴於主鍵
- 移除了部分依賴關係

### 4.3 第三正規化 (3NF)
✅ **符合**: 
- 移除了傳遞依賴
- 建立了參考資料表 (event_types, severity_levels, object_types)
- 消除了重複的列舉值

### 4.4 正規化改進項目
1. **事件類型正規化**: 將 ENUM 改為參考表
2. **嚴重程度正規化**: 建立獨立的嚴重程度表
3. **物件類型正規化**: 標準化物件辨識類型
4. **消除重複資料**: 移除重複的列舉定義

## 5. 業務規則

### 5.1 駕駛個案相關
- 每個駕駛個案必須關聯一個駕駛者、車輛和設備
- 配對Token有時效性，過期後需重新產生
- 同一時間一個設備只能配對一個駕駛者

### 5.2 影像資料相關
- 原始影像檔案必須有對應的儲存路徑
- 影像資料必須與駕駛個案關聯
- 支援多種鏡頭類型的影像儲存

### 5.3 AI辨識相關
- 所有辨識結果必須有信心度分數
- 物件辨識結果需要邊界框座標
- 臉部辨識僅限車內鏡頭

### 5.4 危險事件相關
- 危險事件必須有明確的事件類型和嚴重程度
- 高嚴重程度事件必須發出警告
- 事件持續時間由系統自動計算

### 5.5 評分系統相關
- 評分標準可由MDG工程師調整
- 扣分標準與事件類型及嚴重程度關聯
- 每日扣分有上限限制
- Gemini API提供駕駛建議

## 6. 資料完整性約束

### 6.1 主鍵約束
- 每個資料表都有唯一的主鍵
- 使用 BIGINT AUTO_INCREMENT 確保唯一性

### 6.2 外鍵約束
```sql
-- 主要外鍵關聯
ALTER TABLE driving_cases ADD FOREIGN KEY (driver_id) REFERENCES drivers(driver_id);
ALTER TABLE driving_cases ADD FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id);
ALTER TABLE driving_cases ADD FOREIGN KEY (device_id) REFERENCES vehicle_devices(device_id);

ALTER TABLE dangerous_events ADD FOREIGN KEY (case_id) REFERENCES driving_cases(case_id);
ALTER TABLE dangerous_events ADD FOREIGN KEY (event_type_id) REFERENCES event_types(event_type_id);
ALTER TABLE dangerous_events ADD FOREIGN KEY (severity_id) REFERENCES severity_levels(severity_id);

ALTER TABLE object_detection_data ADD FOREIGN KEY (case_id) REFERENCES driving_cases(case_id);
ALTER TABLE object_detection_data ADD FOREIGN KEY (object_type_id) REFERENCES object_types(object_type_id);

ALTER TABLE deduction_criteria ADD FOREIGN KEY (event_type_id) REFERENCES event_types(event_type_id);
ALTER TABLE deduction_criteria ADD FOREIGN KEY (severity_id) REFERENCES severity_levels(severity_id);
```

### 6.3 檢查約束
```sql
-- 分數範圍檢查
ALTER TABLE driving_case_scores ADD CONSTRAINT chk_score_range 
CHECK (total_score >= 0 AND total_score <= 100);

-- 信心度範圍檢查
ALTER TABLE object_detection_data ADD CONSTRAINT chk_confidence_range 
CHECK (confidence >= 0 AND confidence <= 1);

-- 嚴重程度權重檢查
ALTER TABLE severity_levels ADD CONSTRAINT chk_weight_range 
CHECK (severity_weight >= 0 AND severity_weight <= 5);
```
