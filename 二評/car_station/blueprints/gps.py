# blueprints/gps.py
from flask import Blueprint, jsonify, render_template
import serial
import platform
from config import HARDWARE_CONFIG, GPS_CONFIG
from datetime import datetime
import json

gps_bp = Blueprint('gps', __name__)

def get_hardware_port():
    """根據平台自動選擇正確的序列埠（與 GPIO 共用）"""
    system = platform.system()
    if system == "Darwin":  # macOS
        return HARDWARE_CONFIG['MAC_PORT']
    elif system == "Linux":  # Raspberry Pi
        return HARDWARE_CONFIG['RASPI_PORT']
    else:
        return HARDWARE_CONFIG['RASPI_PORT']

def parse_nmea_sentence(sentence):
    """解析 NMEA 語句"""
    try:
        # 移除開頭的 $ 和結尾的校驗碼
        if '*' in sentence:
            sentence = sentence.split('*')[0]
        sentence = sentence.lstrip('$')
        
        parts = sentence.split(',')
        sentence_type = parts[0]
        
        if sentence_type == 'GPRMC':
            # $GPRMC,時間,狀態,緯度,緯度方向,經度,經度方向,速度,航向,日期,磁偏角,磁偏角方向
            if len(parts) < 10:
                return None
                
            status = parts[2]  # A=有效, V=無效
            if status != 'A':
                return {
                    "latitude": None,
                    "longitude": None,
                    "altitude": None,
                    "satellites": 0,
                    "signal_strength": 0.0,
                    "timestamp": None,
                    "fix_status": "無定位"
                }
            
            # 解析緯度 (DDMM.MMMM 格式)
            lat_raw = parts[3]
            lat_dir = parts[4]
            latitude = None
            if lat_raw:
                lat_deg = float(lat_raw[:2])
                lat_min = float(lat_raw[2:])
                latitude = lat_deg + lat_min / 60.0
                if lat_dir == 'S':
                    latitude = -latitude
            
            # 解析經度 (DDDMM.MMMM 格式)
            lon_raw = parts[5]
            lon_dir = parts[6]
            longitude = None
            if lon_raw:
                lon_deg = float(lon_raw[:3])
                lon_min = float(lon_raw[3:])
                longitude = lon_deg + lon_min / 60.0
                if lon_dir == 'W':
                    longitude = -longitude
            
            # 組合時間和日期
            time_raw = parts[1]
            date_raw = parts[9]
            timestamp = None
            if time_raw and date_raw and len(time_raw) >= 6 and len(date_raw) >= 6:
                try:
                    hour = int(time_raw[:2])
                    minute = int(time_raw[2:4])
                    second = int(time_raw[4:6])
                    day = int(date_raw[:2])
                    month = int(date_raw[2:4])
                    year = 2000 + int(date_raw[4:6])
                    timestamp = f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}"
                except:
                    timestamp = None
            
            return {
                "latitude": latitude,
                "longitude": longitude,
                "altitude": None,  # GPRMC 不包含高度資訊
                "satellites": 0,   # GPRMC 不包含衛星數量
                "signal_strength": 1.0 if status == 'A' else 0.0,
                "timestamp": timestamp,
                "fix_status": "有定位" if status == 'A' and latitude and longitude else "無定位"
            }
            
        elif sentence_type == 'GPGGA':
            # $GPGGA,時間,緯度,緯度方向,經度,經度方向,定位品質,衛星數量,HDOP,高度,高度單位,大地水準面高度,大地水準面高度單位,差分時間,差分站台ID
            if len(parts) < 15:
                return None
            
            quality = parts[6]  # 0=無效, 1=GPS, 2=DGPS
            if quality == '0':
                return {
                    "latitude": None,
                    "longitude": None,
                    "altitude": None,
                    "satellites": 0,
                    "signal_strength": 0.0,
                    "timestamp": None,
                    "fix_status": "無定位"
                }
            
            # 解析緯度
            lat_raw = parts[2]
            lat_dir = parts[3]
            latitude = None
            if lat_raw:
                lat_deg = float(lat_raw[:2])
                lat_min = float(lat_raw[2:])
                latitude = lat_deg + lat_min / 60.0
                if lat_dir == 'S':
                    latitude = -latitude
            
            # 解析經度
            lon_raw = parts[4]
            lon_dir = parts[5]
            longitude = None
            if lon_raw:
                lon_deg = float(lon_raw[:3])
                lon_min = float(lon_raw[3:])
                longitude = lon_deg + lon_min / 60.0
                if lon_dir == 'W':
                    longitude = -longitude
            
            # 其他資訊
            satellites = int(parts[7]) if parts[7] else 0
            altitude = float(parts[9]) if parts[9] else None
            hdop = float(parts[8]) if parts[8] else 0.0
            signal_strength = 1.0 / (1.0 + hdop) if hdop > 0 else 0.0  # 簡單的信號強度估算
            
            return {
                "latitude": latitude,
                "longitude": longitude,
                "altitude": altitude,
                "satellites": satellites,
                "signal_strength": signal_strength,
                "timestamp": None,  # GPGGA 只有時間沒有日期
                "fix_status": "有定位" if int(quality) > 0 and latitude and longitude else "無定位"
            }
        
        return None
        
    except (ValueError, IndexError) as e:
        print(f"NMEA 資料解析錯誤: {e}")
        return None

