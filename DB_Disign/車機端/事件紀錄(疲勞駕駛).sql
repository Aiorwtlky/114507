CREATE TABLE IF NOT EXISTS fatigue_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,                         -- 主鍵，自動遞增
  device_serial TEXT NOT NULL,                                  -- 車機序號
  event_time TEXT NOT NULL,                                     -- 事件發生時間（ISO 8601 格式）
  eye_closure_duration REAL NOT NULL,                           -- 眼睛閉合持續時間（秒）
  alert_level INTEGER DEFAULT 1,                                -- 警示等級（1一般，數字越大風險越高）
  image_path TEXT NOT NULL,                                     -- 事件截圖路徑
  notes TEXT DEFAULT NULL                                       -- 備註（如異常狀況）
);

CREATE INDEX IF NOT EXISTS idx_fatigue_events_time
ON fatigue_events(device_serial, event_time);