# test_gpio.py
import serial
import time

try:
    print("嘗試連接...")
    ser = serial.Serial('/dev/cu.usbmodem1401', 9600, timeout=1)
    print("✅ 連接成功！")
    ser.close()
except Exception as e:
    print(f"❌ 失敗: {e}")