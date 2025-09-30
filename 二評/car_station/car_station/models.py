# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import platform
import psutil
import json
import os
import glob

db = SQLAlchemy()

class VehicleDevice(db.Model):
    """車機資訊模型 - 對應伺服器端的 vehicle_device 表"""
    __tablename__ = 'vehicle_device'
    
    id = db.Column(db.Integer, primary_key=True, comment='流水號')
    device_number = db.Column(db.String(50), unique=True, nullable=False, comment='車機編號')
    vehicle_type = db.Column(db.String(20), nullable=False, comment='車輛類型')
    activation_date = db.Column(db.Date, nullable=False, comment='車機啟用日')
    is_active = db.Column(db.Boolean, default=True, comment='是否啟用')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='建立時間')
    
    # 車機端額外資訊
    last_sync = db.Column(db.DateTime, comment='最後同步時間')
    system_info = db.Column(db.Text, comment='系統資訊 JSON')
    
    def __repr__(self):
        return f'<VehicleDevice {self.device_number}>'
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            'id': self.id,
            'device_number': self.device_number,
            'vehicle_type': self.vehicle_type,
            'activation_date': self.activation_date.isoformat() if self.activation_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None
        }
    
    @classmethod
    def get_current_device(cls):
        """取得當前車機資訊"""
        return cls.query.first()
    
    @classmethod
    def create_default_device(cls):
        """建立預設車機資訊"""
        import json
        
        # 生成車機編號
        device_number = f"MDG-{uuid.uuid4().hex[:8].upper()}"
        
        # 取得系統資訊
        system_info = {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'architecture': platform.machine(),
            'hostname': platform.node(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'python_version': platform.python_version()
        }
        
        device = cls(
            device_number=device_number,
            vehicle_type='一般客車',  # 預設車輛類型
            activation_date=datetime.now().date(),
            is_active=True,
            system_info=json.dumps(system_info, ensure_ascii=False)
        )
        
        db.session.add(device)
        db.session.commit()
        
        return device

class Personnel(db.Model):
    """人員資訊模型 - 車機端暫存"""
    __tablename__ = 'personnel'
    
    id = db.Column(db.Integer, primary_key=True)
    personnel_number = db.Column(db.String(50), unique=True, nullable=False, comment='人員編號')
    name = db.Column(db.String(100), nullable=False, comment='姓名')
    license_number = db.Column(db.String(50), nullable=False, comment='駕照號碼')
    card_id = db.Column(db.String(50), comment='卡片ID - 用於刷卡識別')
    last_sync = db.Column(db.DateTime, comment='最後同步時間')
    
    def to_dict(self):
        return {
            'id': self.id,
            'personnel_number': self.personnel_number,
            'name': self.name,
            'license_number': self.license_number,
            'card_id': self.card_id
        }

class Trip(db.Model):
    """行程管理模型"""
    __tablename__ = 'trip'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_number = db.Column(db.String(50), unique=True, nullable=False, comment='行程編號')
    name = db.Column(db.String(200), nullable=False, comment='行程名稱')
    device_id = db.Column(db.Integer, db.ForeignKey('vehicle_device.id'), nullable=False)
    personnel_id = db.Column(db.Integer, db.ForeignKey('personnel.id'), nullable=False)
    
    # 行程狀態
    status = db.Column(db.String(20), default='準備中', comment='行程狀態: 準備中/進行中/已完成/已上傳')
    score = db.Column(db.Float, comment='行程評分')
    
    # 時間記錄
    start_time = db.Column(db.DateTime, comment='開始時間')
    end_time = db.Column(db.DateTime, comment='結束時間')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 本地儲存路徑
    video_storage_path = db.Column(db.String(500), comment='影片儲存路徑')
    data_storage_path = db.Column(db.String(500), comment='資料儲存路徑')
    
    # 同步狀態
    synced_to_server = db.Column(db.Boolean, default=False, comment='是否已同步到伺服器')
    sync_attempts = db.Column(db.Integer, default=0, comment='同步嘗試次數')
    last_sync_attempt = db.Column(db.DateTime, comment='最後同步嘗試時間')
    
    # 關聯
    device = db.relationship('VehicleDevice', backref='trips')
    personnel = db.relationship('Personnel', backref='trips')
    
    def to_dict(self):
        return {
            'id': self.id,
            'trip_number': self.trip_number,
            'name': self.name,
            'status': self.status,
            'score': self.score,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'personnel_name': self.personnel.name if self.personnel else None,
            'synced_to_server': self.synced_to_server
        }
    
    @classmethod
    def create_new_trip(cls, personnel_id, trip_name=None):
        """建立新行程"""
        device = VehicleDevice.get_current_device()
        if not device:
            raise ValueError("車機資訊不存在")
        
        trip_number = f"TRIP-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        if not trip_name:
            trip_name = f"行程 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        trip = cls(
            trip_number=trip_number,
            name=trip_name,
            device_id=device.id,
            personnel_id=personnel_id,
            status='準備中'
        )
        
        db.session.add(trip)
        db.session.commit()
        return trip

