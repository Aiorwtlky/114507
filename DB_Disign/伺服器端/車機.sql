CREATE TABLE `devices` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主鍵，自動遞增',
  `device_serial` varchar(100) NOT NULL COMMENT '車機序號（唯一） -- 重設後保留',
  `manufacturer` varchar(100) NOT NULL COMMENT '製造廠名稱 -- 重設後保留',
  `hardware_version` varchar(50) DEFAULT NULL COMMENT '硬體版本',
  `software_version` varchar(50) NOT NULL COMMENT '軟體版本',
  `car_brand` varchar(100) DEFAULT NULL COMMENT '車輛品牌',
  `car_plate` varchar(50) DEFAULT NULL COMMENT '車牌號碼',
  `vehicle_type` varchar(50) DEFAULT NULL COMMENT '車種（如：大客車、小貨車）',
  `driver_position` varchar(50) DEFAULT NULL COMMENT '駕駛座位置（如：左駕、右駕）',
  `install_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '裝置安裝時間 -- 重設後保留',
  `bind_status` tinyint(1) DEFAULT '0' COMMENT '是否已綁定（0=否，1=是）',
  PRIMARY KEY (`id`),
  UNIQUE KEY `device_serial` (`device_serial`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
