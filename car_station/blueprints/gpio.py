# blueprints/gpio.py
"""
GPIO 藍圖 - 包含車速資訊
"""

from flask import Blueprint, jsonify
import platform

gpio_bp = Blueprint('gpio', __name__)

# 判斷運行平台
IS_MAC = platform.system() == 'Darwin'

if IS_MAC:
    # Demo 模式
    from demo.mock_gpio import get_mock_gpio
    gpio_instance = None
else:
    # 實際硬體
    import serial
    from config import GPIO_CONFIG
    
    try:
        ser = serial.Serial(
            GPIO_CONFIG['RASPI_PORT'],
            GPIO_CONFIG['BAUD_RATE'],
            timeout=GPIO_CONFIG['TIMEOUT']
        )
    except:
        ser = None

@gpio_bp.route('/gpio_status', methods=['GET'])
def get_gpio_status():
    """取得 GPIO 狀態（包含車速）"""
    
    if IS_MAC:
        # Demo 模式
        global gpio_instance
        if gpio_instance is None:
            gpio_instance = get_mock_gpio()
        
        status = gpio_instance.get_status()
        
        return jsonify({
            'success': True,
            'data': {
                'left_turn': status['left_turn'],
                'right_turn': status['right_turn'],
                'reverse': status['reverse'],
                'speed': status['speed']  # km/h
            }
        })
    else:
        # 實際硬體
        if ser is None:
            return jsonify({
                'success': False,
                'error': 'GPIO 未連接'
            }), 500
        
        try:
            ser.write(b'STATUS\n')
            response = ser.readline().decode('utf-8').strip()
            # 解析硬體回傳的資料
            # 格式假設: "LEFT:0,RIGHT:1,REVERSE:0,SPEED:50"
            
            parts = response.split(',')
            data = {}
            for part in parts:
                key, value = part.split(':')
                data[key.lower()] = int(value)
            
            return jsonify({
                'success': True,
                'data': {
                    'left_turn': data.get('left', 0) == 1,
                    'right_turn': data.get('right', 0) == 1,
                    'reverse': data.get('reverse', 0) == 1,
                    'speed': data.get('speed', 0)
                }
            })
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500