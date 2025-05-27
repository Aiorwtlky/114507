import os
import time
import requests

class SyncManager:
    def __init__(self, cache_dir='./events/', server_api_url='http://localhost:5000/api/events/upload'):
        self.cache_dir = cache_dir
        self.server_api_url = server_api_url

    def list_cached_events(self):
        # 假設事件資料存在 cache_dir 內特定格式資料夾或檔案
        # 回傳待上傳的事件檔案列表（可擴充JSON、影像、影片）
        files = []
        for root, dirs, filenames in os.walk(self.cache_dir):
            for file in filenames:
                if file.endswith(('.jpg', '.mp4', '.json')):
                    files.append(os.path.join(root, file))
        return files

    def upload_file(self, filepath):
        try:
            with open(filepath, 'rb') as f:
                files = {'file': (os.path.basename(filepath), f)}
                response = requests.post(self.server_api_url, files=files)
            if response.status_code == 200:
                return True
            else:
                print(f"上傳失敗：{filepath} 狀態碼 {response.status_code}")
                return False
        except Exception as e:
            print(f"上傳例外：{filepath} {e}")
            return False

    def sync(self):
        files = self.list_cached_events()
        for file in files:
            success = self.upload_file(file)
            if success:
                print(f"已成功上傳: {file}")
                # 可在此刪除或標記檔案為已同步
                # os.remove(file)
            else:
                print(f"未能上傳: {file}")

    def run_periodic_sync(self, interval_sec=300):
        while True:
            self.sync()
            time.sleep(interval_sec)
