CREATE TABLE IF NOT EXISTS raw_camera_images (
  id INTEGER PRIMARY KEY AUTOINCREMENT,                          -- 主鍵，自動遞增
  device_serial TEXT NOT NULL,                                   -- 車機序號
  camera_position TEXT NOT NULL,                                 -- 鏡頭位置
  image_path TEXT NOT NULL,                                      -- 影像檔案路徑
  capture_time TEXT NOT NULL,                                    -- 拍攝時間 (ISO 8601 字串)
  file_size INTEGER DEFAULT NULL,                               -- 檔案大小（bytes）
  image_format TEXT DEFAULT NULL,                               -- 檔案格式
  uploaded INTEGER DEFAULT 0,                                   -- 是否已上傳伺服器（0未上傳，1已上傳）
  upload_time TEXT DEFAULT NULL,                                -- 上傳時間
  remarks TEXT DEFAULT NULL                                     -- 備註
);

CREATE INDEX IF NOT EXISTS idx_device_camera_time 
ON raw_camera_images(device_serial, camera_position, capture_time);
