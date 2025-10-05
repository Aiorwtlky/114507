# blueprints/device_info.py
from flask import Blueprint, render_template, jsonify, request
from models import db, VehicleDevice
from config import SERVER_URL
import json
import platform
import psutil
from datetime import datetime

device_info_bp = Blueprint('device_info', __name__)

@device_info_bp.route('/info')
def device_info():
    """車機資訊頁面"""
    device = VehicleDevice.get_current_device()
    
    if not device:
        # 如果沒有車機資訊，建立預設的
        device = VehicleDevice.create_default_device()
    
    return render_template('device_info/info.html', device=device)

@device_info_bp.route('/api/device_info')
def api_device_info():
    """API: 取得車機資訊"""
    device = VehicleDevice.get_current_device()
    
    if not device:
        return jsonify({"error": "車機資訊不存在"}), 404
    
    return jsonify(device.to_dict())

@device_info_bp.route('/api/system_status')
def api_system_status():
    """API: 取得即時系統狀態"""
    try:
        # CPU 使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 記憶體使用率
        memory = psutil.virtual_memory()
        
        # 磁碟使用率
        disk = psutil.disk_usage('/')
        
        # 網路狀態
        network = psutil.net_io_counters()
        
        # 系統運行時間
        boot_time = psutil.boot_time()
        uptime = datetime.now().timestamp() - boot_time
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'usage_percent': cpu_percent,
                'count': psutil.cpu_count()
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': (disk.used / disk.total) * 100
            },
            'network': {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv
            },
            'uptime_seconds': uptime,
            'platform': {
                'system': platform.system(),
                'release': platform.release(),
                'machine': platform.machine()
            }
        }
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({"error": f"無法取得系統狀態: {str(e)}"}), 500

@device_info_bp.route('/api/update_device', methods=['POST'])
def api_update_device():
    """API: 更新車機資訊"""
    device = VehicleDevice.get_current_device()
    
    if not device:
        return jsonify({"error": "車機資訊不存在"}), 404
    
    data = request.get_json()
    
    try:
        # 更新允許修改的欄位
        if 'vehicle_type' in data:
            device.vehicle_type = data['vehicle_type']
        
        if 'is_active' in data:
            device.is_active = data['is_active']
        
        # 更新同步時間
        device.last_sync = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "車機資訊已更新",
            "device": device.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"更新失敗: {str(e)}"}), 500

@device_info_bp.route('/api/sync_server', methods=['POST'])
def api_sync_server():
    """API: 與伺服器同步（預留）"""
    device = VehicleDevice.get_current_device()
    
    if not device:
        return jsonify({"error": "車機資訊不存在"}), 404
    
    # TODO: 實作與伺服器的同步邏輯
    # 這裡之後會連接到 SERVER_URL 進行資料同步
    
    return jsonify({
        "status": "pending",
        "message": "伺服器同步功能開發中",
        "server_url": SERVER_URL,
        "last_sync": device.last_sync.isoformat() if device.last_sync else None
    })