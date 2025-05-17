CREATE TABLE IF NOT EXISTS penalty_details (
  id INT NOT NULL AUTO_INCREMENT COMMENT '主鍵，自動遞增',
  score_detail_id INT NOT NULL COMMENT '評分細節ID（來自score_details表）',
  penalty_criteria_id INT NOT NULL COMMENT '扣分標準ID（來自penalty_criteria表）',
  penalty_condition TEXT NOT NULL COMMENT '扣分條件描述',
  penalty_points DECIMAL(5,2) NOT NULL COMMENT '扣分數值',
  penalty_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '扣分時間',
  PRIMARY KEY (id),
  FOREIGN KEY (score_detail_id) REFERENCES score_details(id) ON DELETE CASCADE,
  FOREIGN KEY (penalty_criteria_id) REFERENCES penalty_criteria(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
