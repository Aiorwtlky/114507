# test_system.py
"""
系統測試腳本
用於測試各個模組是否正常運作
"""

from database.local_db import LocalDatabase
from database.models import NFCMapping
from sync.api_client import APIClient
from sync.gcs_uploader import GCSUploader
from core.trip_manager import TripManager
from datetime import datetime


def test_database():
    """測試資料庫"""
    print("\n=== Testing Database ===")
    db = LocalDatabase("test.db")
    
    # 測試快取 NFC
    mapping = NFCMapping(
        nfc_uid="TEST:11:22:33",
        user_id=123,
        username="test_user",
        groups=[{'group_id': 1, 'group_name': 'Test Group'}]
    )
    db.cache_nfc_mapping(mapping)
    
    # 讀取
    result = db.get_nfc_mapping("TEST:11:22:33")
    print(f"NFC Mapping: {result}")
    
    db.close()
    print("✅ Database test passed")


def test_api_client():
    """測試 API 客戶端"""
    print("\n=== Testing API Client ===")
    api = APIClient()
    
    # 測試健康檢查
    if api.health_check():
        print("✅ API health check passed")
    else:
        print("❌ API health check failed")


def test_gcs_uploader():
    """測試 GCS 上傳器"""
    print("\n=== Testing GCS Uploader ===")
    gcs = GCSUploader()
    
    # 測試連線
    if gcs.check_connection():
        print("✅ GCS connection test passed")
    else:
        print("❌ GCS connection test failed")


def test_trip_manager():
    """測試行程管理器"""
    print("\n=== Testing Trip Manager ===")
    db = LocalDatabase("test.db")
    trip_mgr = TripManager(db)
    
    # 模擬開始行程
    user_info = {
        'user_id': 123,
        'username': 'test_user',
        'groups': [{'group_id': 1, 'group_name': 'Test Group'}]
    }
    
    trip_id = trip_mgr.start_trip("TEST:11:22:33", user_info)
    print(f"Trip started: {trip_id}")
    
    # 模擬新增事件
    trip_mgr.add_event("A01: 重度疲勞", "inner", 0.95)
    trip_mgr.add_event("B03: 未保持適當車距", "outer", 0.88)
    
    # 取得行程資訊
    info = trip_mgr.get_current_trip_info()
    print(f"Trip info: {info}")
    
    # 結束行程
    import time
    time.sleep(2)  # 等待 2 秒
    result = trip_mgr.end_trip(total_mileage=5.5)
    print(f"Trip ended: Score={result['score']:.2f}")
    
    db.close()
    print("✅ Trip manager test passed")


def main():
    """執行所有測試"""
    print("="*60)
    print("系統測試")
    print("="*60)
    
    test_database()
    test_api_client()
    test_gcs_uploader()
    test_trip_manager()
    
    print("\n" + "="*60)
    print("測試完成")
    print("="*60)


if __name__ == '__main__':
    main()