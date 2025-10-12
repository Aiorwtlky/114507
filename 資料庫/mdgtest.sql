-- #############################################################################
-- -- 1. 人員與權限管理 (User & Permission Management)
-- #############################################################################

-- 資料表: personnel_profile (人員詳細資料)
-- 說明: 一對一擴充 Django 內建的 User 模型，儲存人員的詳細資訊。
CREATE TABLE `personnel_profile` (
    `user_id` INT NOT NULL PRIMARY KEY,                 -- 使用者帳號 (主鍵 & 外鍵)
    `personnel_number` VARCHAR(50) NOT NULL UNIQUE,     -- 人員編號
    `gender` VARCHAR(20) NOT NULL DEFAULT 'UNSPECIFIED',-- 性別
    `license_number` VARCHAR(20) NOT NULL,              -- 駕照號碼
    `avatar` VARCHAR(100),                              -- 個人頭像 (儲存檔案路徑)
    `phone` VARCHAR(20) NOT NULL,                       -- 聯絡電話
    `license_type` VARCHAR(50) NOT NULL,                -- 駕照等級
    `driving_experience` INT UNSIGNED NOT NULL DEFAULT 0, -- 駕駛年資
    `nfc_card_id` VARCHAR(50) UNIQUE                    -- NFC 卡片識別碼
);

-- 資料表: `group` (群組)
-- 說明: 用於組織使用者的群組模型。
CREATE TABLE `group` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,             -- 群組 ID
    `group_number` VARCHAR(50) NOT NULL UNIQUE,         -- 群組編號
    `name` VARCHAR(100) NOT NULL,                       -- 群組名稱
    `description` TEXT,                                 -- 描述
    `created_at` DATETIME NOT NULL,                     -- 建立時間
    `updated_at` DATETIME NOT NULL,                     -- 更新時間
    `created_by_id` INT                                 -- 建立者 (外鍵)
);

-- 資料表: group_member (群組成員)
-- 說明: 群組與使用者之間的多對多中介模型，用於定義角色。
CREATE TABLE `group_member` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,             -- 成員關係 ID
    `joined_at` DATETIME NOT NULL,                      -- 加入時間
    `role` VARCHAR(10) NOT NULL DEFAULT 'MEMBER',       -- 群組角色
    `group_id` BIGINT NOT NULL,                         -- 所屬群組 (外鍵)
    `user_id` INT NOT NULL,                             -- 使用者 (外鍵)
    UNIQUE (`group_id`, `user_id`)                      -- 同一群組內的使用者不可重複
);

-- 資料表: activationcode (系統啟用碼)
-- 說明: 用於管理系統級別的、可多次使用的註冊啟用碼。
CREATE TABLE `activationcode` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,             -- 啟用碼 ID
    `code` VARCHAR(16) NOT NULL UNIQUE,                 -- 啟用碼
    `max_uses` INT UNSIGNED NOT NULL DEFAULT 50,        -- 最大使用次數
    `current_uses` INT UNSIGNED NOT NULL DEFAULT 0,     -- 當前使用次數
    `created_at` DATETIME NOT NULL,                     -- 建立時間
    `expires_at` DATETIME,                              -- 過期時間
    `notes` TEXT NOT NULL                               -- 備註
);


-- #############################################################################
-- -- 2. 系統與公告 (System & Announcement)
-- #############################################################################

-- 資料表: system_announcement (系統公告)
-- 說明: 系統級別的公告。
CREATE TABLE `system_announcement` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,             -- 公告 ID
    `announcement_number` VARCHAR(50) NOT NULL UNIQUE,  -- 公告編號
    `content` TEXT NOT NULL,                            -- 公告內容
    `date` DATETIME NOT NULL,                           -- 發布日期
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE           -- 是否啟用
);

-- 資料表: group_announcement (群組公告)
-- 說明: 群組內部公告。
CREATE TABLE `group_announcement` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,             -- 公告 ID
    `announcement_number` VARCHAR(50) NOT NULL UNIQUE,  -- 公告編號
    `content` TEXT NOT NULL,                            -- 公告內容
    `publish_date` DATETIME NOT NULL,                   -- 發布日期
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE,          -- 是否啟用
    `group_id` BIGINT NOT NULL,                         -- 所屬群組 (外鍵)
    `publisher_id` INT NOT NULL                         -- 發布者 (外鍵)
);

