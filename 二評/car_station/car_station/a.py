import requests
import time

response = requests.post("http://localhost:5003/trip/api/start_trip")
print("開始行程:", response.json())
trip_id = response.json().get('trip_id')

print("等待 30 秒進行 AI 偵測...")
time.sleep(30)

response = requests.post("http://localhost:5003/trip/api/end_trip")
print("結束行程:", response.json())