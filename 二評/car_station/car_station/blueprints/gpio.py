# blueprints/gpio.py
from flask import Blueprint, jsonify, render_template
import serial
import platform
from config import HARDWARE_CONFIG, GPIO_CONFIG
from models import db, GPIOLog, Trip
from datetime import datetime

gpio_bp = Blueprint('gpio', __name__)

# 全域變數追蹤上一次狀態
last_gpio_state = {'left': 0, 'right': 0, 'rear': 0}
gpio_start_time = {'left': None, 'right': None, 'rear': None}

def get_hardware_port():
    """根據平台自動選擇正確的序列埠（與 GPS 共用）"""
    system = platform.system()
    if system == "Darwin":  # macOS
        return HARDWARE_CONFIG['MAC_PORT']
    elif system == "Linux":  # Raspberry Pi
        return HARDWARE_CONFIG['RASPI_PORT']
    else:
        return HARDWARE_CONFIG['RASPI_PORT']

def read_gpio_from_pico():
    """讀取 Pico 的 GPIO 狀態 (方向燈和倒車檔)"""
    port = get_hardware_port()
    
    try:
        with serial.Serial(port, HARDWARE_CONFIG['BAUD_RATE'], timeout=GPIO_CONFIG['TIMEOUT']) as ser:
            ser.write(b'STATUS\n')  # 傳送請求
            response = ser.readline().decode().strip()  # 讀取回應
            
            if not response:
                return {
                    "left": 0,
                    "right": 0,
                    "rear": 0,
                    "status": "error",
                    "message": "⚠️ 無回應"
                }
            
            values = response.split(',')
            if len(values) == 3:
                return {
                    "left": int(values[0]),
                    "right": int(values[1]),
                    "rear": int(values[2]),
                    "status": "success",
                    "port": port,
                    "timestamp": None  # 可以之後加入時間戳記
                }
            else:
                return {
                    "left": 0,
                    "right": 0,
                    "rear": 0,
                    "status": "error",
                    "message": f"⚠️ 格式錯誤：{response}",
                    "port": port
                }
                
    except serial.SerialException as e:
        return {
            "left": 0,
            "right": 0,
            "rear": 0,
            "status": "error",
            "message": f"⚠️ 序列埠錯誤：{e}",
            "port": port
        }
    except Exception as e:
        return {
            "left": 0,
            "right": 0,
            "rear": 0,
            "status": "error",
            "message": f"⚠️ 無法與 Pico 通訊：{e}",
            "port": port
        }

@gpio_bp.route('/gpio_status', methods=['GET'])
def gpio_status():
    """API 端點：取得 GPIO 狀態"""
    return jsonify(read_gpio_from_pico())

@gpio_bp.route('/test_connection', methods=['GET'])
def test_connection():
    """API 端點：測試與 Pico 的連線"""
    result = read_gpio_from_pico()
    
    if result['status'] == 'success':
        return jsonify({
            "status": "connected",
            "message": "✅ Pico 連線正常",
            "port": result['port']
        })
    else:
        return jsonify({
            "status": "disconnected", 
            "message": result['message'],
            "port": result.get('port', 'unknown')
        })

@gpio_bp.route('/test')
def gpio_test():
    """GPIO 測試頁面"""
    return render_template('gpio/test.html')

@gpio_bp.route('/gpio_realtime')
def gpio_realtime():
    """即時 GPIO 狀態 API（包含記錄功能）"""
    global last_gpio_state, gpio_start_time
    
    result = read_gpio_from_pico()
    
    if result['status'] == 'success':
        current_state = {
            'left': result['left'],
            'right': result['right'], 
            'rear': result['rear']
        }
        
        # 檢查是否有進行中的行程
        active_trip = Trip.query.filter_by(status='進行中').first()
        
        if active_trip:
            # 記錄GPIO狀態變化（只記錄開始使用的時候）
            for gpio_type in ['left', 'right', 'rear']:
                current_value = current_state[gpio_type]
                last_value = last_gpio_state[gpio_type]
                
                # 只有狀態從0變1時才記錄一次使用（開始使用）
                if last_value == 0 and current_value == 1:
                    gpio_start_time[gpio_type] = datetime.now()
                    
                    # 記錄使用事件
                    gpio_log = GPIOLog(
                        trip_id=active_trip.id,
                        timestamp=gpio_start_time[gpio_type],
                        gpio_type=f"{gpio_type}_turn" if gpio_type != 'rear' else 'reverse',
                        action='on'
                    )
                    db.session.add(gpio_log)
                    print(f"記錄 {gpio_type} 方向燈使用")
                
                # 狀態從1變0時記錄持續時間（但不增加使用次數）
                elif last_value == 1 and current_value == 0:
                    if gpio_start_time[gpio_type]:
                        end_time = datetime.now()
                        duration = (end_time - gpio_start_time[gpio_type]).total_seconds()
                        
                        # 更新最後一筆記錄的持續時間
                        last_log = GPIOLog.query.filter_by(
                            trip_id=active_trip.id,
                            gpio_type=f"{gpio_type}_turn" if gpio_type != 'rear' else 'reverse',
                            action='on'
                        ).order_by(GPIOLog.timestamp.desc()).first()
                        
                        if last_log and last_log.duration is None:
                            last_log.duration = duration
                            print(f"{gpio_type} 方向燈使用時長: {duration:.1f}秒")
                        
                        # 重置開始時間
                        gpio_start_time[gpio_type] = None
            
            # 提交資料庫變更
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"GPIO記錄錯誤: {e}")
        
        # 更新上一次狀態
        last_gpio_state = current_state.copy()
        
        return jsonify({
            "status": "success",
            "left": result['left'],
            "right": result['right'], 
            "rear": result['rear'],
            "left_active": result['left'] == 1,
            "right_active": result['right'] == 1,
            "rear_active": result['rear'] == 1,
            "timestamp": result.get('timestamp')
        })
    else:
        return jsonify({
            "status": "error",
            "message": result['message'],
            "left": 0,
            "right": 0,
            "rear": 0,
            "left_active": False,
            "right_active": False,
            "rear_active": False
        })