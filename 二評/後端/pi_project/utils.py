import numpy as np
import cv2
import time
import logging
import os
import json
import threading
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
from queue import Queue
import psutil

def setup_logging(log_level: str = 'INFO', log_dir: str = 'data/logs') -> logging.Logger:
    """設定日誌系統"""
    os.makedirs(log_dir, exist_ok=True)
    
    # 建立日誌格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    
    # 主系統日誌
    logger = logging.getLogger('pi_project')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 避免重複處理器
    if not logger.handlers:
        # 檔案處理器
        file_handler = logging.FileHandler(os.path.join(log_dir, 'system.log'), encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

def calculate_ear(eye_landmarks: np.ndarray) -> float:
    """
    計算 Eye Aspect Ratio (EAR)
    
    Args:
        eye_landmarks: 眼部關鍵點座標陣列 (6個點)
        
    Returns:
        float: EAR 值
    """
    try:
        if len(eye_landmarks) < 6:
            return 0.25  # 預設值
        
        # 計算垂直距離 (兩對點)
        A = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])  # 上眼瞼到下眼瞼
        B = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])  # 第二對垂直點
        
        # 計算水平距離 (眼角距離)
        C = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])  # 左眼角到右眼角
        
        if C == 0:
            return 0.25
        
        # 計算 EAR
        ear = (A + B) / (2.0 * C)
        
        # 異常值檢測和修正
        if ear > 1.0 or ear < 0.05:
            return 0.25  # 返回合理預設值
        
        return ear
        
    except (ZeroDivisionError, IndexError, TypeError) as e:
        return 0.25  # 計算失敗時返回預設值

def calculate_ear_robust(eye_landmarks: np.ndarray) -> float:
    """
    強健的 EAR 計算，使用多個參考點
    
    Args:
        eye_landmarks: 眼部關鍵點座標陣列
        
    Returns:
        float: 強健的 EAR 值
    """
    try:
        if len(eye_landmarks) < 6:
            return 0.25
        
        # 計算多個垂直距離
        vertical_distances = []
        
        # 使用不同的點對計算垂直距離
        point_pairs = [(1, 5), (2, 4)]
        for i, j in point_pairs:
            if i < len(eye_landmarks) and j < len(eye_landmarks):
                dist = np.linalg.norm(eye_landmarks[i] - eye_landmarks[j])
                vertical_distances.append(dist)
        
        if not vertical_distances:
            return 0.25
        
        # 使用中位數減少異常值影響
        avg_vertical = np.median(vertical_distances)
        
        # 水平距離
        horizontal_dist = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        
        if horizontal_dist == 0:
            return 0.25
        
        ear = avg_vertical / horizontal_dist
        
        # 範圍檢查
        return max(0.05, min(1.0, ear))
        
    except Exception:
        return 0.25

def rotation_matrix_to_euler_angles(R: np.ndarray) -> np.ndarray:
    """
    將旋轉矩陣轉換為歐拉角
    
    Args:
        R: 3x3 旋轉矩陣
        
    Returns:
        np.ndarray: [pitch, yaw, roll] 角度 (度)
    """
    try:
        sy = np.sqrt(R[0,0] * R[0,0] + R[1,0] * R[1,0])
        singular = sy < 1e-6
        
        if not singular:
            x = np.arctan2(R[2,1], R[2,2])  # pitch
            y = np.arctan2(-R[2,0], sy)     # yaw
            z = np.arctan2(R[1,0], R[0,0])  # roll
        else:
            x = np.arctan2(-R[1,2], R[1,1])
            y = np.arctan2(-R[2,0], sy)
            z = 0
        
        return np.array([x, y, z]) * 180.0 / np.pi
        
    except Exception:
        return np.array([0.0, 0.0, 0.0])

def generate_video_filename(camera_type: str = 'external', timestamp: Optional[datetime] = None) -> str:
    """
    生成影片檔案名稱
    
    Args:
        camera_type: 攝影機類型 ('internal' 或 'external')
        timestamp: 指定時間戳記，None 則使用當前時間
        
    Returns:
        str: 檔案名稱
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    timestamp_str = timestamp.strftime('%Y%m%d_%H%M%S')
    return f"{camera_type}_{timestamp_str}.mp4"

def ensure_directory_exists(directory: str) -> bool:
    """
    確保目錄存在
    
    Args:
        directory: 目錄路徑
        
    Returns:
        bool: 成功建立或已存在
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        print(f"建立目錄失敗 {directory}: {e}")
        return False

def get_system_info() -> Dict[str, Any]:
    """獲取系統資訊"""
    try:
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'boot_time': psutil.boot_time(),
            'timestamp': datetime.now().isoformat(),
            'process_count': len(psutil.pids())
        }
    except Exception:
        return {
            'cpu_percent': 0,
            'memory_percent': 0,
            'disk_usage': 0,
            'timestamp': datetime.now().isoformat(),
            'error': 'Unable to get system info'
        }

def cleanup_old_files(directory: str, max_files: int = 10, file_pattern: str = "*.mp4") -> int:
    """
    清理舊檔案
    
    Args:
        directory: 目錄路徑
        max_files: 最多保留的檔案數量
        file_pattern: 檔案模式 (如 "*.mp4")
        
    Returns:
        int: 刪除的檔案數量
    """
    try:
        if not os.path.exists(directory):
            return 0
        
        import glob
        pattern = os.path.join(directory, file_pattern)
        files = glob.glob(pattern)
        
        if not files:
            return 0
        
        # 按修改時間排序 (舊的在前)
        files.sort(key=lambda x: os.path.getmtime(x))
        
        # 刪除超過限制的舊檔案
        deleted_count = 0
        if len(files) > max_files:
            files_to_delete = files[:-max_files]
            for filepath in files_to_delete:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                    print(f"🗑️  已刪除舊檔案: {os.path.basename(filepath)}")
                except Exception as e:
                    print(f"❌ 刪除檔案失敗 {filepath}: {e}")
        
        return deleted_count
        
    except Exception as e:
        print(f"清理檔案時發生錯誤: {e}")
        return 0

