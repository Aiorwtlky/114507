CREATE TABLE IF NOT EXISTS penalty_details (
  id INT NOT NULL AUTO_INCREMENT COMMENT '主鍵，自動遞增',                 -- 主鍵，自動遞增
  score_detail_id INT NOT NULL COMMENT '評分細節ID（來自score_details表）', -- 來自score_details表的ID
  penalty_condition TEXT NOT NULL COMMENT '具體扣分條件',                -- 扣分條件描述（如：未打燈、煞車過急等）
  penalty_points DECIMAL(5,2) NOT NULL COMMENT '扣分數值',              -- 扣分數值
  penalty_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '扣分時間',  -- 扣分時間
  PRIMARY KEY (id),
  FOREIGN KEY (score_detail_id) REFERENCES score_details(id) ON DELETE CASCADE   -- 參照score_details表
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
