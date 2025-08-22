-- 智慧行車紀錄器系統資料庫建立語句
-- 版本: 2.0
-- 建立日期: 2025-08-22

-- 建立資料庫
CREATE DATABASE smart_dashcam_system 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE smart_dashcam_system;

-- =============================================================================
-- 1. 參考資料表 (Reference Tables)
-- =============================================================================

-- 事件類型表
CREATE TABLE event_types (
    event_type_id INT AUTO_INCREMENT PRIMARY KEY,
    event_code VARCHAR(50) NOT NULL UNIQUE,
    event_name VARCHAR(100) NOT NULL,
    event_category VARCHAR(50) NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_event_category (event_category),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB COMMENT='事件類型參考表';

-- 嚴重程度表
CREATE TABLE severity_levels (
    severity_id INT AUTO_INCREMENT PRIMARY KEY,
    severity_code VARCHAR(20) NOT NULL UNIQUE,
    severity_name VARCHAR(50) NOT NULL,
    severity_weight DECIMAL(3,2) NOT NULL,
    color_code VARCHAR(7),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_severity_weight CHECK (severity_weight >= 0 AND severity_weight <= 5)
) ENGINE=InnoDB COMMENT='嚴重程度參考表';

-- 物件類型表
CREATE TABLE object_types (
    object_type_id INT AUTO_INCREMENT PRIMARY KEY,
    type_code VARCHAR(30) NOT NULL UNIQUE,
    type_name VARCHAR(50) NOT NULL,
    category VARCHAR(30) NOT NULL,
    risk_level INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_risk_level CHECK (risk_level >= 1 AND risk_level <= 5),
    INDEX idx_category (category),
    INDEX idx_risk_level (risk_level)
) ENGINE=InnoDB COMMENT='物件類型參考表';

-- =============================================================================
-- 2. 用戶管理相關表
-- =============================================================================

-- 人員管理表
CREATE TABLE personnel_management (
    personnel_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    role ENUM('admin', 'manager', 'device_operator', 'mdg_engineer') NOT NULL,
    permissions JSON,
    last_login_at DATETIME,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB COMMENT='系統人員管理表';

-- 群組資料表
CREATE TABLE groups (
    group_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    group_name VARCHAR(100) NOT NULL,
    group_description TEXT,
    manager_id BIGINT NOT NULL,
    max_members INT,
    current_members INT NOT NULL DEFAULT 0,
    group_settings JSON,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (manager_id) REFERENCES personnel_management(personnel_id),
    INDEX idx_group_name (group_name),
    INDEX idx_manager_id (manager_id),
    INDEX idx_is_active (is_active),
    CONSTRAINT chk_current_members CHECK (current_members >= 0)
) ENGINE=InnoDB COMMENT='群組資料表';

-- 駕駛者資料表
CREATE TABLE drivers (
    driver_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    employee_id VARCHAR(50),
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    license_number VARCHAR(50),
    license_class VARCHAR(10),
    hire_date DATE,
    group_id BIGINT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups(group_id),
    UNIQUE KEY uk_employee_id (employee_id),
    UNIQUE KEY uk_email (email),
    UNIQUE KEY uk_license_number (license_number),
    INDEX idx_full_name (full_name),
    INDEX idx_group_id (group_id),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB COMMENT='駕駛者資料表';

-- =============================================================================
-- 3. 設備管理相關表
-- =============================================================================

-- 車機資料表
CREATE TABLE vehicle_devices (
    device_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    device_serial VARCHAR(100) NOT NULL UNIQUE,
    device_model VARCHAR(50) NOT NULL,
    firmware_version VARCHAR(20),
    installation_date DATE,
    last_maintenance DATE,
    device_status ENUM('active', 'inactive', 'maintenance', 'error') NOT NULL DEFAULT 'inactive',
    network_status ENUM('online', 'offline', 'weak_signal') NOT NULL DEFAULT 'offline',
    storage_capacity BIGINT,
    storage_used BIGINT DEFAULT 0,
    battery_level INT,
    gps_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_device_serial (device_serial),
    INDEX idx_device_status (device_status),
    INDEX idx_network_status (network_status),
    CONSTRAINT chk_battery_level CHECK (battery_level >= 0 AND battery_level <= 100),
    CONSTRAINT chk_storage_used CHECK (storage_used >= 0)
) ENGINE=InnoDB COMMENT='車載設備資料表';

-- 車輛資料表
CREATE TABLE vehicles (
    vehicle_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    license_plate VARCHAR(20) NOT NULL UNIQUE,
    vehicle_make VARCHAR(50),
    vehicle_model VARCHAR(50),
    vehicle_year INT,
    vehicle_type ENUM('sedan', 'suv', 'truck', 'bus', 'motorcycle'),
    device_id BIGINT,
    current_driver_id BIGINT,
    group_id BIGINT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES vehicle_devices(device_id),
    FOREIGN KEY (current_driver_id) REFERENCES drivers(driver_id),
    FOREIGN KEY (group_id) REFERENCES groups(group_id),
    INDEX idx_license_plate (license_plate),
    INDEX idx_device_id (device_id),
    INDEX idx_current_driver_id (current_driver_id),
    INDEX idx_group_id (group_id),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB COMMENT='車輛資料表';

-- 駕駛配對金鑰表
CREATE TABLE driver_pairing_keys (
    pairing_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    driver_id BIGINT NOT NULL,
    device_id BIGINT NOT NULL,
    pairing_token VARCHAR(255) NOT NULL,
    qr_code TEXT,
    token_status ENUM('active', 'used', 'expired') NOT NULL DEFAULT 'active',
    expires_at DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id),
    FOREIGN KEY (device_id) REFERENCES vehicle_devices(device_id),
    UNIQUE KEY uk_pairing_token (pairing_token),
    INDEX idx_driver_device (driver_id, device_id),
    INDEX idx_token_status (token_status),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB COMMENT='駕駛配對金鑰表';

-- =============================================================================
-- 4. 駕駛個案相關表
-- =============================================================================

-- 駕駛個案資料表
CREATE TABLE driving_cases (
    case_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    driver_id BIGINT NOT NULL,
    vehicle_id BIGINT NOT NULL,
    device_id BIGINT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    total_distance DECIMAL(10,2),
    total_duration INT,
    case_status ENUM('active', 'completed', 'cancelled') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id),
    FOREIGN KEY (device_id) REFERENCES vehicle_devices(device_id),
    INDEX idx_driver_id (driver_id),
    INDEX idx_vehicle_id (vehicle_id),
    INDEX idx_device_id (device_id),
    INDEX idx_start_time (start_time),
    INDEX idx_case_status (case_status),
    CONSTRAINT chk_total_distance CHECK (total_distance >= 0),
    CONSTRAINT chk_total_duration CHECK (total_duration >= 0)
) ENGINE=InnoDB COMMENT='駕駛個案資料表';

-- =============================================================================
-- 5. 影像資料相關表
-- =============================================================================

-- 原始影像資料表
CREATE TABLE raw_video_data (
    video_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    case_id BIGINT NOT NULL,
    camera_type ENUM('interior', 'exterior_front', 'exterior_rear') NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    duration INT NOT NULL,
    resolution VARCHAR(20),
    fps INT,
    start_timestamp DATETIME NOT NULL,
    end_timestamp DATETIME NOT NULL,
    upload_status ENUM('pending', 'uploaded', 'failed') NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES driving_cases(case_id),
    INDEX idx_case_id (case_id),
    INDEX idx_camera_type (camera_type),
    INDEX idx_start_timestamp (start_timestamp),
    INDEX idx_upload_status (upload_status),
    CONSTRAINT chk_file_size CHECK (file_size > 0),
    CONSTRAINT chk_duration CHECK (duration > 0)
) ENGINE=InnoDB COMMENT='原始影像資料表';

-- =============================================================================
-- 6. AI辨識資料相關表
-- =============================================================================

-- 物件資料表
CREATE TABLE object_detection_data (
    detection_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    case_id BIGINT NOT NULL,
    video_id BIGINT,
    object_type_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    bbox_x INT NOT NULL,
    bbox_y INT NOT NULL,
    bbox_width INT NOT NULL,
    bbox_height INT NOT NULL,
    distance DECIMAL(8,2),
    relative_speed DECIMAL(8,2),
    is_in_blind_spot BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES driving_cases(case_id),
    FOREIGN KEY (video_id) REFERENCES raw_video_data(video_id),
    FOREIGN KEY (object_type_id) REFERENCES object_types(object_type_id),
    INDEX idx_case_id (case_id),
    INDEX idx_video_id (video_id),
    INDEX idx_object_type_id (object_type_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_confidence (confidence),
    CONSTRAINT chk_confidence CHECK (confidence >= 0 AND confidence <= 1),
    CONSTRAINT chk_bbox_positive CHECK (bbox_width > 0 AND bbox_height > 0)
) ENGINE=InnoDB COMMENT='物件辨識資料表';

-- 車道線資料表
CREATE TABLE lane_detection_data (
    lane_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    case_id BIGINT NOT NULL,
    video_id BIGINT,
    timestamp DATETIME NOT NULL,
    lane_type ENUM('left', 'right', 'center') NOT NULL,
    lane_status ENUM('detected', 'missing', 'unclear') NOT NULL,
    deviation_distance DECIMAL(8,2),
    lane_confidence DECIMAL(5,4) NOT NULL,
    lane_curvature DECIMAL(10,6),
    is_crossing BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES driving_cases(case_id),
    FOREIGN KEY (video_id) REFERENCES raw_video_data(video_id),
    INDEX idx_case_id (case_id),
    INDEX idx_video_id (video_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_lane_type (lane_type),
    CONSTRAINT chk_lane_confidence CHECK (lane_confidence >= 0 AND lane_confidence <= 1)
) ENGINE=InnoDB COMMENT='車道線辨識資料表';

-- 燈號資料表
CREATE TABLE traffic_light_data (
    light_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    case_id BIGINT NOT NULL,
    video_id BIGINT,
    timestamp DATETIME NOT NULL,
    light_type ENUM('traffic_light', 'turn_signal', 'reverse_light') NOT NULL,
    light_color ENUM('red', 'yellow', 'green', 'off') NOT NULL,
    light_status ENUM('on', 'off', 'blinking') NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    distance DECIMAL(8,2),
    turn_signal_status ENUM('left', 'right', 'hazard', 'off'),
    reverse_gear_status BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES driving_cases(case_id),
    FOREIGN KEY (video_id) REFERENCES raw_video_data(video_id),
    INDEX idx_case_id (case_id),
    INDEX idx_video_id (video_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_light_type (light_type),
    CONSTRAINT chk_traffic_confidence CHECK (confidence >= 0 AND confidence <= 1)
) ENGINE=InnoDB COMMENT='交通燈號辨識資料表';

-- 臉部資料表
CREATE TABLE facial_detection_data (
    facial_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    case_id BIGINT NOT NULL,
    video_id BIGINT,
    timestamp DATETIME NOT NULL,
    face_detected BOOLEAN NOT NULL,
    drowsiness_level DECIMAL(5,4),
    attention_level DECIMAL(5,4),
    eye_closure_duration INT,
    head_pose_yaw DECIMAL(8,2),
    head_pose_pitch DECIMAL(8,2),
    head_pose_roll DECIMAL(8,2),
    emotion_state VARCHAR(50),
    is_using_phone BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES driving_cases(case_id),
    FOREIGN KEY (video_id) REFERENCES raw_video_data(video_id),
    INDEX idx_case_id (case_id),
    INDEX idx_video_id (video_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_face_detected (face_detected),
    CONSTRAINT chk_drowsiness_level CHECK (drowsiness_level IS NULL OR (drowsiness_level >= 0 AND drowsiness_level <= 1)),
    CONSTRAINT chk_attention_level CHECK (attention_level IS NULL OR (attention_level >= 0 AND attention_level <= 1))
) ENGINE=InnoDB COMMENT='臉部狀態辨識資料表';

-- =============================================================================
-- 7. 危險事件相關表
-- =============================================================================

-- 危險事件資料表
CREATE TABLE dangerous_events (
    event_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    case_id BIGINT NOT NULL,
    event_type_id INT NOT NULL,
    severity_id INT NOT NULL,
    start_timestamp DATETIME NOT NULL,
    end_timestamp DATETIME,
    duration INT,
    location_lat DECIMAL(10,8),
    location_lng DECIMAL(11,8),
    speed_kmh DECIMAL(6,2),
    acceleration DECIMAL(8,4),
    confidence_score DECIMAL(5,4) NOT NULL,
    warning_issued BOOLEAN NOT NULL DEFAULT FALSE,
    warning_timestamp DATETIME,
    event_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES driving_cases(case_id),
    FOREIGN KEY (event_type_id) REFERENCES event_types(event_type_id),
    FOREIGN KEY (severity_id) REFERENCES severity_levels(severity_id),
    INDEX idx_case_id (case_id),
    INDEX idx_event_type_id (event_type_id),
    INDEX idx_severity_id (severity_id),
    INDEX idx_start_timestamp (start_timestamp),
    INDEX idx_warning_issued (warning_issued),
    CONSTRAINT chk_event_confidence CHECK (confidence_score >= 0 AND confidence_score <= 1),
    CONSTRAINT chk_event_duration CHECK (duration IS NULL OR duration >= 0)
) ENGINE=InnoDB COMMENT='危險事件資料表';

-- =============================================================================
-- 8. 評分系統相關表
-- =============================================================================

-- 扣分標準表 (精簡版)
CREATE TABLE deduction_criteria (
    deduction_id INT AUTO_INCREMENT PRIMARY KEY,
    event_type_id INT NOT NULL,
    severity_id INT NOT NULL,
    deduction_points INT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_type_id) REFERENCES event_types(event_type_id),
    FOREIGN KEY (severity_id) REFERENCES severity_levels(severity_id),
    UNIQUE KEY uk_event_severity (event_type_id, severity_id),
    INDEX idx_is_active (is_active),
    CONSTRAINT chk_deduction_points CHECK (deduction_points > 0)
) ENGINE=InnoDB COMMENT='扣分標準表';

-- 駕駛個案評分資料表 (精簡版)
CREATE TABLE driving_case_scores (
    case_id BIGINT PRIMARY KEY,
    total_score DECIMAL(5,2) NOT NULL,
    total_deductions INT NOT NULL DEFAULT 0,
    gemini_feedback TEXT,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES driving_cases(case_id),
    INDEX idx_total_score (total_score),
    CONSTRAINT chk_total_score CHECK (total_score >= 0 AND total_score <= 100),
    CONSTRAINT chk_total_deductions CHECK (total_deductions >= 0)
) ENGINE=InnoDB COMMENT='駕駛個案評分資料表';

-- 評分細節表 (精簡版)
CREATE TABLE score_details (
    detail_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    case_id BIGINT NOT NULL,
    event_id BIGINT NOT NULL,
    deduction_points INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES driving_cases(case_id),
    FOREIGN KEY (event_id) REFERENCES dangerous_events(event_id),
    INDEX idx_case_id (case_id),
    INDEX idx_event_id (event_id),
    CONSTRAINT chk_deduction_points_detail CHECK (deduction_points > 0)
) ENGINE=InnoDB COMMENT='評分扣分細節表';

-- =============================================================================
-- 9. 初始化參考資料
-- =============================================================================

-- 插入事件類型基礎資料
INSERT INTO event_types (event_code, event_name, event_category, description) VALUES
('COLLISION_RISK', '碰撞風險', 'safety', '系統偵測到潛在碰撞風險'),
('LANE_DEPARTURE', '車道偏離', 'safety', '車輛偏離行駛車道'),
('DROWSY_DRIVING', '疲勞駕駛', 'behavior', '偵測到駕駛者疲勞狀態'),
('DISTRACTED_DRIVING', '分心駕駛', 'behavior', '駕駛者注意力不集中'),
('SPEEDING', '超速行駛', 'compliance', '超過限制速度行駛'),
('HARSH_BRAKING', '急煞車', 'efficiency', '緊急煞車行為'),
('HARSH_ACCELERATION', '急加速', 'efficiency', '急速加速行為'),
('PHONE_USAGE', '使用手機', 'behavior', '駕駛時使用手機'),
('BLIND_SPOT_DETECTION', '盲區偵測', 'safety', '盲區有物件存在'),
('TRAFFIC_VIOLATION', '交通違規', 'compliance', '違反交通規則');

-- 插入嚴重程度基礎資料
INSERT INTO severity_levels (severity_code, severity_name, severity_weight, color_code) VALUES
('LOW', '低', 1.0, '#28a745'),
('MEDIUM', '中', 2.0, '#ffc107'),
('HIGH', '高', 3.5, '#fd7e14'),
('CRITICAL', '嚴重', 5.0, '#dc3545');

-- 插入物件類型基礎資料
INSERT INTO object_types (type_code, type_name, category, risk_level) VALUES
('CAR', '汽車', 'vehicle', 3),
('TRUCK', '卡車', 'vehicle', 4),
('BUS', '公車', 'vehicle', 4),
('MOTORCYCLE', '機車', 'vehicle', 3),
('BICYCLE', '腳踏車', 'vehicle', 2),
('PEDESTRIAN', '行人', 'person', 5),
('TRAFFIC_LIGHT', '交通號誌', 'infrastructure', 4),
('ROAD_SIGN', '道路標誌', 'infrastructure', 3),
('BARRIER', '護欄', 'infrastructure', 2),
('ANIMAL', '動物', 'other', 3);

-- =============================================================================
-- 10. 建立視圖 (Views)
-- =============================================================================

-- 駕駛個案詳細資訊視圖 (精簡版)
CREATE VIEW v_driving_case_details AS
SELECT 
    dc.case_id,
    dc.start_time,
    dc.end_time,
    dc.total_distance,
    dc.total_duration,
    dc.case_status,
    d.full_name AS driver_name,
    d.employee_id,
    v.license_plate,
    v.vehicle_make,
    v.vehicle_model,
    vd.device_serial,
    g.group_name,
    dcs.total_score,
    dcs.total_deductions
FROM driving_cases dc
LEFT JOIN drivers d ON dc.driver_id = d.driver_id
LEFT JOIN vehicles v ON dc.vehicle_id = v.vehicle_id
LEFT JOIN vehicle_devices vd ON dc.device_id = vd.device_id
LEFT JOIN groups g ON d.group_id = g.group_id
LEFT JOIN driving_case_scores dcs ON dc.case_id = dcs.case_id;

-- 危險事件統計視圖
CREATE VIEW v_dangerous_event_summary AS
SELECT 
    de.case_id,
    COUNT(*) AS total_events,
    SUM(CASE WHEN sl.severity_code = 'CRITICAL' THEN 1 ELSE 0 END) AS critical_events,
    SUM(CASE WHEN sl.severity_code = 'HIGH' THEN 1 ELSE 0 END) AS high_events,
    SUM(CASE WHEN sl.severity_code = 'MEDIUM' THEN 1 ELSE 0 END) AS medium_events,
    SUM(CASE WHEN sl.severity_code = 'LOW' THEN 1 ELSE 0 END) AS low_events,
    COUNT(DISTINCT et.event_category) AS event_categories
FROM dangerous_events de
JOIN event_types et ON de.event_type_id = et.event_type_id
JOIN severity_levels sl ON de.severity_id = sl.severity_id
GROUP BY de.case_id;

-- 駕駛者績效統計視圖 (精簡版)
CREATE VIEW v_driver_performance AS
SELECT 
    d.driver_id,
    d.full_name,
    d.employee_id,
    COUNT(dc.case_id) AS total_trips,
    AVG(dcs.total_score) AS avg_score,
    SUM(dcs.total_deductions) AS total_deductions,
    SUM(des.total_events) AS total_dangerous_events,
    SUM(des.critical_events) AS total_critical_events
FROM drivers d
LEFT JOIN driving_cases dc ON d.driver_id = dc.driver_id
LEFT JOIN driving_case_scores dcs ON dc.case_id = dcs.case_id
LEFT JOIN v_dangerous_event_summary des ON dc.case_id = des.case_id
WHERE dc.case_status = 'completed'
GROUP BY d.driver_id, d.full_name, d.employee_id;

-- =============================================================================
-- 11. 建立觸發器 (Triggers)
-- =============================================================================

-- 觸發器：更新群組成員數量
DELIMITER $
CREATE TRIGGER tr_update_group_member_count_insert
AFTER INSERT ON drivers
FOR EACH ROW
BEGIN
    IF NEW.group_id IS NOT NULL THEN
        UPDATE groups 
        SET current_members = current_members + 1 
        WHERE group_id = NEW.group_id;
    END IF;
END$

CREATE TRIGGER tr_update_group_member_count_update
AFTER UPDATE ON drivers
FOR EACH ROW
BEGIN
    -- 如果從一個群組移到另一個群組
    IF OLD.group_id != NEW.group_id THEN
        -- 減少舊群組成員數
        IF OLD.group_id IS NOT NULL THEN
            UPDATE groups 
            SET current_members = current_members - 1 
            WHERE group_id = OLD.group_id;
        END IF;
        -- 增加新群組成員數
        IF NEW.group_id IS NOT NULL THEN
            UPDATE groups 
            SET current_members = current_members + 1 
            WHERE group_id = NEW.group_id;
        END IF;
    END IF;
END$

CREATE TRIGGER tr_update_group_member_count_delete
AFTER DELETE ON drivers
FOR EACH ROW
BEGIN
    IF OLD.group_id IS NOT NULL THEN
        UPDATE groups 
        SET current_members = current_members - 1 
        WHERE group_id = OLD.group_id;
    END IF;
END$

-- 觸發器：自動計算危險事件持續時間
CREATE TRIGGER tr_calculate_event_duration
BEFORE UPDATE ON dangerous_events
FOR EACH ROW
BEGIN
    IF NEW.end_timestamp IS NOT NULL AND NEW.start_timestamp IS NOT NULL THEN
        SET NEW.duration = TIMESTAMPDIFF(SECOND, NEW.start_timestamp, NEW.end_timestamp);
    END IF;
END$

DELIMITER ;

-- =============================================================================
-- 12. 建立預存程序 (Stored Procedures)
-- =============================================================================

-- 預存程序：計算駕駛個案評分
DELIMITER $
CREATE PROCEDURE sp_calculate_driving_score(IN p_case_id BIGINT)
BEGIN
    DECLARE v_base_score INT DEFAULT 100;
    DECLARE v_total_deduction INT DEFAULT 0;
    DECLARE v_final_score DECIMAL(6,2);
    DECLARE v_safety_score DECIMAL(6,2) DEFAULT 100;
    DECLARE v_efficiency_score DECIMAL(6,2) DEFAULT 100;
    DECLARE v_compliance_score DECIMAL(6,2) DEFAULT 100;
    DECLARE v_behavior_score DECIMAL(6,2) DEFAULT 100;
    
    -- 計算總扣分
    SELECT COALESCE(SUM(dc.deduction_points), 0)
    INTO v_total_deduction
    FROM dangerous_events de
    JOIN deduction_criteria dc ON de.event_type_id = dc.event_type_id 
                               AND de.severity_id = dc.severity_id
    WHERE de.case_id = p_case_id AND dc.is_active = TRUE;
    
    -- 計算分類扣分
    SELECT COALESCE(SUM(CASE WHEN et.event_category = 'safety' THEN dc.deduction_points ELSE 0 END), 0)
    INTO @safety_deduction
    FROM dangerous_events de
    JOIN event_types et ON de.event_type_id = et.event_type_id
    JOIN deduction_criteria dc ON de.event_type_id = dc.event_type_id 
                               AND de.severity_id = dc.severity_id
    WHERE de.case_id = p_case_id AND dc.is_active = TRUE;
    
    SELECT COALESCE(SUM(CASE WHEN et.event_category = 'efficiency' THEN dc.deduction_points ELSE 0 END), 0)
    INTO @efficiency_deduction
    FROM dangerous_events de
    JOIN event_types et ON de.event_type_id = et.event_type_id
    JOIN deduction_criteria dc ON de.event_type_id = dc.event_type_id 
                               AND de.severity_id = dc.severity_id
    WHERE de.case_id = p_case_id AND dc.is_active = TRUE;
    
    SELECT COALESCE(SUM(CASE WHEN et.event_category = 'compliance' THEN dc.deduction_points ELSE 0 END), 0)
    INTO @compliance_deduction
    FROM dangerous_events de
    JOIN event_types et ON de.event_type_id = et.event_type_id
    JOIN deduction_criteria dc ON de.event_type_id = dc.event_type_id 
                               AND de.severity_id = dc.severity_id
    WHERE de.case_id = p_case_id AND dc.is_active = TRUE;
    
    SELECT COALESCE(SUM(CASE WHEN et.event_category = 'behavior' THEN dc.deduction_points ELSE 0 END), 0)
    INTO @behavior_deduction
    FROM dangerous_events de
    JOIN event_types et ON de.event_type_id = et.event_type_id
    JOIN deduction_criteria dc ON de.event_type_id = dc.event_type_id 
                               AND de.severity_id = dc.severity_id
    WHERE de.case_id = p_case_id AND dc.is_active = TRUE;
    
    -- 計算各項分數
    SET v_safety_score = GREATEST(0, 100 - @safety_deduction);
    SET v_efficiency_score = GREATEST(0, 100 - @efficiency_deduction);
    SET v_compliance_score = GREATEST(0, 100 - @compliance_deduction);
    SET v_behavior_score = GREATEST(0, 100 - @behavior_deduction);
    SET v_final_score = GREATEST(0, v_base_score - v_total_deduction);
    
    -- 插入或更新評分記錄
    INSERT INTO driving_case_scores (
        case_id, total_score, safety_score, efficiency_score, 
        compliance_score, behavior_score, total_deductions, calculated_at
    ) VALUES (
        p_case_id, v_final_score, v_safety_score, v_efficiency_score,
        v_compliance_score, v_behavior_score, v_total_deduction, NOW()
    ) ON DUPLICATE KEY UPDATE
        total_score = v_final_score,
        safety_score = v_safety_score,
        efficiency_score = v_efficiency_score,
        compliance_score = v_compliance_score,
        behavior_score = v_behavior_score,
        total_deductions = v_total_deduction,
        calculated_at = NOW();
        
END$

DELIMITER ;

-- =============================================================================
-- 13. 建立索引優化
-- =============================================================================

-- 複合索引優化
CREATE INDEX idx_case_timestamp ON dangerous_events(case_id, start_timestamp);
CREATE INDEX idx_driver_date ON driving_cases(driver_id, start_time);
CREATE INDEX idx_video_camera_timestamp ON raw_video_data(camera_type, start_timestamp);
CREATE INDEX idx_detection_type_timestamp ON object_detection_data(object_type_id, timestamp);

-- 全文檢索索引
-- CREATE FULLTEXT INDEX ft_event_description ON dangerous_events(event_description);
-- CREATE FULLTEXT INDEX ft_gemini_feedback ON driving_case_scores(gemini_feedback);

-- =============================================================================
-- 14. 權限設定範例
-- =============================================================================

-- 建立應用程式使用者
-- CREATE USER 'dashcam_app'@'localhost' IDENTIFIED BY 'secure_password_here';
-- GRANT SELECT, INSERT, UPDATE ON smart_dashcam_system.* TO 'dashcam_app'@'localhost';

-- 建立唯讀使用者
-- CREATE USER 'dashcam_readonly'@'localhost' IDENTIFIED BY 'readonly_password_here';
-- GRANT SELECT ON smart_dashcam_system.* TO 'dashcam_readonly'@'localhost';

-- 建立管理員使用者
-- CREATE USER 'dashcam_admin'@'localhost' IDENTIFIED BY 'admin_password_here';
-- GRANT ALL PRIVILEGES ON smart_dashcam_system.* TO 'dashcam_admin'@'localhost';

-- =============================================================================
-- 15. 資料庫設定優化
-- =============================================================================

-- 設定 InnoDB 緩衝池大小 (建議設定為可用記憶體的 70-80%)
-- SET GLOBAL innodb_buffer_pool_size = 1073741824; -- 1GB

-- 設定查詢快取
-- SET GLOBAL query_cache_size = 268435456; -- 256MB
-- SET GLOBAL query_cache_type = ON;

-- 設定連線數限制
-- SET GLOBAL max_connections = 500;

-- 設定慢查詢日誌
-- SET GLOBAL slow_query_log = 'ON';
-- SET GLOBAL long_query_time = 2;

-- =============================================================================
-- 建立完成
-- =============================================================================
SELECT 'Smart Dashcam Database Created Successfully!' AS Status;
