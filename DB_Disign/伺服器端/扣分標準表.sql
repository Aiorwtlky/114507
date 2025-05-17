CREATE TABLE IF NOT EXISTS penalty_criteria (
  id INT NOT NULL AUTO_INCREMENT COMMENT '主鍵，自動遞增',
  criteria_id INT NOT NULL COMMENT '評分標準ID（來自scoring_criteria表）',
  penalty_condition VARCHAR(255) NOT NULL COMMENT '扣分條件',
  penalty_points DECIMAL(5,2) NOT NULL COMMENT '扣分數值',
  PRIMARY KEY (id),
  FOREIGN KEY (criteria_id) REFERENCES scoring_criteria(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
