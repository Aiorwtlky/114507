# utils/server.py
"""
伺服器相關工具函數
統一管理所有與伺服器通訊的功能
"""
import requests
from config import SERVER_URL
from datetime import datetime
import json

class ServerAPI:
    """伺服器 API 工具類"""
    
    def __init__(self):
        self.base_url = SERVER_URL
        self.timeout = 10  # 請求超時時間
    
    def test_connection(self):
        """測試伺服器連線"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            return {
                "status": "success",
                "message": "伺服器連線正常",
                "server_url": self.base_url,
                "response_time": response.elapsed.total_seconds()
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "error",
                "message": "無法連接到伺服器",
                "server_url": self.base_url
            }
        except requests.exceptions.Timeout:
            return {
                "status": "error", 
                "message": "伺服器連線超時",
                "server_url": self.base_url
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"連線錯誤：{str(e)}",
                "server_url": self.base_url
            }
    
    def register_device(self, device_data):
        """向伺服器註冊車機"""
        try:
            response = requests.post(
                f"{self.base_url}/api/device/register",
                json=device_data,
                timeout=self.timeout
            )
            return response.json()
        except Exception as e:
            return {
                "status": "error",
                "message": f"註冊失敗：{str(e)}"
            }
    
    def sync_device_info(self, device_data):
        """同步車機資訊到伺服器"""
        try:
            response = requests.post(
                f"{self.base_url}/api/device/sync",
                json=device_data,
                timeout=self.timeout
            )
            return response.json()
        except Exception as e:
            return {
                "status": "error",
                "message": f"同步失敗：{str(e)}"
            }
    
    def upload_trip_data(self, trip_data):
        """上傳行程資料到伺服器"""
        try:
            response = requests.post(
                f"{self.base_url}/api/trip/upload",
                json=trip_data,
                timeout=self.timeout
            )
            return response.json()
        except Exception as e:
            return {
                "status": "error",
                "message": f"上傳失敗：{str(e)}"
            }

# 全域 API 實例
server_api = ServerAPI()

def get_server_url():
    """取得伺服器 URL - 統一入口"""
    return SERVER_URL

def get_server_status():
    """取得伺服器狀態 - 統一入口"""
    return server_api.test_connection()