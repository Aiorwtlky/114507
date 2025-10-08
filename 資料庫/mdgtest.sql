-- 智慧行車記錄器系統資料庫 - 簡化實用版本
-- 版本: Final
-- 建立日期: 2025-08-30
-- 資料表數量: 11張

CREATE DATABASE my_driving_god
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE my_driving_god;

-- 智慧車隊安全系統資料庫架構 - 最終版
-- 版本: 2025-08-29

-- 為了確保腳本可以重複執行，先暫時關閉外鍵檢查
SET FOREIGN_KEY_CHECKS=0;

-- 如果需要，可以加入刪除舊資料表和檢視表的指令 (開發時常用)
DROP VIEW IF EXISTS personnel_trip_stats, group_trip_stats;
DROP TABLE IF EXISTS video_record, ai_vision_log, scoring_standard, route_log, trip, group_announcement, group_member, vehicle_device, `group`, system_announcement, personnel;

-- =======================================================
-- 步驟一：建立無依賴的基礎資料表
-- =======================================================

-- 1. 人員管理資料表
CREATE TABLE personnel (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '流水號',
    personnel_number VARCHAR(50) NOT NULL UNIQUE COMMENT '人員編號',
    name VARCHAR(100) NOT NULL COMMENT '姓名',
    email VARCHAR(255) NOT NULL UNIQUE COMMENT '電子郵件',
    password VARCHAR(255) NOT NULL COMMENT '密碼',
    gender VARCHAR(10) NOT NULL COMMENT '性別',
    license_number VARCHAR(50) NOT NULL UNIQUE COMMENT '駕照號碼',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='人員管理資料表';

-- 2. 群組管理資料表
CREATE TABLE `group` (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '流水號',
    group_number VARCHAR(50) NOT NULL UNIQUE COMMENT '群組編號',
    name VARCHAR(100) NOT NULL COMMENT '群組名稱',
    description TEXT COMMENT '群組敘述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='群組管理資料表';

-- 3. 系統公告資料表
CREATE TABLE system_announcement (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '流水號',
    announcement_number VARCHAR(50) NOT NULL UNIQUE COMMENT '公告編號',
    content TEXT NOT NULL COMMENT '公告內容',
    date DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '公告日期',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否啟用'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系統公告資料表';

-- 4. 車機資料表
CREATE TABLE vehicle_device (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '流水號',
    device_number VARCHAR(50) NOT NULL UNIQUE COMMENT '車機編號',
    vehicle_type VARCHAR(20) NOT NULL COMMENT '車輛類型',
    activation_date DATE NOT NULL COMMENT '車機啟用日',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否啟用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='車機資料表';

-- 5. 評分標準資料表
CREATE TABLE scoring_standard (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '流水號',
    event_number VARCHAR(50) NOT NULL UNIQUE COMMENT '事件編號',
    description VARCHAR(255) NOT NULL COMMENT '事件敘述',
    deduction_points INT NOT NULL COMMENT '扣分數值',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否啟用'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='評分標準資料表';

-- =======================================================
-- 步驟二：建立有關聯的資料表
-- =======================================================

-- 6. 群組人員資料表 (依賴 personnel, group)
CREATE TABLE group_member (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '流水號',
    group_id BIGINT NOT NULL COMMENT '群組ID',
    personnel_id BIGINT NOT NULL COMMENT '人員ID',
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '加入時間',
    FOREIGN KEY (group_id) REFERENCES `group`(id) ON DELETE CASCADE,
    FOREIGN KEY (personnel_id) REFERENCES personnel(id) ON DELETE CASCADE,
    UNIQUE KEY uk_group_personnel (group_id, personnel_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='群組人員資料表';

-- 7. 群組公告資料表 (依賴 personnel, group)
CREATE TABLE group_announcement (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '流水號',
    announcement_number VARCHAR(50) NOT NULL UNIQUE COMMENT '公告編號',
    group_id BIGINT NOT NULL COMMENT '群組ID',
    publisher_id BIGINT NOT NULL COMMENT '發布者ID',
    content TEXT NOT NULL COMMENT '公告內容',
    publish_date DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '發布日期',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否啟用',
    FOREIGN KEY (group_id) REFERENCES `group`(id) ON DELETE CASCADE,
    FOREIGN KEY (publisher_id) REFERENCES personnel(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='群組公告資料表';

-- 8. 行程管理資料表 (依賴 personnel, group, vehicle_device)
CREATE TABLE trip (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '流水號',
    trip_number VARCHAR(50) NOT NULL UNIQUE COMMENT '行程編號',
    name VARCHAR(200) NOT NULL COMMENT '行程名稱',
    group_id BIGINT NOT NULL COMMENT '群組ID',
    device_id BIGINT NOT NULL COMMENT '車機ID',
    personnel_id BIGINT NOT NULL COMMENT '駕駛員ID',
    score DECIMAL(5,2) NULL COMMENT '行程評分',
    ai_suggestion TEXT COMMENT 'AI建議',
    start_time DATETIME NULL COMMENT '開始時間',
    end_time DATETIME NULL COMMENT '結束時間',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    FOREIGN KEY (group_id) REFERENCES `group`(id) ON DELETE CASCADE,
    FOREIGN KEY (device_id) REFERENCES vehicle_device(id) ON DELETE CASCADE,
    FOREIGN KEY (personnel_id) REFERENCES personnel(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='行程管理資料表';

-- 9. 路程管理資料表 (依賴 trip)
CREATE TABLE route_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '流水號',
    trip_id BIGINT NOT NULL COMMENT '行程ID',
    timestamp DATETIME NOT NULL COMMENT '行程時間點',
    location VARCHAR(100) NOT NULL COMMENT '經緯度',
    speed FLOAT NULL COMMENT '車速',
    FOREIGN KEY (trip_id) REFERENCES trip(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='路程管理資料表';

-- 10. AI視覺資料表 (依賴 trip, scoring_standard)
CREATE TABLE ai_vision_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '流水號',
    trip_id BIGINT NOT NULL COMMENT '行程ID',
    event_id INT NOT NULL COMMENT '事件類型ID',
    timestamp DATETIME NOT NULL COMMENT '事件發生時間',
    event_details VARCHAR(255) NOT NULL COMMENT '事件詳細內容',
    confidence_score FLOAT NULL COMMENT '信心分數',
    FOREIGN KEY (trip_id) REFERENCES trip(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES scoring_standard(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI視覺資料表';

-- 11. 影像紀錄資料表 (依賴 trip)
CREATE TABLE video_record (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '流水號',
    video_number VARCHAR(50) NOT NULL UNIQUE COMMENT '影像編號',
    trip_id BIGINT NOT NULL COMMENT '行程ID',
    start_time DATETIME NOT NULL COMMENT '開始錄影時間',
    end_time DATETIME NOT NULL COMMENT '結束錄影時間',
    location VARCHAR(500) NOT NULL COMMENT '影像存放位置',
    file_size BIGINT NULL COMMENT '檔案大小(bytes)',
    FOREIGN KEY (trip_id) REFERENCES trip(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='影像紀錄資料表';

-- =======================================================
-- 步驟三：插入基礎資料與建立檢視表
-- =======================================================

-- 插入最終版的評分標準資料 (已加入"駕駛中使用手機")
INSERT INTO scoring_standard (event_number, description, deduction_points) VALUES
('A01', '重度疲勞駕駛 (閉眼超過3秒)', 25),
('A02', '中度疲勞駕駛 (閉眼1-3秒)', 15),
('A03', '長時間分心 (低頭/轉頭超過5秒)', 20),
('A04', '駕駛中使用手機', 20),
('B01', '車道偏離 (未打方向燈)', 5),
('B02', '前車過近', 15),
('B03', '行人逼近', 20);

-- 建立檢視表：人員行程統計
CREATE VIEW personnel_trip_stats AS
SELECT 
    p.id, p.personnel_number, p.name,
    COUNT(t.id) as total_trips,
    AVG(t.score) as avg_score,
    MAX(t.score) as best_score,
    MIN(t.score) as worst_score
FROM personnel p
LEFT JOIN trip t ON p.id = t.personnel_id
GROUP BY p.id, p.personnel_number, p.name;

-- 建立檢視表：群組行程統計
CREATE VIEW group_trip_stats AS
SELECT 
    g.id, g.group_number, g.name,
    COUNT(t.id) as total_trips,
    AVG(t.score) as avg_score,
    COUNT(DISTINCT t.personnel_id) as active_drivers
FROM `group` g
LEFT JOIN trip t ON g.id = t.group_id
GROUP BY g.id, g.group_number, g.name;

-- 重新開啟外鍵檢查，確保資料庫完整性
SET FOREIGN_KEY_CHECKS=1;
