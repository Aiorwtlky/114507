-- 智慧行車記錄器系統資料庫 - 簡化實用版本
-- 版本: 4.0
-- 建立日期: 2025-08-25
-- 預估資料表數量: 12個主要表 + 3個視圖

CREATE DATABASE smart_dashcam_system 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE smart_dashcam_system;

-- =============================================================================
-- 1. 用戶管理系統 (3個表)
-- =============================================================================

-- 用戶主表 (管理者 + 駕駛員)
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,                    -- Django預設主鍵
    username VARCHAR(150) NOT NULL UNIQUE,                   -- 登入帳號
    password VARCHAR(128) NOT NULL,                          -- 密碼雜湊值
    email VARCHAR(254) NOT NULL UNIQUE,                      -- 電子郵件
    first_name VARCHAR(150),                                 -- 名字
    last_name VARCHAR(150),                                  -- 姓氏
    is_active BOOLEAN NOT NULL DEFAULT TRUE,                 -- 帳號是否啟用
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,                 -- 是否為管理員
    date_joined DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 建立時間
    last_login DATETIME,                                     -- 最後登入時間
    INDEX idx_username (username),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB COMMENT='系統用戶主表';

-- 管理群組表
CREATE TABLE management_groups (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,                    -- 群組ID
    name VARCHAR(100) NOT NULL,                              -- 群組名稱
    description TEXT,                                        -- 群組描述
    manager_id BIGINT NOT NULL,                              -- 群組管理者ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- 建立時間
    FOREIGN KEY (manager_id) REFERENCES users(id),
    INDEX idx_manager_id (manager_id)
) ENGINE=InnoDB COMMENT='管理群組表';

-- 駕駛員資料表
CREATE TABLE drivers (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,                    -- 駕駛員ID
    user_id BIGINT NOT NULL UNIQUE,                          -- 關聯用戶表
    employee_id VARCHAR(50) UNIQUE,                          -- 員工編號
    license_number VARCHAR(50),                              -- 駕照號碼
    phone VARCHAR(20),                                       -- 聯絡電話
    group_id BIGINT,                                         -- 所屬群組
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- 建立時間
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES management_groups(id),
    INDEX idx_employee_id (employee_id),
    INDEX idx_group_id (group_id)
) ENGINE=InnoDB COMMENT='駕駛員資料表';

-- =============================================================================
-- 2. 設備管理 (2個表)
-- =============================================================================

-- 樹莓派設備表
CREATE TABLE raspberry_devices (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,                    -- 設備ID
    device_serial VARCHAR(100) NOT NULL UNIQUE,              -- 設備序號
    device_model VARCHAR(50),                                -- 設備型號
    status ENUM('active', 'inactive', 'maintenance') DEFAULT 'inactive', -- 設備狀態
    last_sync_at DATETIME,                                   -- 最後同步時間
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- 建立時間
    INDEX idx_device_serial (device_serial),
    INDEX idx_status (status)
) ENGINE=InnoDB COMMENT='樹莓派設備表';

-- 車輛資料表
CREATE TABLE vehicles (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,                    -- 車輛ID
    license_plate VARCHAR(20) NOT NULL UNIQUE,               -- 車牌號碼
    make VARCHAR(50),                                        -- 車輛品牌
    model VARCHAR(50),                                       -- 車輛型號
    raspberry_device_id BIGINT,                              -- 安裝的樹莓派設備
    group_id BIGINT,                                         -- 所屬群組
    is_active BOOLEAN DEFAULT TRUE,                          -- 是否啟用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- 建立時間
    FOREIGN KEY (raspberry_device_id) REFERENCES raspberry_devices(id),
    FOREIGN KEY (group_id) REFERENCES management_groups(id),
    INDEX idx_license_plate (license_plate)
) ENGINE=InnoDB COMMENT='車輛資料表';

-- =============================================================================
-- 3. 駕駛記錄系統 (1個表)
-- =============================================================================

