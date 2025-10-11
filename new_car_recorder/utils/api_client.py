# utils/api_client.py
import json
import datetime

class ApiClient:
    def __init__(self, base_url="http://127.0.0.1:8000/api", mock_mode=True):
        """
        初始化 API 客戶端。
        :param base_url: 後端伺服器的基礎 URL。
        :param mock_mode: 是否啟用模擬模式。若為 True，則不發送實際請求，只在 console 印出資訊。
        """
        self.base_url = base_url
        self.mock_mode = mock_mode
        self.trip_id = None
        print(f"ApiClient initialized. Mock mode: {'ON' if self.mock_mode else 'OFF'}")

    def start_trip(self, user_id, vehicle_id):
        """模擬開始一趟新的行程"""
        self.trip_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S") # 模擬一個行程 ID
        log_message = f"[API MOCK] >>> Called start_trip | User: {user_id}, Vehicle: {vehicle_id}, TripID: {self.trip_id}"
        print(log_message)
        
        if not self.mock_mode:
            # TODO: 在此處加入實際的 requests.post 請求
            pass
        return True

    def send_event(self, event_data):
        """
        發送偵測到的駕駛事件。
        :param event_data: 包含事件資訊的字典。
        """
        log_message = f"[API MOCK] >>> Sending Event | TripID: {self.trip_id}, Data: {json.dumps(event_data)}"
        print(log_message)

        if not self.mock_mode:
            # TODO: 在此處加入實際的 requests.post 請求
            pass
        return True
        
    def end_trip(self):
        """模擬結束當前行程"""
        log_message = f"[API MOCK] >>> Called end_trip | TripID: {self.trip_id}"
        print(log_message)
        self.trip_id = None

        if not self.mock_mode:
            # TODO: 在此處加入實際的 requests.post 請求
            pass
        return True