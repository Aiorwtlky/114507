CREATE TABLE IF NOT EXISTS raw_camera_images (
  id INT NOT NULL AUTO_INCREMENT COMMENT '主鍵，自動遞增',                 -- 主鍵，自動遞增
  device_serial VARCHAR(100) NOT NULL COMMENT '車機序號',                   -- 車機序號
  camera_position VARCHAR(50) NOT NULL COMMENT '鏡頭位置',                  -- 鏡頭位置
  image_path VARCHAR(255) NOT NULL COMMENT '影像檔案路徑',                 -- 影像檔案路徑
  capture_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '拍攝時間', -- 拍攝時間（MySQL 使用 TIMESTAMP）
  file_size INT DEFAULT NULL COMMENT '檔案大小（bytes）',                 -- 檔案大小（bytes）
  image_format VARCHAR(50) DEFAULT NULL COMMENT '檔案格式',                -- 檔案格式
  uploaded TINYINT(1) DEFAULT 0 COMMENT '是否已上傳伺服器（0未上傳，1已上傳）', -- 是否已上傳伺服器
  upload_time TIMESTAMP DEFAULT NULL COMMENT '上傳時間',                  -- 上傳時間
  remarks TEXT DEFAULT NULL COMMENT '備註',                             -- 備註
  PRIMARY KEY (id),
  INDEX idx_device_camera_time (device_serial, camera_position, capture_time)  -- 建立索引：加速基於車機序號、鏡頭位置和時間的查詢
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