-- 駕駛工作階段表
CREATE TABLE driving_sessions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,                    -- 工作階段ID
    driver_id BIGINT NOT NULL,                               -- 駕駛員ID
    vehicle_id BIGINT NOT NULL,                              -- 車輛ID
    start_time DATETIME NOT NULL,                            -- 開始時間
    end_time DATETIME,                                       -- 結束時間
    total_distance DECIMAL(8,2),                            -- 總行駛距離(公里)
    total_duration INT,                                      -- 總行駛時間(分鐘)
    status ENUM('active', 'completed', 'cancelled') DEFAULT 'active', -- 狀態
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- 建立時間
    FOREIGN KEY (driver_id) REFERENCES drivers(id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
    INDEX idx_driver_id (driver_id),
    INDEX idx_start_time (start_time),
    INDEX idx_status (status)
) ENGINE=InnoDB COMMENT='駕駛工作階段表';

-- =============================================================================
-- 4. AI偵測結果系統 (2個表) - 只儲存偵測結果文字
-- =============================================================================

-- 內鏡頭偵測結果表 (駕駛員行為偵測)
CREATE TABLE interior_detections (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,                    -- 偵測記錄ID
    session_id BIGINT NOT NULL,                              -- 關聯的駕駛工作階段
    detection_time DATETIME NOT NULL,                        -- 偵測時間
    detection_type ENUM('fatigue', 'distraction', 'phone_usage', 'smoking', 'no_seatbelt', 'normal') NOT NULL, -- 偵測類型
    confidence DECIMAL(4,3) NOT NULL,                        -- 信心度(0.000-1.000)
    description TEXT,                                        -- 偵測結果描述
    is_violation BOOLEAN DEFAULT FALSE,                      -- 是否為違規
    severity ENUM('normal', 'warning', 'danger') DEFAULT 'normal', -- 嚴重程度
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- 同步時間
    FOREIGN KEY (session_id) REFERENCES driving_sessions(id),
    INDEX idx_session_id (session_id),
    INDEX idx_detection_time (detection_time),
    INDEX idx_is_violation (is_violation)
) ENGINE=InnoDB COMMENT='內鏡頭偵測結果表';

-- 前鏡頭偵測結果表 (交通環境偵測 - 簡化版本)
CREATE TABLE exterior_detections (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,                    -- 偵測記錄ID
    session_id BIGINT NOT NULL,                              -- 關聯的駕駛工作階段
    detection_time DATETIME NOT NULL,                        -- 偵測時間
    detection_type ENUM('lane_departure', 'obstacle_detected', 'traffic_sign', 'traffic_light', 'normal') NOT NULL, -- 偵測類型(簡化)
    confidence DECIMAL(4,3) NOT NULL,                        -- 信心度(0.000-1.000)
    description TEXT,                                        -- 偵測結果描述
    is_violation BOOLEAN DEFAULT FALSE,                      -- 是否為違規
    severity ENUM('normal', 'warning', 'danger') DEFAULT 'normal', -- 嚴重程度
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- 同步時間
    FOREIGN KEY (session_id) REFERENCES driving_sessions(id),
    INDEX idx_session_id (session_id),
    INDEX idx_detection_time (detection_time),
    INDEX idx_is_violation (is_violation)
) ENGINE=InnoDB COMMENT='前鏡頭偵測結果表';

-- =============================================================================
-- 5. 簡化評分系統 (3個表)
-- =============================================================================

-- 評分規則表
CREATE TABLE scoring_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,                       -- 規則ID
    detection_type VARCHAR(50) NOT NULL,                     -- 偵測類型
    severity ENUM('warning', 'danger') NOT NULL,             -- 嚴重程度(移除normal)
    deduction_points INT NOT NULL,                           -- 扣分
    description TEXT,                                        -- 規則描述
    is_active BOOLEAN DEFAULT TRUE,                          -- 是否啟用
    UNIQUE KEY uk_detection_severity (detection_type, severity),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB COMMENT='評分規則表';

