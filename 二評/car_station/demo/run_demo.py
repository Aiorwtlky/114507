# demo/run_demo.py（修正版）
"""
Demo 模式啟動腳本
"""

import sys
import os

# 將專案根目錄加入 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from demo.mock_gpio import get_mock_gpio
from app import create_app

def run_demo():
    """啟動 Demo 模式"""
    print("=" * 50)
    print("MDG 車機系統 - DEMO 模式（無 GPS）")
    print("=" * 50)
    
    # 啟動 GPIO 模擬器
    mock_gpio = get_mock_gpio()
    mock_gpio.start()
    
    # 啟動 Flask
    app = create_app()
    
    try:
        print("\nWeb 介面: http://localhost:5003")
        print("按 Ctrl+C 停止\n")
        app.run(debug=True, host='0.0.0.0', port=5003, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n正在停止...")
        mock_gpio.stop()
        print("已停止")

if __name__ == '__main__':
    run_demo()