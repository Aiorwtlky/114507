-- 智慧行車紀錄器系統資料庫建立語句
-- 版本: 1.0
-- 建立日期: 2025-08-05

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
    warning_issued BOOLEAN NOT NULL