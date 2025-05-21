# firebase_helper.py

import firebase_admin
from firebase_admin import credentials, firestore

# 初始化 Firebase（僅執行一次）
cred = credentials.Certificate("config/firebase_key.json")
firebase_admin.initialize_app(cred)

# 建立 Firestore 客戶端
db = firestore.client()

def upload_event_metadata(event_data: dict):
    """
    將事件資料上傳至 Firestore 的 'events' 集合
    event_data: 包含 timestamp、event_type、image_path 等欄位
    """
    db.collection("events").add(event_data)
    print("事件已上傳至 Firestore")
