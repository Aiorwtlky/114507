# core/storage_manager.py
"""
檔案儲存管理
負責管理影片檔案的儲存、清理等工作
"""

import os
import shutil
from pathlib import Path
from typing import List, Tuple
from datetime import datetime, timedelta


class StorageManager:
    def __init__(self, base_path: str = "upload_queue_videos"):
        """
        初始化儲存管理器
        
        Args:
            base_path: 影片儲存的根目錄
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        print(f"[StorageManager] Initialized with base path: {self.base_path}")
    
    def get_video_path(self, trip_number: str, timestamp: datetime, camera_type: str = "outer") -> Path:
        """
        生成影片檔案路徑
        
        Args:
            trip_number: 行程編號
            timestamp: 時間戳記
            camera_type: 鏡頭類型 ('inner' or 'outer')
        
        Returns:
            完整的影片檔案路徑
        """
        # 按日期分資料夾: YYYY-MM-DD/
        date_folder = self.base_path / timestamp.strftime("%Y-%m-%d")
        date_folder.mkdir(parents=True, exist_ok=True)
        
        # 檔名格式: TRIP_20250411_120000_outer.mp4
        filename = f"{trip_number}_{timestamp.strftime('%Y%m%d_%H%M%S')}_{camera_type}.mp4"
        
        return date_folder / filename
    
    def get_disk_usage(self) -> Tuple[int, int, float]:
        """
        取得磁碟使用情況
        
        Returns:
            (total_bytes, used_bytes, usage_percent)
        """
        total, used, free = shutil.disk_usage(self.base_path)
        usage_percent = (used / total) * 100
        return total, used, usage_percent
    
    def cleanup_old_videos(self, days: int = 7, force: bool = False) -> List[Path]:
        """
        清理舊影片檔案
        
        Args:
            days: 保留最近幾天的影片
            force: 是否強制刪除（即使未同步）
        
        Returns:
            被刪除的檔案列表
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_files = []
        
        for video_file in self.base_path.rglob("*.mp4"):
            # 取得檔案的修改時間
            file_mtime = datetime.fromtimestamp(video_file.stat().st_mtime)
            
            if file_mtime < cutoff_date:
                # TODO: 如果 force=False，應該檢查資料庫中該影片是否已同步
                # 這裡先簡化為直接刪除
                try:
                    video_file.unlink()
                    deleted_files.append(video_file)
                    print(f"[StorageManager] Deleted old video: {video_file.name}")
                except Exception as e:
                    print(f"[StorageManager] Failed to delete {video_file.name}: {e}")
        
        return deleted_files
    
    def cleanup_empty_folders(self):
        """刪除空的日期資料夾"""
        for folder in self.base_path.iterdir():
            if folder.is_dir() and not any(folder.iterdir()):
                folder.rmdir()
                print(f"[StorageManager] Deleted empty folder: {folder.name}")
    
    def get_total_video_size(self) -> int:
        """計算所有影片的總大小（bytes）"""
        total_size = 0
        for video_file in self.base_path.rglob("*.mp4"):
            total_size += video_file.stat().st_size
        return total_size
    
    def check_disk_space(self, required_mb: int = 1000) -> bool:
        """
        檢查磁碟空間是否足夠
        
        Args:
            required_mb: 需要的空間（MB）
        
        Returns:
            True 如果空間足夠
        """
        total, used, free = shutil.disk_usage(self.base_path)
        free_mb = free / (1024 * 1024)
        
        if free_mb < required_mb:
            print(f"[StorageManager] WARNING: Low disk space! Free: {free_mb:.1f}MB")
            return False
        return True
    
    def get_video_info(self, video_path: Path) -> dict:
        """
        取得影片檔案資訊
        
        Returns:
            包含檔案大小、修改時間等資訊的字典
        """
        if not video_path.exists():
            return {}
        
        stat = video_path.stat()
        return {
            'path': str(video_path),
            'size': stat.st_size,
            'size_mb': stat.st_size / (1024 * 1024),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'exists': True
        }