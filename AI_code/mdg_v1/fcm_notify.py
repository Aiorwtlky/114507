# fcm_notify.py

import firebase_admin
from firebase_admin import credentials, messaging

# 初始化 Firebase App（只做一次）
cred = credentials.Certificate("config/firebase_key.json")
firebase_admin.initialize_app(cred)

# 測試裝置 token（請替換為實際 token）
test_token = "在這裡貼上你的 FCM token"

# 發送通知訊息
def send_fcm(title, body):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token=test_token
    )

    try:
        response = messaging.send(message)
        print("推播成功：", response)
    except Exception as e:
        print("推播失敗：", e)

# 測試呼叫
if __name__ == "__main__":
    send_fcm("內輪差偵測警告", "在 right_cam 偵測到 person")
