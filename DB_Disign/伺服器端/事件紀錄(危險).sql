CREATE TABLE IF NOT EXISTS event_logs (
  id INT NOT NULL AUTO_INCREMENT COMMENT '主鍵，自動遞增',                      -- 主鍵，自動遞增
  device_serial VARCHAR(100) NOT NULL COMMENT '車機序號',                        -- 車機序號
  camera_position VARCHAR(50) NOT NULL COMMENT '鏡頭位置',                       -- 鏡頭位置
  event_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '事件發生時間',  -- 事件發生時間
  detected_objects TEXT NOT NULL COMMENT '偵測物件名稱列表（逗號分隔）',          -- 偵測物件名稱列表（逗號分隔）
  alert_level INT DEFAULT 1 COMMENT '警示等級（1為一般，數字越大風險越高）',     -- 警示等級（1為一般，數字越大風險越高）
  image_path VARCHAR(255) NOT NULL COMMENT '事件截圖路徑',                      -- 事件截圖路徑
  video_path VARCHAR(255) DEFAULT NULL COMMENT '事件錄影路徑',                   -- 事件錄影路徑
  uploaded TINYINT(1) DEFAULT 0 COMMENT '是否已上傳伺服器（0未上傳，1已上傳）',  -- 是否已上傳伺服器（0未上傳，1已上傳）
  PRIMARY KEY (id), 
  INDEX idx_device_event_time (device_serial, event_time)                      -- 索引設置
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
