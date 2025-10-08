# demo/run_demo.py（完整版）
import os
os.environ['OPENCV_AVFOUNDATION_SKIP_AUTH'] = '1' # MacOS 特定設定，避免攝影機權限問題

import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from demo.mock_gpio import get_mock_gpio
from app import create_app
import time
import threading

def auto_start_trip(app):
    """自動啟動測試行程"""
    time.sleep(3)  # 等待 Flask 啟動
    
    with app.app_context():
        from models import db, Trip, Personnel
        from services.detection_service import DetectionService
        
        # 檢查是否有測試人員
        personnel = Personnel.query.first()
        if not personnel:
            print("⚠️ 找不到測試人員，請先執行主程式建立")
            return
        
        # 檢查是否已有進行中的行程
        active_trip = Trip.query.filter_by(status='進行中').first()
        
        if not active_trip:
            # 建立測試行程
            trip = Trip.create_new_trip(
                personnel_id=personnel.id,
                trip_name="Demo 測試行程"
            )
            trip.status = '進行中'
            trip.start_time = datetime.now()
            db.session.commit()
            
            print(f"\n✅ 已自動建立測試行程: {trip.trip_number}")
            active_trip = trip
        
        # 啟動 AI 服務
        print(f"\n🤖 啟動 AI 偵測服務...")
        success = DetectionService.start_trip_detection(active_trip.id)
        
        if success:
            print(f"✅ AI 服務已啟動 (Trip ID: {active_trip.id})")
            print(f"🎥 內鏡頭: 筆電攝影機")
            print(f"🎥 外鏡頭: demo/test_videos/test_outsideCamera.mov")
            print(f"\n📍 監控頁面: http://localhost:5003/trip/monitor/{active_trip.id}")
        else:
            print(f"❌ AI 服務啟動失敗")

def run_demo():
    """啟動 Demo 模式"""
    print("=" * 50)
    print("MDG 車機系統 - DEMO 模式（含 AI 自動啟動）")
    print("=" * 50)
    
    # 啟動 GPIO 模擬器
    mock_gpio = get_mock_gpio()
    mock_gpio.start()
    
    # 建立 Flask app
    app = create_app()
    
    # 在背景執行緒自動啟動行程
    threading.Thread(target=auto_start_trip, args=(app,), daemon=True).start()
    
    try:
        print("\n🌐 Web 介面: http://localhost:5003")
        print("⌨️  鍵盤控制: W/X=車速, A/D=方向燈")
        print("按 Ctrl+C 停止\n")
        app.run(debug=False, host='0.0.0.0', port=5003, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n正在停止...")
        mock_gpio.stop()
        print("已停止")

if __name__ == '__main__':
    from datetime import datetime
    run_demo()