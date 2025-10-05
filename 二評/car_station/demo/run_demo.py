# demo/run_demo.py
"""
Demo 模式啟動腳本
整合所有模擬器
"""

import sys
sys.path.append('..')

from flask import Flask
from demo.mock_gpio import get_mock_gpio
from demo.mock_gps import MockGPS
from config import DEMO_GPS_ROUTE
from app import create_app

def run_demo():
    """啟動 Demo 模式"""
    print("=" * 50)
    print("🚗 MDG 車機系統 - DEMO 模式")
    print("=" * 50)
    
    # 啟動模擬器
    mock_gpio = get_mock_gpio()
    mock_gpio.start()
    
    mock_gps = MockGPS(DEMO_GPS_ROUTE)
    mock_gps.start()
    
    # 啟動 Flask
    app = create_app()
    
    try:
        print("\n🌐 Web 介面: http://localhost:5003")
        print("按 Ctrl+C 停止\n")
        app.run(debug=True, host='0.0.0.0', port=5003)
    except KeyboardInterrupt:
        print("\n\n正在停止...")
        mock_gpio.stop()
        mock_gps.stop()
        print("已停止")

if __name__ == '__main__':
    run_demo()