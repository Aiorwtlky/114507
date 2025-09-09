import cv2
import numpy as np
import time
import psutil
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

def get_system_info() -> Dict:
    """取得系統資訊"""
    try:
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'temperature': get_cpu_temperature()
        }
    except Exception as e:
        logger.error(f"取得系統資訊失敗: {e}")
        return {}

def get_cpu_temperature() -> Optional[float]:
    """取得 CPU 溫度 (Raspberry Pi)"""
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = float(f.read()) / 1000.0
            return temp
    except:
        return None

def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """計算兩點間距離"""
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def normalize_landmarks(landmarks, image_width: int, image_height: int) -> List[Tuple[float, float]]:
    """正規化特徵點座標"""
    normalized = []
    for landmark in landmarks:
        x = landmark.x * image_width
        y = landmark.y * image_height
        normalized.append((x, y))
    return normalized

def draw_landmarks(image: np.ndarray, landmarks: List[Tuple[float, float]], 
                  color: Tuple[int, int, int] = (0, 255, 0), radius: int = 2) -> np.ndarray:
    """在影像上繪製特徵點"""
    for point in landmarks:
        cv2.circle(image, (int(point[0]), int(point[1])), radius, color, -1)
    return image

def resize_frame(frame: np.ndarray, target_width: int, target_height: int) -> np.ndarray:
    """調整影像大小"""
    return cv2.resize(frame, (target_width, target_height))

def create_video_writer(output_path: str, fps: int, width: int, height: int) -> cv2.VideoWriter:
    """建立影片寫入器"""
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    return cv2.VideoWriter(output_path, fourcc, fps, (width, height))

def cleanup_old_files(directory: str, max_files: int):
    """清理舊檔案"""
    try:
        import os
        import glob
        
        files = glob.glob(os.path.join(directory, "*"))
        files.sort(key=os.path.getctime)
        
        if len(files) > max_files:
            files_to_remove = files[:-max_files]
            for file_path in files_to_remove:
                os.remove(file_path)
                logger.info(f"已刪除舊檔案: {file_path}")
                
    except Exception as e:
        logger.error(f"清理檔案失敗: {e}")

class PerformanceMonitor:
    """效能監控器"""
    
    def __init__(self):
        self.frame_times = []
        self.last_frame_time = time.time()
    
    def update(self):
        """更新效能統計"""
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        self.frame_times.append(frame_time)
        
        # 保持最近 30 幀的統計
        if len(self.frame_times) > 30:
            self.frame_times.pop(0)
        
        self.last_frame_time = current_time
    
    def get_fps(self) -> float:
        """取得當前 FPS"""
        if len(self.frame_times) > 0:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            return 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        return 0
    
    def get_stats(self) -> Dict:
        """取得詳細統計"""
        if len(self.frame_times) == 0:
            return {'fps': 0, 'avg_frame_time': 0, 'min_frame_time': 0, 'max_frame_time': 0}
        
        return {
            'fps': self.get_fps(),
            'avg_frame_time': sum(self.frame_times) / len(self.frame_times),
            'min_frame_time': min(self.frame_times),
            'max_frame_time': max(self.frame_times)
        }