# utils/uploader.py
import requests
from typing import List, Dict, Tuple

class ServerUploader:
    """伺服器上傳管理器（簡化版）"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "http://your-server-url.com"  # 替換為實際伺服器
        self.headers = {
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json'
        }
    
    def bulk_upload_events(self, trip_id: int, events: List[Dict]) -> Tuple[bool, str]:
        """批次上傳事件"""
        if not events:
            return True, None
        
        url = f"{self.base_url}/api/trips/{trip_id}/events/bulk/"
        try:
            response = requests.post(url, headers=self.headers, json={'events': events}, timeout=30)
            if response.status_code in [200, 201]:
                return True, None
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)

class UploadManager:
    """上傳任務管理器"""
    
    def __init__(self, token: str):
        self.uploader = ServerUploader(token)