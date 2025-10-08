# demo/mock_gpio.py
"""
模擬 GPIO 輸入（使用鍵盤）
用於電腦開發測試
"""

import threading
from pynput import keyboard
from datetime import datetime

class MockGPIO:
    """模擬 GPIO 狀態"""
    
    def __init__(self):
        self.left_turn = False
        self.right_turn = False
        self.reverse = False
        self.speed = 0  # km/h
        
        self.listener = None
        print("\n🎮 GPIO 模擬鍵盤控制:")
        print("  A - 左轉燈")
        print("  D - 右轉燈")
        print("  S - 倒車")
        print("  W - 加速 (+10 km/h)")
        print("  X - 減速 (-10 km/h)")
        print("  Q - 全部關閉\n")
    
    def start(self):
        """啟動鍵盤監聽"""
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
        print("✅ GPIO 模擬器已啟動")
    
    def stop(self):
        """停止監聽"""
        if self.listener:
            self.listener.stop()
        print("🛑 GPIO 模擬器已停止")
    
    def _on_press(self, key):
        """按鍵按下"""
        try:
            if hasattr(key, 'char'):
                if key.char == 'a':
                    self.left_turn = True
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 左轉燈: ON")
                elif key.char == 'd':
                    self.right_turn = True
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 右轉燈: ON")
                elif key.char == 's':
                    self.reverse = True
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 倒車: ON")
                elif key.char == 'w':
                    self.speed = min(120, self.speed + 10)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 車速: {self.speed} km/h")
                elif key.char == 'x':
                    self.speed = max(0, self.speed - 10)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 車速: {self.speed} km/h")
                elif key.char == 'q':
                    self.left_turn = False
                    self.right_turn = False
                    self.reverse = False
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 全部關閉")
        except:
            pass
    
    def _on_release(self, key):
        """按鍵釋放"""
        try:
            if hasattr(key, 'char'):
                if key.char == 'a':
                    self.left_turn = False
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 左轉燈: OFF")
                elif key.char == 'd':
                    self.right_turn = False
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 右轉燈: OFF")
                elif key.char == 's':
                    self.reverse = False
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 倒車: OFF")
        except:
            pass
    
    def get_status(self):
        """取得當前狀態"""
        return {
            'left_turn': self.left_turn,
            'right_turn': self.right_turn,
            'reverse': self.reverse,
            'speed': self.speed
        }

# 全域實例
_mock_gpio = None

def get_mock_gpio():
    """取得模擬 GPIO 單例"""
    global _mock_gpio
    if _mock_gpio is None:
        _mock_gpio = MockGPIO()
    return _mock_gpio