-- 資料表: invitationcode (群組邀請碼)
-- 說明: 具時效性、一次性的群組邀請碼。
CREATE TABLE `invitationcode` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,             -- 邀請碼 ID
    `name` VARCHAR(100) NOT NULL DEFAULT 'Default Invite', -- 邀請名稱
    `code` VARCHAR(8) NOT NULL UNIQUE,                  -- 邀請碼
    `created_at` DATETIME NOT NULL,                     -- 建立時間
    `expires_at` DATETIME NOT NULL,                     -- 過期時間
    `is_used` BOOLEAN NOT NULL DEFAULT FALSE,           -- 是否已使用
    `created_by_id` INT NOT NULL,                       -- 建立者 (外鍵)
    `group_id` BIGINT NOT NULL                          -- 所屬群組 (外鍵)
);


-- #############################################################################
-- -- 3. 車輛與行程管理 (Vehicle & Trip Management)
-- #############################################################################

-- 資料表: vehicle_device (車機設備)
-- 說明: 車機設備模型。
CREATE TABLE `vehicle_device` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,             -- 設備 ID
    `device_number` VARCHAR(50) NOT NULL UNIQUE,        -- 設備編號
    `vehicle_type` VARCHAR(20) NOT NULL,                -- 車輛類型
    `activation_date` DATE NOT NULL,                    -- 啟用日期
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE,          -- 是否啟用
    `created_at` DATETIME NOT NULL                      -- 建立時間
);

-- 資料表: trip (行程)
-- 說明: 核心的行程紀錄模型。
CREATE TABLE `trip` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,             -- 行程 ID
    `trip_number` VARCHAR(50) NOT NULL UNIQUE,          -- 行程編號
    `name` VARCHAR(200) NOT NULL,                       -- 行程名稱
    `score` DECIMAL(5, 2),                              -- 總評分
    `in_car_score` DECIMAL(5, 2),                       -- 車內評分
    `out_car_score` DECIMAL(5, 2),                      -- 車外評分
    `ai_suggestion` TEXT,                               -- AI 建議
    `start_time` DATETIME,                              -- 開始時間
    `end_time` DATETIME,                                -- 結束時間
    `created_at` DATETIME NOT NULL,                     -- 建立時間
    `total_mileage` DOUBLE,                             -- 總里程(KM)
    `device_id` BIGINT NOT NULL,                        -- 關聯設備 (外鍵)
    `group_id` BIGINT NOT NULL,                         -- 所屬群組 (外鍵)
    `personnel_id` INT NOT NULL                         -- 負責人員 (外鍵)
);

-- 資料表: scoring_standard (評分標準)
-- 說明: 定義危險駕駛事件的評分標準與扣分。
CREATE TABLE `scoring_standard` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,                -- 標準 ID
    `event_number` VARCHAR(50) NOT NULL UNIQUE,         -- 事件編號
    `description` VARCHAR(255) NOT NULL,                -- 事件描述
    `deduction_points` INT NOT NULL,                    -- 扣除分數
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE           -- 是否啟用
);

-- 資料表: ai_vision_log (AI視覺事件紀錄)
-- 說明: 儲存行程中由 AI 偵測到的具體駕駛事件。
CREATE TABLE `ai_vision_log` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,             -- 紀錄 ID
    `timestamp` DATETIME NOT NULL,                      -- 事件時間
    `event_details` VARCHAR(255) NOT NULL,              -- 事件詳情
    `confidence_score` DOUBLE,                          -- 信賴度分數
    `event_id` INT NOT NULL,                            -- 關聯事件 (外鍵)
    `trip_id` BIGINT NOT NULL                           -- 關聯行程 (外鍵)
);

-- 資料表: video_record (影像紀錄)
-- 說明: 儲存與行程關聯的影像紀錄資訊。
CREATE TABLE `video_record` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,             -- 紀錄 ID
    `video_number` VARCHAR(50) NOT NULL UNIQUE,         -- 影像編號
    `start_time` DATETIME NOT NULL,                     -- 開始時間
    `end_time` DATETIME NOT NULL,                       -- 結束時間
    `location` VARCHAR(500) NOT NULL,                   -- 儲存位置
    `file_size` BIGINT,                                 -- 檔案大小
    `video_url` VARCHAR(500),                           -- 影片雲端網址
    `trip_id` BIGINT NOT NULL                           -- 關聯行程 (外鍵)
);


