CREATE TABLE IF NOT EXISTS violation_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,                    -- 主鍵，自動遞增
  device_serial TEXT NOT NULL,                             -- 車機序號
  event_time TEXT NOT NULL DEFAULT (datetime('now')),     -- 事件時間（ISO 8601 字串）
  violation_type TEXT NOT NULL,                            -- 違規類型（如闖紅燈、未打燈、未起步）
  camera_position TEXT NOT NULL,                           -- 鏡頭位置（left/right/rear）
  image_path TEXT NOT NULL,                                -- 違規事件截圖路徑
  video_path TEXT DEFAULT NULL,                           -- 違規事件錄影路徑
  description TEXT DEFAULT NULL,                           -- 違規描述
  uploaded INTEGER DEFAULT 0                               -- 是否已上傳（0未上傳，1已上傳）
);

CREATE INDEX IF NOT EXISTS idx_violation_device_time
ON violation_events(device_serial, event_time);
