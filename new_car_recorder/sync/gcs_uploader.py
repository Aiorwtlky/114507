# sync/gcs_uploader.py
"""
Google Cloud Storage 上傳模組
負責將影片上傳至 GCS
"""

import os
from pathlib import Path
from typing import Optional, Callable
from google.cloud import storage
from google.oauth2 import service_account
import configparser


class GCSUploader:
    def __init__(self, config_path: str = "config.ini"):
        """
        初始化 GCS 上傳器
        
        Args:
            config_path: 設定檔路徑
        """
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        # 讀取 GCS 設定
        self.bucket_name = self.config.get('gcs', 'bucket_name')
        self.credentials_path = self.config.get('gcs', 'credentials_path')
        self.video_folder = self.config.get('gcs', 'video_folder', fallback='videos')
        self.chunk_size = self.config.getint('gcs', 'upload_chunk_size', fallback=5242880)  # 5MB
        
        # 初始化 GCS 客戶端
        self.client = None
        self.bucket = None
        self._init_client()
    
    def _init_client(self):
        """初始化 GCS 客戶端"""
        try:
            # 檢查憑證檔案是否存在
            if not Path(self.credentials_path).exists():
                print(f"[GCSUploader] ERROR: Credentials file not found: {self.credentials_path}")
                return
            
            # 設定環境變數
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path
            
            # 建立客戶端
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path
            )
            self.client = storage.Client(credentials=credentials, project=credentials.project_id)
            self.bucket = self.client.bucket(self.bucket_name)
            
            print(f"[GCSUploader] Initialized successfully")
            print(f"  - Bucket: {self.bucket_name}")
            print(f"  - Video Folder: {self.video_folder}")
            
        except Exception as e:
            print(f"[GCSUploader] ERROR: Failed to initialize: {e}")
            self.client = None
            self.bucket = None
    
    def upload_video(
        self, 
        local_path: Path, 
        remote_filename: Optional[str] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Optional[str]:
        """
        上傳影片到 GCS
        
        Args:
            local_path: 本地影片路徑
            remote_filename: GCS 上的檔案名稱（不含資料夾路徑）
            progress_callback: 進度回調函式，參數為 0-100 的百分比
        
        Returns:
            GCS 公開 URL，失敗則返回 None
        """
        if not self.client or not self.bucket:
            print("[GCSUploader] ERROR: Client not initialized")
            return None
        
        if not local_path.exists():
            print(f"[GCSUploader] ERROR: File not found: {local_path}")
            return None
        
        try:
            # 生成遠端檔案路徑
            if not remote_filename:
                remote_filename = local_path.name
            
            # 完整的 GCS 路徑: videos/YYYY-MM-DD/filename.mp4
            date_folder = local_path.parent.name  # 例如 "2025-10-11"
            blob_name = f"{self.video_folder}/{date_folder}/{remote_filename}"
            
            # 建立 Blob
            blob = self.bucket.blob(blob_name)
            
            # 設定 chunk size（用於大檔案）
            blob.chunk_size = self.chunk_size
            
            print(f"[GCSUploader] Uploading: {local_path.name}")
            print(f"  - Destination: gs://{self.bucket_name}/{blob_name}")
            
            # 上傳檔案
            file_size = local_path.stat().st_size
            
            # 使用 upload_from_filename 進行上傳
            blob.upload_from_filename(str(local_path))
            
            # 模擬進度回調（因為 upload_from_filename 不支援即時進度）
            if progress_callback:
                progress_callback(100.0)
            
            # 生成公開 URL
            public_url = f"https://storage.googleapis.com/{self.bucket_name}/{blob_name}"
            
            print(f"[GCSUploader] Upload successful!")
            print(f"  - URL: {public_url}")
            print(f"  - Size: {file_size / (1024*1024):.2f} MB")
            
            return public_url
            
        except Exception as e:
            print(f"[GCSUploader] ERROR: Upload failed: {e}")
            return None
    
    def upload_with_progress(
        self,
        local_path: Path,
        remote_filename: Optional[str] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Optional[str]:
        """
        上傳影片並即時回報進度（使用分段上傳）
        
        Args:
            local_path: 本地影片路徑
            remote_filename: GCS 上的檔案名稱
            progress_callback: 進度回調函式
        
        Returns:
            GCS 公開 URL
        """
        if not self.client or not self.bucket:
            return None
        
        if not local_path.exists():
            return None
        
        try:
            if not remote_filename:
                remote_filename = local_path.name
            
            date_folder = local_path.parent.name
            blob_name = f"{self.video_folder}/{date_folder}/{remote_filename}"
            blob = self.bucket.blob(blob_name)
            
            # 取得檔案大小
            file_size = local_path.stat().st_size
            uploaded = 0
            
            print(f"[GCSUploader] Uploading with progress: {local_path.name}")
            
            # 分段讀取並上傳
            with open(local_path, 'rb') as f:
                # 使用 resumable upload
                blob.upload_from_file(
                    f,
                    rewind=True,
                    size=file_size,
                    num_retries=3
                )
            
            # 完成後回報 100%
            if progress_callback:
                progress_callback(100.0)
            
            public_url = f"https://storage.googleapis.com/{self.bucket_name}/{blob_name}"
            print(f"[GCSUploader] Upload completed: {public_url}")
            
            return public_url
            
        except Exception as e:
            print(f"[GCSUploader] ERROR: Upload failed: {e}")
            return None
    
    def delete_video(self, blob_name: str) -> bool:
        """
        從 GCS 刪除影片
        
        Args:
            blob_name: GCS 上的 blob 名稱（完整路徑）
        
        Returns:
            True 如果刪除成功
        """
        if not self.client or not self.bucket:
            return False
        
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            print(f"[GCSUploader] Deleted: {blob_name}")
            return True
        except Exception as e:
            print(f"[GCSUploader] ERROR: Delete failed: {e}")
            return False
    
    def check_connection(self) -> bool:
        """
        測試 GCS 連線
        
        Returns:
            True 如果連線正常
        """
        if not self.client or not self.bucket:
            return False
        
        try:
            # 嘗試列出 bucket 內容（限制 1 筆）
            blobs = list(self.bucket.list_blobs(max_results=1))
            print("[GCSUploader] Connection test successful")
            return True
        except Exception as e:
            print(f"[GCSUploader] Connection test failed: {e}")
            return False