class RouteLog(db.Model):
    """路程記錄模型"""
    __tablename__ = 'route_log'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float, nullable=False, comment='緯度')
    longitude = db.Column(db.Float, nullable=False, comment='經度')
    altitude = db.Column(db.Float, comment='高度')
    speed = db.Column(db.Float, comment='車速')
    
    trip = db.relationship('Trip', backref='route_logs')

class GPIOLog(db.Model):
    """GPIO 記錄模型"""
    __tablename__ = 'gpio_log'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    gpio_type = db.Column(db.String(20), nullable=False, comment='GPIO類型: left_turn/right_turn/reverse')
    action = db.Column(db.String(10), nullable=False, comment='動作: on/off')
    duration = db.Column(db.Float, comment='持續時間(秒)')
    
    trip = db.relationship('Trip', backref='gpio_logs')

class EventLog(db.Model):
    """事件記錄模型 - 對應 AI 視覺或手動記錄"""
    __tablename__ = 'event_log'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    event_code = db.Column(db.String(10), nullable=False, comment='事件代碼: A01, B02 等')
    event_description = db.Column(db.String(255), nullable=False, comment='事件描述')
    timestamp = db.Column(db.DateTime, nullable=False)
    confidence_score = db.Column(db.Float, comment='信心分數 (AI辨識)')
    deduction_points = db.Column(db.Integer, comment='扣分')
    detection_method = db.Column(db.String(20), default='manual', comment='檢測方式: ai/manual/gpio')
    
    trip = db.relationship('Trip', backref='event_logs')

class VideoRecord(db.Model):
    """影片記錄模型"""
    __tablename__ = 'video_record'
    
    id = db.Column(db.Integer, primary_key=True)
    video_number = db.Column(db.String(50), unique=True, nullable=False)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    camera_position = db.Column(db.String(10), nullable=False, comment='攝影機位置: inside/outside')
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)  # 允許 NULL
    file_path = db.Column(db.String(500), nullable=False, comment='本地檔案路徑')
    file_size = db.Column(db.BigInteger, nullable=True)  # 允許 NULL
    uploaded = db.Column(db.Boolean, default=False, comment='是否已上傳')
    
    # 錄影狀態欄位
    recording_status = db.Column(db.String(20), default='recording', comment='錄影狀態: recording/completed/failed')
    
    trip = db.relationship('Trip', backref='video_records')

def check_system_status_on_startup():
    """系統重啟時檢查並修正異常狀態"""
    print("🔍 檢查系統異常狀態...")
    
    # 1. 檢查進行中但可能已異常的行程
    active_trips = Trip.query.filter_by(status='進行中').all()
    for trip in active_trips:
        # 檢查行程是否超過合理時間仍未結束（例如超過24小時）
        if trip.start_time:
            hours_since_start = (datetime.now() - trip.start_time).total_seconds() / 3600
            if hours_since_start > 24:  # 超過24小時
                print(f"⚠️ 發現異常行程: {trip.trip_number} (已進行 {hours_since_start:.1f} 小時)")
                trip.status = '已完成'
                trip.end_time = datetime.now()
                print(f"🔧 已自動結束異常行程: {trip.trip_number}")
    
    # 2. 檢查錄製中但可能已異常的影片
    recording_videos = VideoRecord.query.filter_by(recording_status='recording').all()
    fixed_videos = 0
    
    for video in recording_videos:
        # 檢查影片對應的行程是否已結束
        trip = Trip.query.get(video.trip_id)
        if trip and trip.status in ['已完成', '已上傳']:
            print(f"🔧 修正異常影片狀態: {video.video_number}")
            
            # 檢查檔案狀態
            if video.file_path and os.path.exists(video.file_path):
                file_size = os.path.getsize(video.file_path)
                video.file_size = file_size
                
                if file_size > 0:
                    video.recording_status = 'completed'
                    video.end_time = trip.end_time
                    print(f"✅ 影片 {video.video_number} 標記為完成")
                else:
                    video.recording_status = 'failed'
                    video.end_time = trip.end_time
                    print(f"❌ 影片 {video.video_number} 標記為失敗（空檔案）")
            else:
                video.recording_status = 'failed'
                video.end_time = trip.end_time
                video.file_size = 0
                print(f"❌ 影片 {video.video_number} 標記為失敗（檔案不存在）")
            
            fixed_videos += 1
        
        # 檢查影片是否超過合理時間仍在錄製（例如超過12小時）
        elif video.start_time:
            hours_since_start = (datetime.now() - video.start_time).total_seconds() / 3600
            if hours_since_start > 12:  # 超過12小時
                print(f"⚠️ 發現超時錄影: {video.video_number} (已錄製 {hours_since_start:.1f} 小時)")
                video.recording_status = 'failed'
                video.end_time = datetime.now()
                print(f"🔧 已自動標記為失敗: {video.video_number}")
                fixed_videos += 1
    
    # 3. 檢查孤立的影片檔案（資料庫中沒有記錄但檔案存在）
    if os.path.exists('trip_data'):
        orphaned_files = check_orphaned_video_files()
        if orphaned_files:
            print(f"⚠️ 發現 {len(orphaned_files)} 個孤立影片檔案")
    
    # 提交所有修正
    db.session.commit()
    
    if len(active_trips) > 0 or fixed_videos > 0:
        print(f"🔧 系統狀態修正完成: 異常行程 {len(active_trips)} 個, 異常影片 {fixed_videos} 個")
    else:
        print("✅ 系統狀態正常")

