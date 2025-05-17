CREATE TABLE IF NOT EXISTS fatigue_events (
  id INT NOT NULL AUTO_INCREMENT COMMENT '主鍵，自動遞增',             -- 主鍵，自動遞增
  device_serial VARCHAR(100) NOT NULL COMMENT '車機序號',              -- 車機序號
  event_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '事件發生時間',  -- 事件發生時間
  eye_closure_duration REAL NOT NULL COMMENT '眼睛閉合持續時間（秒）',  -- 眼睛閉合持續時間
  alert_level INT DEFAULT 1 COMMENT '警示等級（1為一般，數字越大風險越高）', -- 警示等級
  image_path VARCHAR(255) NOT NULL COMMENT '事件截圖路徑',            -- 事件截圖路徑
  notes TEXT DEFAULT NULL COMMENT '備註（如異常狀況）',              -- 備註
  PRIMARY KEY (id),
  INDEX idx_fatigue_events_time (device_serial, event_time)            -- 索引：加速基於車機序號與事件時間的查詢
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
