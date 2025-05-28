"""
共用工具函式模組
提供日期格式化、檔案管理等功能
"""

import os
import time
from datetime import datetime

def get_current_timestamp():
    """
    取得目前時間戳記
    格式: YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def get_current_date():
    """
    取得目前日期
    格式: YYYY-MM-DD
    """
    return datetime.now().strftime("%Y-%m-%d")

def get_current_time():
    """
    取得目前時間
    格式: HH:MM:SS
    """
    return datetime.now().strftime("%H:%M:%S")

def ensure_directory_exists(directory_path):
    """
    確保目錄存在，如果不存在則建立
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"建立目錄: {directory_path}")

# 為了向後相容，提供別名
ensure_dir_exists = ensure_directory_exists

def get_file_size_mb(file_path):
    """
    取得檔案大小（MB）
    """
    if os.path.exists(file_path):
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    return 0

def cleanup_old_files(directory, days_old=7, file_extension=None):
    """
    清理舊檔案
    
    Args:
        directory: 目錄路徑
        days_old: 保留天數，預設7天
        file_extension: 檔案副檔名過濾，如 '.mp4', '.jpg'
    """
    if not os.path.exists(directory):
        return
    
    current_time = time.time()
    cutoff_time = current_time - (days_old * 24 * 60 * 60)
    
    deleted_count = 0
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        # 檢查檔案副檔名
        if file_extension and not filename.lower().endswith(file_extension.lower()):
            continue
            
        if os.path.isfile(file_path):
            file_time = os.path.getmtime(file_path)
            if file_time < cutoff_time:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"已刪除舊檔案: {filename}")
                except Exception as e:
                    print(f"刪除檔案失敗 {filename}: {e}")
    
    print(f"共清理了 {deleted_count} 個檔案")

def format_file_path(base_dir, filename_prefix, timestamp=None, file_extension=""):
    """
    格式化檔案路徑
    
    Args:
        base_dir: 基礎目錄
        filename_prefix: 檔案名稱前綴
        timestamp: 時間戳記，如果為None則使用當前時間
        file_extension: 檔案副檔名（包含.）
    
    Returns:
        完整的檔案路徑
    """
    if timestamp is None:
        timestamp = get_current_timestamp()
    
    ensure_directory_exists(base_dir)
    filename = f"{filename_prefix}_{timestamp}{file_extension}"
    return os.path.join(base_dir, filename)