def format_duration(seconds: float) -> str:
    """格式化時間長度"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{int(minutes)}分{remaining_seconds:.0f}秒"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{int(hours)}小時{int(remaining_minutes)}分"

def format_file_size(bytes_size: int) -> str:
    """格式化檔案大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def save_json_file(data: Dict[str, Any], filepath: str, backup: bool = True) -> bool:
    """
    安全地儲存 JSON 檔案
    
    Args:
        data: 要儲存的資料
        filepath: 檔案路徑
        backup: 是否備份原檔案
        
    Returns:
        bool: 是否成功
    """
    try:
        # 確保目錄存在
        directory = os.path.dirname(filepath)
        if directory:
            ensure_directory_exists(directory)
        
        # 備份原檔案
        if backup and os.path.exists(filepath):
            backup_path = f"{filepath}.backup"
            try:
                import shutil
                shutil.copy2(filepath, backup_path)
            except Exception:
                pass  # 備份失敗不影響主要操作
        
        # 寫入新檔案
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
        
    except Exception as e:
        print(f"儲存 JSON 檔案失敗 {filepath}: {e}")
        return False

def load_json_file(filepath: str, default: Any = None) -> Any:
    """
    載入 JSON 檔案
    
    Args:
        filepath: 檔案路徑
        default: 檔案不存在或錯誤時的預設值
        
    Returns:
        載入的資料或預設值
    """
    try:
        if not os.path.exists(filepath):
            return default
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    except Exception as e:
        print(f"載入 JSON 檔案失敗 {filepath}: {e}")
        return default

class PerformanceMonitor:
    """效能監控器"""
    
    def __init__(self, name: str = "default"):
        self.name = name
        self.start_time = time.time()
        self.frame_count = 0
        self.processing_times = []
        self.frame_start_time = None
        self._lock = threading.Lock()
    
    def start_frame(self):
        """開始處理幀"""
        self.frame_start_time = time.time()
    
    def end_frame(self):
        """結束處理幀"""
        if self.frame_start_time is not None:
            with self._lock:
                processing_time = time.time() - self.frame_start_time
                self.processing_times.append(processing_time)
                self.frame_count += 1
                
                # 保持最近 100 筆記錄
                if len(self.processing_times) > 100:
                    self.processing_times.pop(0)
                
                self.frame_start_time = None
    
    def get_fps(self) -> float:
        """獲取 FPS"""
        with self._lock:
            if len(self.processing_times) < 2:
                return 0.0
            
            avg_processing_time = sum(self.processing_times) / len(self.processing_times)
            return 1.0 / avg_processing_time if avg_processing_time > 0 else 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計資料"""
        with self._lock:
            if not self.processing_times:
                return {
                    'name': self.name,
                    'fps': 0.0,
                    'total_frames': self.frame_count,
                    'uptime': time.time() - self.start_time
                }
            
            return {
                'name': self.name,
                'fps': self.get_fps(),
                'avg_processing_time': sum(self.processing_times) / len(self.processing_times),
                'max_processing_time': max(self.processing_times),
                'min_processing_time': min(self.processing_times),
                'total_frames': self.frame_count,
                'uptime': time.time() - self.start_time,
                'samples': len(self.processing_times)
            }

class ThreadSafeQueue:
    """執行緒安全的佇列包裝器"""
    
    def __init__(self, maxsize: int = 0):
        self.queue = Queue(maxsize)
        self.stats = {
            'put_count': 0,
            'get_count': 0,
            'error_count': 0
        }
        self._lock = threading.Lock()
    
    def put(self, item: Any, timeout: Optional[float] = None) -> bool:
        """放入項目"""
        try:
            self.queue.put(item, timeout=timeout)
            with self._lock:
                self.stats['put_count'] += 1
            return True
        except Exception:
            with self._lock:
                self.stats['error_count'] += 1
            return False
    
    def get(self, timeout: Optional[float] = None) -> Any:
        """取出項目"""
        try:
            item = self.queue.get(timeout=timeout)
            with self._lock:
                self.stats['get_count'] += 1
            return item
        except Exception:
            with self._lock:
                self.stats['error_count'] += 1
            raise
    
    def qsize(self) -> int:
        """佇列大小"""
        return self.queue.qsize()
    
    def empty(self) -> bool:
        """是否為空"""
        return self.queue.empty()
    
    def get_stats(self) -> Dict[str, int]:
        """獲取統計資料"""
        with self._lock:
            return self.stats.copy()

# 全域效能監控器
performance_monitors = {}

def get_performance_monitor(name: str) -> PerformanceMonitor:
    """獲取或建立效能監控器"""
    if name not in performance_monitors:
        performance_monitors[name] = PerformanceMonitor(name)
    return performance_monitors[name]

def get_all_performance_stats() -> Dict[str, Dict[str, Any]]:
    """獲取所有效能統計"""
    return {name: monitor.get_stats() for name, monitor in performance_monitors.items()}

# 導出常用函式
__all__ = [
    'setup_logging', 'calculate_ear', 'calculate_ear_robust',
    'rotation_matrix_to_euler_angles', 'generate_video_filename',
    'ensure_directory_exists', 'get_system_info', 'cleanup_old_files',
    'format_duration', 'format_file_size', 'save_json_file', 'load_json_file',
    'PerformanceMonitor', 'ThreadSafeQueue', 'get_performance_monitor',
    'get_all_performance_stats'
]