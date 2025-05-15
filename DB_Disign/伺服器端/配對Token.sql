CREATE TABLE `tokens` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主鍵，自動遞增',
  `device_serial` varchar(100) NOT NULL COMMENT '對應車機序號',
  `token` varchar(255) NOT NULL COMMENT '唯一識別用 Token 字串',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
  `expires_at` timestamp NULL DEFAULT NULL COMMENT 'Token 過期時間',
  `used` tinyint(1) DEFAULT '0' COMMENT '是否已使用（0=未使用，1=已使用）',
  `is_reset` tinyint(1) DEFAULT '0' COMMENT '是否為重設用途（0=綁定，1=重設）',
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`),
  KEY `idx_device_serial` (`device_serial`)
) ENGINE=InnoDB AUTO_INCREMENT=155 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
