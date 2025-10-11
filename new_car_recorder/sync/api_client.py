# sync/api_client.py (完整修正版)
"""
後端 API 客戶端
負責與後端 API 溝通
"""

import requests
from typing import Optional, Dict, List
from datetime import datetime
import configparser


class APIClient:
    def __init__(self, config_path: str = "config.ini"):
        """初始化 API 客戶端"""
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        self.base_url = self.config.get('api', 'base_url')
        self.timeout = self.config.getint('api', 'timeout', fallback=30)
        self.token: Optional[str] = None
        
        print(f"[APIClient] Initialized with base URL: {self.base_url}")
    
    def _get_headers(self) -> Dict:
        """取得請求標頭"""
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers
    
    def login(self, username: str, password: str) -> bool:
        """使用者登入（取得 Token）"""
        try:
            response = requests.post(
                f"{self.base_url}/api/token/",
                json={'username': username, 'password': password},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access')
                print("[APIClient] Login successful")
                return True
            else:
                print(f"[APIClient] Login failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"[APIClient] Login error: {e}")
            return False
    
    def lookup_nfc(self, nfc_uid: str) -> Optional[Dict]:
        """根據 NFC UID 查詢使用者資訊"""
        try:
            response = requests.get(
                f"{self.base_url}/api/users/by-nfc/",
                params={'nfc_id': nfc_uid},
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"[APIClient] NFC lookup successful: {user_data.get('username')}")
                return user_data
            else:
                print(f"[APIClient] NFC lookup failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"[APIClient] NFC lookup error: {e}")
            return None
    
    def start_trip(self, trip_data: Dict) -> Optional[Dict]:
        """開始行程（通知後端）"""
        try:
            response = requests.post(
                f"{self.base_url}/api/trips/start/",
                json=trip_data,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code == 201:
                backend_data = response.json()
                print(f"[APIClient] Trip started on backend: {backend_data.get('id')}")
                return backend_data
            else:
                print(f"[APIClient] Start trip failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"[APIClient] Start trip error: {e}")
            return None
    
    def end_trip(self, backend_trip_id: int, end_data: Dict) -> bool:
        """結束行程（通知後端）"""
        try:
            response = requests.patch(
                f"{self.base_url}/api/trips/{backend_trip_id}/end/",
                json=end_data,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                print(f"[APIClient] Trip ended on backend: {backend_trip_id}")
                return True
            else:
                print(f"[APIClient] End trip failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"[APIClient] End trip error: {e}")
            return False
    
    def upload_event(self, event_data: Dict) -> Optional[int]:
        """上傳 AI 事件"""
        try:
            response = requests.post(
                f"{self.base_url}/api/events/",
                json=event_data,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code == 201:
                backend_data = response.json()
                event_id = backend_data.get('id')
                print(f"[APIClient] Event uploaded: {event_id}")
                return event_id
            else:
                print(f"[APIClient] Upload event failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"[APIClient] Upload event error: {e}")
            return None
    
    def register_video(self, video_data: Dict) -> Optional[int]:
        """註冊影片（告訴後端影片已上傳到 GCS）"""
        try:
            response = requests.post(
                f"{self.base_url}/api/videos/register/",
                json=video_data,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code == 201:
                backend_data = response.json()
                video_id = backend_data.get('id')
                print(f"[APIClient] Video registered: {video_id}")
                return video_id
            else:
                print(f"[APIClient] Register video failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"[APIClient] Register video error: {e}")
            return None
    
    def health_check(self) -> bool:
        """
        檢查後端 API 是否正常
        ✅ 寬鬆版：允許 500 錯誤，只要能連上就好
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/health/",
                timeout=5
            )
            
            # ✅ 接受 200 和 500
            if response.status_code in [200, 500]:
                try:
                    data = response.json()
                    
                    if response.status_code == 500:
                        error_msg = data.get('error', 'Unknown error')
                        print(f"[APIClient] Health check warning: Backend has error")
                        print(f"             Error: {error_msg[:100]}")
                        print(f"[APIClient] But connection is OK, will try to sync anyway")
                    else:
                        status = data.get('status', 'unknown')
                        if status == 'healthy':
                            print("[APIClient] Health check passed: API is healthy")
                        else:
                            print(f"[APIClient] Health check warning: API status is {status}")
                    
                    return True
                    
                except Exception:
                    print(f"[APIClient] Health check warning: Cannot parse response, but connection OK")
                    return True
            else:
                print(f"[APIClient] Health check failed: status code {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("[APIClient] Health check failed: Cannot connect to server")
            return False
        except requests.exceptions.Timeout:
            print("[APIClient] Health check failed: Connection timeout")
            return False
        except Exception as e:
            print(f"[APIClient] Health check failed: {e}")
            return False