-- #############################################################################
-- -- 4. 回饋 (Feedback)
-- #############################################################################

-- 資料表: tripsuggestionfeedback (AI行程建議回饋)
-- 說明: 用於儲存使用者對 AI 行程建議的回饋。
CREATE TABLE `tripsuggestionfeedback` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,             -- 回饋 ID
    `feedback_type` INT NOT NULL,                       -- 回饋類型 (1:有幫助, -1:沒有幫助)
    `comment` TEXT,                                     -- 使用者評論
    `timestamp` DATETIME NOT NULL,                      -- 回饋時間
    `trip_id` BIGINT NOT NULL,                          -- 關聯行程 (外鍵)
    `user_id` INT NOT NULL,                             -- 回饋使用者 (外鍵)
    UNIQUE (`trip_id`, `user_id`)                       -- 同一使用者對同一行程只能回饋一次
);


-- #############################################################################
-- -- FOREIGN KEY CONSTRAINTS (外鍵約束)
-- -- 說明: 在所有資料表建立完畢後，統一建立外鍵關聯。
-- -- 假設 Django 內建的使用者資料表名為 `auth_user`。
-- #############################################################################

-- personnel_profile 的外鍵
ALTER TABLE `personnel_profile` ADD CONSTRAINT `fk_personnel_profile_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

-- `group` 的外鍵
ALTER TABLE `group` ADD CONSTRAINT `fk_group_created_by_id` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);

-- group_member 的外鍵
ALTER TABLE `group_member` ADD CONSTRAINT `fk_group_member_group_id` FOREIGN KEY (`group_id`) REFERENCES `group` (`id`);
ALTER TABLE `group_member` ADD CONSTRAINT `fk_group_member_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

-- group_announcement 的外鍵
ALTER TABLE `group_announcement` ADD CONSTRAINT `fk_group_announcement_group_id` FOREIGN KEY (`group_id`) REFERENCES `group` (`id`);
ALTER TABLE `group_announcement` ADD CONSTRAINT `fk_group_announcement_publisher_id` FOREIGN KEY (`publisher_id`) REFERENCES `auth_user` (`id`);

-- invitationcode 的外鍵
ALTER TABLE `invitationcode` ADD CONSTRAINT `fk_invitationcode_created_by_id` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `invitationcode` ADD CONSTRAINT `fk_invitationcode_group_id` FOREIGN KEY (`group_id`) REFERENCES `group` (`id`);

-- trip 的外鍵
ALTER TABLE `trip` ADD CONSTRAINT `fk_trip_device_id` FOREIGN KEY (`device_id`) REFERENCES `vehicle_device` (`id`);
ALTER TABLE `trip` ADD CONSTRAINT `fk_trip_group_id` FOREIGN KEY (`group_id`) REFERENCES `group` (`id`);
ALTER TABLE `trip` ADD CONSTRAINT `fk_trip_personnel_id` FOREIGN KEY (`personnel_id`) REFERENCES `auth_user` (`id`);

-- ai_vision_log 的外鍵
ALTER TABLE `ai_vision_log` ADD CONSTRAINT `fk_ai_vision_log_event_id` FOREIGN KEY (`event_id`) REFERENCES `scoring_standard` (`id`);
ALTER TABLE `ai_vision_log` ADD CONSTRAINT `fk_ai_vision_log_trip_id` FOREIGN KEY (`trip_id`) REFERENCES `trip` (`id`);

-- video_record 的外鍵
ALTER TABLE `video_record` ADD CONSTRAINT `fk_video_record_trip_id` FOREIGN KEY (`trip_id`) REFERENCES `trip` (`id`);

-- tripsuggestionfeedback 的外鍵
ALTER TABLE `tripsuggestionfeedback` ADD CONSTRAINT `fk_tripsuggestionfeedback_trip_id` FOREIGN KEY (`trip_id`) REFERENCES `trip` (`id`);
ALTER TABLE `tripsuggestionfeedback` ADD CONSTRAINT `fk_tripsuggestionfeedback_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