def parse_nmea_gps_data(data):
    """解析從 Pico 傳來的 GPS 資料（支援 NMEA 和自訂格式）"""
    try:
        # 檢查是否為 NMEA 格式
        if data.startswith('$'):
            return parse_nmea_sentence(data)
        else:
            # 原有的自訂格式：緯度,經度,高度,衛星數量,信號強度,時間戳記
            # 例如：25.033611,121.564472,10.5,8,0.9,2024-09-21T10:30:15
            parts = data.split(',')
            if len(parts) >= 6:
                return {
                    "latitude": float(parts[0]) if parts[0] and parts[0] != '0' else None,
                    "longitude": float(parts[1]) if parts[1] and parts[1] != '0' else None,
                    "altitude": float(parts[2]) if parts[2] and parts[2] != '0' else None,
                    "satellites": int(parts[3]) if parts[3] and parts[3] != '0' else 0,
                    "signal_strength": float(parts[4]) if parts[4] and parts[4] != '0' else 0.0,
                    "timestamp": parts[5] if len(parts) > 5 else None,
                    "fix_status": "有定位" if parts[0] and float(parts[0]) != 0 else "無定位"
                }
        return None
    except (ValueError, IndexError) as e:
        print(f"GPS 資料解析錯誤: {e}")
        return None

def read_gps_from_pico():
    """讀取 Pico 的 GPS 資料"""
    port = get_hardware_port()
    
    try:
        with serial.Serial(port, HARDWARE_CONFIG['BAUD_RATE'], timeout=GPS_CONFIG['TIMEOUT']) as ser:
            ser.write(b'GPS\n')  # 傳送 GPS 資料請求
            response = ser.readline().decode().strip()
            
            if not response:
                return {
                    "status": "error",
                    "message": "⚠️ GPS 模組無回應",
                    "port": port
                }
            
            # 解析 GPS 資料
            gps_data = parse_nmea_gps_data(response)
            if gps_data:
                return {
                    "status": "success",
                    "port": port,
                    "timestamp": datetime.now().isoformat(),
                    **gps_data
                }
            else:
                return {
                    "status": "error",
                    "message": f"⚠️ GPS 資料格式錯誤：{response}",
                    "port": port,
                    "raw_data": response
                }
                
    except serial.SerialException as e:
        return {
            "status": "error",
            "message": f"⚠️ GPS 序列埠錯誤：{e}",
            "port": port
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"⚠️ 無法讀取 GPS 資料：{e}",
            "port": port
        }

@gps_bp.route('/api/gps_status')
def api_gps_status():
    """API: 取得 GPS 狀態"""
    return jsonify(read_gps_from_pico())

@gps_bp.route('/api/gps_location')
def api_gps_location():
    """API: 取得當前位置（簡化版）"""
    gps_data = read_gps_from_pico()
    
    if gps_data['status'] == 'success' and gps_data.get('latitude') and gps_data.get('longitude'):
        return jsonify({
            "status": "located",
            "latitude": gps_data['latitude'],
            "longitude": gps_data['longitude'],
            "altitude": gps_data.get('altitude'),
            "accuracy": gps_data.get('signal_strength', 0),
            "timestamp": gps_data['timestamp']
        })
    else:
        return jsonify({
            "status": "no_fix",
            "message": gps_data.get('message', '無法取得位置'),
            "satellites": gps_data.get('satellites', 0)
        })

@gps_bp.route('/api/gps_test')
def api_gps_test():
    """API: GPS 連線測試"""
    port = get_hardware_port()
    
    try:
        with serial.Serial(port, HARDWARE_CONFIG['BAUD_RATE'], timeout=GPS_CONFIG['TIMEOUT']) as ser:
            ser.write(b'GPS_TEST\n')  # 測試指令
            response = ser.readline().decode().strip()
            
            if response:
                return jsonify({
                    "status": "connected",
                    "message": "✅ GPS 模組連線正常",
                    "port": port,
                    "response": response
                })
            else:
                return jsonify({
                    "status": "no_response",
                    "message": "⚠️ GPS 模組無回應",
                    "port": port
                })
                
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"⚠️ GPS 連線失敗：{e}",
            "port": port
        })

@gps_bp.route('/status')
def gps_view():
    """GPS 狀態檢視頁面"""
    return render_template('gps/status.html')

@gps_bp.route('/api/gps_mock')
def api_gps_mock():
    """API: GPS 模擬資料（測試用）"""
    return jsonify({
        "status": "success",
        "latitude": 25.033611,  # 台北車站
        "longitude": 121.564472,
        "altitude": 10.5,
        "satellites": 8,
        "signal_strength": 0.9,
        "fix_status": "有定位",
        "timestamp": datetime.now().isoformat(),
        "port": "mock",
        "note": "這是模擬資料，用於測試"
    })