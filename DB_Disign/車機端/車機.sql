CREATE TABLE `local_device_info` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,                               -- 主鍵，自動遞增
  `device_serial` TEXT NOT NULL UNIQUE,                                 -- 車機序號（唯一） -- 重設後保留
  `manufacturer` TEXT NOT NULL,                                         -- 製造廠名稱 -- 重設後保留
  `hardware_version` TEXT,                                              -- 硬體版本
  `software_version` TEXT NOT NULL,                                     -- 軟體版本
  `car_brand` TEXT,                                                     -- 車輛品牌
  `car_plate` TEXT,                                                     -- 車牌號碼
  `vehicle_type` TEXT,                                                  -- 車種（如：大客車、小貨車）
  `driver_position` TEXT,                                               -- 駕駛座位置（如：左駕、右駕）
  `install_date` TEXT DEFAULT (datetime('now')),                        -- 裝置安裝時間 -- 重設後保留
  `bind_status` INTEGER DEFAULT 0                                       -- 是否已綁定（0=否，1=是）
);
