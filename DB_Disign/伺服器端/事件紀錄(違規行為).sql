CREATE TABLE IF NOT EXISTS violation_events (
  id INT NOT NULL AUTO_INCREMENT COMMENT '主鍵，自動遞增',                   -- 主鍵，自動遞增
  device_serial VARCHAR(100) NOT NULL COMMENT '車機序號',                    -- 車機序號
  event_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '事件發生時間', -- 事件時間
  violation_type VARCHAR(100) NOT NULL COMMENT '違規類型（如闖紅燈、未打燈、未起步）', -- 違規類型
  camera_position VARCHAR(50) NOT NULL COMMENT '鏡頭位置（left/right/rear）',  -- 鏡頭位置
  image_path VARCHAR(255) NOT NULL COMMENT '違規事件截圖路徑',                -- 違規事件截圖路徑
  video_path VARCHAR(255) DEFAULT NULL COMMENT '違規事件錄影路徑',             -- 違規事件錄影路徑
  description TEXT DEFAULT NULL COMMENT '違規描述',                           -- 違規描述
  uploaded TINYINT(1) DEFAULT 0 COMMENT '是否已上傳（0未上傳，1已上傳）',       -- 是否已上傳伺服器（0未上傳，1已上傳）
  PRIMARY KEY (id),
  INDEX idx_violation_device_time (device_serial, event_time)                 -- 索引：加速基於車機序號與事件時間的查詢
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