-- 工作階段評分表 (大幅簡化)
CREATE TABLE session_scores (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,                    -- 評分記錄ID
    session_id BIGINT NOT NULL UNIQUE,                       -- 工作階段ID
    total_score INT DEFAULT 100,                            -- 總分(0-100整數)
    violation_count INT DEFAULT 0,                          -- 違規次數
    deduction_points INT DEFAULT 0,                         -- 總扣分
    grade ENUM('A', 'B', 'C', 'F') DEFAULT 'A',            -- 等級評分(4級)
    ai_feedback TEXT,                                       -- AI改善建議
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,      -- 計算時間
    FOREIGN KEY (session_id) REFERENCES driving_sessions(id),
    INDEX idx_total_score (total_score),
    INDEX idx_grade (grade)
) ENGINE=InnoDB COMMENT='工作階段評分表';

-- 違規記錄表 (簡化統計用)
CREATE TABLE violation_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,                    -- 違規記錄ID
    session_id BIGINT NOT NULL,                              -- 工作階段ID
    detection_type VARCHAR(50) NOT NULL,                     -- 違規類型
    severity ENUM('warning', 'danger') NOT NULL,             -- 嚴重程度
    violation_time DATETIME NOT NULL,                        -- 違規時間
    deduction_points INT NOT NULL,                           -- 該次扣分
    source ENUM('interior', 'exterior') NOT NULL,            -- 來源鏡頭
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- 建立時間
    FOREIGN KEY (session_id) REFERENCES driving_sessions(id),
    INDEX idx_session_id (session_id),
    INDEX idx_detection_type (detection_type),
    INDEX idx_violation_time (violation_time)
) ENGINE=InnoDB COMMENT='違規記錄表';

-- =============================================================================
-- 6. 資料同步管理 (1個表)
-- =============================================================================

-- 同步記錄表
CREATE TABLE sync_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,                    -- 同步記錄ID
    device_id BIGINT NOT NULL,                               -- 樹莓派設備ID
    sync_type ENUM('interior', 'exterior', 'system') NOT NULL, -- 同步類型
    status ENUM('success', 'failed', 'partial') NOT NULL,    -- 同步狀態
    records_synced INT DEFAULT 0,                           -- 同步記錄數
    error_message TEXT,                                      -- 錯誤訊息
    sync_time DATETIME NOT NULL,                            -- 同步時間
    FOREIGN KEY (device_id) REFERENCES raspberry_devices(id),
    INDEX idx_device_id (device_id),
    INDEX idx_sync_time (sync_time)
) ENGINE=InnoDB COMMENT='同步日誌表';

-- =============================================================================
-- 7. 初始化評分規則
-- =============================================================================

INSERT INTO scoring_rules (detection_type, severity, deduction_points, description) VALUES
-- 內鏡頭規則
('fatigue', 'warning', 5, '輕微疲勞'),
('fatigue', 'danger', 15, '嚴重疲勞'),
('distraction', 'warning', 3, '輕微分心'),
('distraction', 'danger', 10, '嚴重分心'),
('phone_usage', 'warning', 8, '疑似使用手機'),
('phone_usage', 'danger', 20, '確認使用手機'),
('no_seatbelt', 'warning', 10, '未繫安全帶'),
('smoking', 'warning', 5, '車內吸菸'),

-- 前鏡頭規則
('lane_departure', 'warning', 4, '輕微偏離車道'),
('lane_departure', 'danger', 12, '嚴重偏離車道'),
('obstacle_detected', 'warning', 6, '偵測到障礙物'),
('obstacle_detected', 'danger', 15, '緊急障礙物');

-- =============================================================================
-- 8. 實用視圖 (3個視圖) - 明確用途
-- =============================================================================

-- 視圖1: 駕駛記錄總覽 (用途: 駕駛員查看自己的歷史記錄)
CREATE VIEW v_driver_sessions AS
SELECT 
    ds.id as session_id,
    CONCAT(u.first_name, ' ', u.last_name) as driver_name,
    d.employee_id,
    v.license_plate,
    ds.start_time,
    ds.end_time,
    ds.total_distance,
    ds.status,
    ss.total_score,
    ss.grade,
    ss.violation_count
FROM driving_sessions ds
JOIN drivers d ON ds.driver_id = d.id
JOIN users u ON d.user_id = u.id
JOIN vehicles v ON ds.vehicle_id = v.id
LEFT JOIN session_scores ss ON ds.id = ss.session_id;

