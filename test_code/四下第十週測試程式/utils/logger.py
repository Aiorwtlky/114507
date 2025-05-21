# utils/logger.py

import os
from datetime import datetime

class WarningLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "warning_log.txt")

    def log_warning(self, camera_name, distance):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}] {camera_name} - Distance: {distance:.2f} m\n")
