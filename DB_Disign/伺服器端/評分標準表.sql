CREATE TABLE IF NOT EXISTS scoring_criteria (
  id INT NOT NULL AUTO_INCREMENT COMMENT '主鍵，自動遞增',
  criteria_name VARCHAR(100) NOT NULL COMMENT '評分標準名稱（如：轉彎未打燈、打瞌睡等）',
  description TEXT COMMENT '評分標準描述',
  max_score INT DEFAULT 10 COMMENT '最大得分',
  min_score INT DEFAULT 0 COMMENT '最小得分（扣分範圍）',
  weight DECIMAL(5,2) DEFAULT 1.00 COMMENT '該項標準的權重',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
