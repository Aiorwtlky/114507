CREATE TABLE `staff` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '主鍵，自動遞增',
  `staff_id` VARCHAR(50) NOT NULL COMMENT '人員編號（唯一）',
  `name` VARCHAR(100) NOT NULL COMMENT '姓名',
  `role` ENUM('driver', 'manager', 'equipment_staff', 'software_engineer') NOT NULL COMMENT '職務',
  `email` VARCHAR(100) DEFAULT NULL COMMENT '電子郵件',
  `phone` VARCHAR(20) DEFAULT NULL COMMENT '聯絡電話',
  `hire_date` DATE DEFAULT NULL COMMENT '加入日期',
  `status` ENUM('active', 'inactive') DEFAULT 'active' COMMENT '在職狀態',
  `last_login` TIMESTAMP NULL DEFAULT NULL COMMENT '最後登入時間',
  PRIMARY KEY (`id`),
  UNIQUE KEY `staff_id` (`staff_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