def check_orphaned_video_files():
    """檢查孤立的影片檔案"""
    orphaned_files = []
    
    # 掃描所有影片檔案
    video_patterns = ['trip_data/*/videos/*.mp4', 'trip_data/*/videos/*.avi']
    
    for pattern in video_patterns:
        for file_path in glob.glob(pattern):
            # 檢查資料庫中是否有對應記錄
            existing_record = VideoRecord.query.filter_by(file_path=file_path).first()
            if not existing_record:
                file_size = os.path.getsize(file_path)
                orphaned_files.append({
                    'path': file_path,
                    'size': file_size,
                    'modified': datetime.fromtimestamp(os.path.getmtime(file_path))
                })
                print(f"🗂️ 孤立檔案: {file_path} ({file_size/1024/1024:.1f}MB)")
    
    return orphaned_files

def init_database(app):
    """初始化資料庫並檢查異常狀態"""
    with app.app_context():
        db.create_all()
        
        # 檢查是否已有車機資訊，沒有的話建立預設資訊
        if not VehicleDevice.query.first():
            device = VehicleDevice.create_default_device()
            print(f"✅ 已建立預設車機資訊: {device.device_number}")
        
        # 建立測試人員資料（暫時用於刷卡測試）
        if not Personnel.query.first():
            test_personnel = Personnel(
                personnel_number="TEST001",
                name="測試駕駛員",
                license_number="TEST123456789",
                card_id="CARD001"  # 暫時測試用卡片ID
            )
            db.session.add(test_personnel)
            db.session.commit()
            print(f"✅ 已建立測試人員: {test_personnel.name}")
        
        # 系統重啟時檢查異常狀態
        check_system_status_on_startup()

# ========== AI 辨識系統新增的表格 ==========

class EventLogLocal(db.Model):
    """本地事件記錄 - AI 偵測到的事件暫存在這裡"""
    __tablename__ = 'event_log_local'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    camera_type = db.Column(db.String(10), nullable=False, comment='鏡頭類型: inside/outside')
    event_number = db.Column(db.String(10), nullable=False, comment='事件編號: A01, B02 等')
    event_description = db.Column(db.String(255), nullable=False, comment='事件描述')
    timestamp = db.Column(db.DateTime, nullable=False, comment='發生時間')
    confidence_score = db.Column(db.Float, comment='AI 信心分數')
    deduction_points = db.Column(db.Integer, comment='扣分')
    event_details = db.Column(db.JSON, comment='事件詳細資訊')
    local_image_path = db.Column(db.String(500), comment='本地截圖路徑')
    uploaded = db.Column(db.Boolean, default=False, comment='是否已上傳')
    uploaded_at = db.Column(db.DateTime, comment='上傳時間')
    
    trip = db.relationship('Trip', backref='local_events')


class UploadQueue(db.Model):
    """上傳佇列 - 網路斷線時的任務排隊"""
    __tablename__ = 'upload_queue'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    task_type = db.Column(db.String(50), nullable=False, comment='任務類型')
    task_data = db.Column(db.JSON, nullable=False, comment='任務資料')
    priority = db.Column(db.Integer, default=5, comment='優先級 1-10')
    status = db.Column(db.String(20), default='pending', comment='狀態')
    retry_count = db.Column(db.Integer, default=0, comment='重試次數')
    error_message = db.Column(db.Text, comment='錯誤訊息')
    created_at = db.Column(db.DateTime, nullable=False, comment='建立時間')
    last_attempt = db.Column(db.DateTime, comment='最後嘗試時間')
    completed_at = db.Column(db.DateTime, comment='完成時間')
    
    trip = db.relationship('Trip', backref='upload_tasks')


class TripLocal(db.Model):
    """本地行程暫存 - 離線模式使用"""
    __tablename__ = 'trip_local'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_number = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    device_id = db.Column(db.Integer, nullable=False)
    personnel_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='準備中')
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    local_score = db.Column(db.Float, comment='本地計算的評分')
    local_total_deduction = db.Column(db.Integer, comment='本地計算的總扣分')
    synced_to_server = db.Column(db.Boolean, default=False)
    server_trip_id = db.Column(db.Integer, comment='伺服器端的 Trip ID')