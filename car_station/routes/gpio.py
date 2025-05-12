# routes/gpio.py

from flask import Blueprint, jsonify
import serial

gpio_bp = Blueprint('gpio', __name__)

# USB 序列埠設定（依實際情況修改）
PICO_PORT = '/dev/ttyACM0'  # Linux/Raspberry Pi 預設，Windows 通常是 'COM3'
BAUD_RATE = 115200
TIMEOUT = 1  # 1秒超時避免卡死

def read_gpio_from_pico():
    try:
        with serial.Serial(PICO_PORT, BAUD_RATE, timeout=TIMEOUT) as ser:
            ser.write(b'STATUS\n')  # 傳送請求
            response = ser.readline().decode().strip()  # 讀取回應
            values = response.split(',')

            if len(values) == 3:
                return {
                    "left": int(values[0]),
                    "right": int(values[1]),
                    "rear": int(values[2])
                }

            return {
                "left": 0,
                "right": 0,
                "rear": 0,
                "message": f"⚠️ 格式錯誤：{response}"
            }

    except Exception as e:
        return {
            "left": 0,
            "right": 0,
            "rear": 0,
            "message": f"⚠️ 無法與 Pico 通訊：{e}"
        }

@gpio_bp.route('/gpio_status', methods=['GET'])
def gpio_status():
    return jsonify(read_gpio_from_pico())