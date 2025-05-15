CREATE TABLE IF NOT EXISTS event_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,                             -- 主鍵，自動遞增
  device_serial TEXT NOT NULL,                                      -- 車機序號
  camera_position TEXT NOT NULL,                                    -- 鏡頭位置
  event_time TEXT NOT NULL DEFAULT (datetime('now')),              -- 事件發生時間 (ISO 8601 格式字串)
  detected_objects TEXT NOT NULL,                                   -- 偵測物件名稱列表（逗號分隔）
  alert_level INTEGER DEFAULT 1,                                   -- 警示等級（1為一般，數字越大風險越高）
  image_path TEXT NOT NULL,                                         -- 事件截圖路徑
  video_path TEXT DEFAULT NULL,                                    -- 事件錄影路徑
  uploaded INTEGER DEFAULT 0                                        -- 是否已上傳伺服器（0未上傳，1已上傳）
);

CREATE INDEX IF NOT EXISTS idx_device_event_time
ON event_logs(device_serial, event_time);