-- 視圖2: 駕駛員績效摘要 (用途: 管理者評估駕駛員表現)
CREATE VIEW v_driver_performance AS
SELECT 
    d.id as driver_id,
    CONCAT(u.first_name, ' ', u.last_name) as driver_name,
    d.employee_id,
    COUNT(ds.id) as total_trips,
    AVG(ss.total_score) as avg_score,
    COUNT(CASE WHEN ss.grade = 'A' THEN 1 END) as grade_a_count,
    COUNT(CASE WHEN ss.grade = 'F' THEN 1 END) as grade_f_count,
    SUM(ss.violation_count) as total_violations
FROM drivers d
JOIN users u ON d.user_id = u.id
LEFT JOIN driving_sessions ds ON d.id = ds.driver_id AND ds.status = 'completed'
LEFT JOIN session_scores ss ON ds.id = ss.session_id
GROUP BY d.id, u.first_name, u.last_name, d.employee_id;

-- 視圖3: 群組管理總覽 (用途: 群組管理者查看群組整體狀況)
CREATE VIEW v_group_summary AS
SELECT 
    mg.id as group_id,
    mg.name as group_name,
    COUNT(DISTINCT d.id) as driver_count,
    COUNT(ds.id) as total_sessions,
    AVG(ss.total_score) as avg_group_score,
    SUM(ss.violation_count) as total_group_violations
FROM management_groups mg
LEFT JOIN drivers d ON mg.id = d.group_id
LEFT JOIN driving_sessions ds ON d.id = ds.driver_id AND ds.status = 'completed'
LEFT JOIN session_scores ss ON ds.id = ss.session_id
GROUP BY mg.id, mg.name;

-- =============================================================================
-- 9. 簡化評分計算
-- =============================================================================

DELIMITER $

CREATE PROCEDURE sp_calculate_score(IN p_session_id BIGINT)
BEGIN
    DECLARE v_total_deduction INT DEFAULT 0;
    DECLARE v_violation_count INT DEFAULT 0;
    DECLARE v_final_score INT;
    DECLARE v_grade VARCHAR(1);
    
    -- 計算違規和扣分
    SELECT 
        COUNT(*) as violations,
        COALESCE(SUM(sr.deduction_points), 0) as deductions
    INTO v_violation_count, v_total_deduction
    FROM (
        SELECT detection_type, severity 
        FROM interior_detections 
        WHERE session_id = p_session_id AND is_violation = TRUE AND severity != 'normal'
        UNION ALL
        SELECT detection_type, severity 
        FROM exterior_detections 
        WHERE session_id = p_session_id AND is_violation = TRUE AND severity != 'normal'
    ) violations
    LEFT JOIN scoring_rules sr ON violations.detection_type = sr.detection_type 
                               AND violations.severity = sr.severity
    WHERE sr.is_active = TRUE;
    
    -- 計算最終分數和等級
    SET v_final_score = GREATEST(0, 100 - v_total_deduction);
    SET v_grade = CASE 
        WHEN v_final_score >= 85 THEN 'A'
        WHEN v_final_score >= 70 THEN 'B'
        WHEN v_final_score >= 60 THEN 'C'
        ELSE 'F'
    END;
    
    -- 插入評分記錄
    INSERT INTO session_scores (session_id, total_score, violation_count, deduction_points, grade)
    VALUES (p_session_id, v_final_score, v_violation_count, v_total_deduction, v_grade)
    ON DUPLICATE KEY UPDATE
        total_score = v_final_score,
        violation_count = v_violation_count,
        deduction_points = v_total_deduction,
        grade = v_grade,
        calculated_at = NOW();
        
END$

DELIMITER ;

-- =============================================================================
-- 總結
-- =============================================================================

SELECT '資料庫建立完成！' as '狀態',
       '12個主要資料表' as '資料表數量',
       '3個實用視圖' as '視圖數量',
       'A/B/C/F 四級評分' as '評分系統',
       '僅儲存文字偵測結果' as '儲存方式';
