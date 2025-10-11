# main.py (修改版)
"""
主程式入口
整合所有模組
"""

import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow

from database.local_db import LocalDatabase
from sync.api_client import APIClient
from sync.gcs_uploader import GCSUploader
from sync.sync_service import SyncService
from gpio_handler import GPIOHandler


def main():
    """主程式"""
    print("="*60)
    print("吾駕仙 - AI 駕駛行為分析系統")
    print("="*60)
    
    # 1. 初始化資料庫
    db = LocalDatabase()
    print("[Main] Database initialized")
    
    # 2. 初始化 API 客戶端
    api_client = APIClient()
    
    # TODO: 車機應該有一個固定的帳號來登入
    # 這裡先用測試帳號
    # api_client.login("car_device_001", "password123")
    
    # 3. 初始化 GCS 上傳器
    gcs_uploader = GCSUploader()
    
    # 測試 GCS 連線
    if gcs_uploader.check_connection():
        print("[Main] GCS connection successful ✅")
    else:
        print("[Main] GCS connection failed ❌")
    
    # 4. 初始化同步服務
    sync_service = SyncService(db, api_client, gcs_uploader)
    
    # 5. 初始化 GPIO 處理器
    gpio_handler = GPIOHandler(port="/dev/cu.usbmodem1401")
    
    # 6. 啟動 Qt 應用程式
    app = QApplication(sys.argv)
    window = MainWindow()
    window.set_gpio_handler(gpio_handler)
    
    # 7. 設定 NFC 回調函式
    def on_nfc_detected(nfc_uid: str):
        """當 NFC 被偵測到時"""
        print(f"[Main] NFC detected: {nfc_uid}")
        
        # 查詢使用者資訊（先查本地快取，再查 API）
        user_info = db.get_nfc_mapping(nfc_uid)
        
        if not user_info:
            # 從 API 查詢
            user_info = api_client.lookup_nfc(nfc_uid)
            if user_info:
                # 快取到本地
                from database.models import NFCMapping
                mapping = NFCMapping(
                    nfc_uid=nfc_uid,
                    user_id=user_info['user_id'],
                    username=user_info.get('username'),
                    first_name=user_info.get('first_name'),
                    last_name=user_info.get('last_name'),
                    groups=user_info.get('groups')
                )
                db.cache_nfc_mapping(mapping)
        
        if user_info:
            # 判斷是開始還是結束行程
            if window.worker.trip_manager.current_trip:
                # 如果已有行程，則結束
                window.worker.end_trip()
            else:
                # 否則開始新行程
                window.worker.start_trip(nfc_uid, user_info)
        else:
            print(f"[Main] ERROR: User not found for NFC: {nfc_uid}")
            window.worker.update_event_log.emit(f"❌ 未知的 NFC 卡片: {nfc_uid}")
    
    gpio_handler.on_nfc_detected = on_nfc_detected
    
    # 8. 啟動服務
    gpio_handler.start()
    sync_service.start()
    
    # 9. 顯示視窗
    window.show()
    
    # 10. 測試用：模擬刷卡（5 秒後）
    from PySide6.QtCore import QTimer
    def simulate_card_scan():
        print("\n[Main] 🧪 SIMULATING NFC SCAN...")
        gpio_handler.simulate_nfc_scan("TEST:AA:BB:CC:DD")
    
    # 延遲 5 秒模擬刷卡（可以註解掉）
    # QTimer.singleShot(5000, simulate_card_scan)
    
    # 11. 執行應用程式
    exit_code = app.exec()
    
    # 12. 清理
    gpio_handler.stop()
    sync_service.stop()
    db.close()
    
    print("[Main] Application exited")
    sys.exit(exit_code)


if __name__ == '__main__':
    main()