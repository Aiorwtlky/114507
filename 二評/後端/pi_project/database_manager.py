import sqlite3
import json
import time
import logging
import threading
from typing import Dict, List, Optional, Any
import os

logger = logging.getLogger(__name__)

class DatabaseManager:
    """資料庫管理器 - 使用 SQLite 適合樹莓派"""
    
    def __init__(self, config):
        self.config = config
        self.db_path = os.path.join(config.data_dir, 'system.db')
        self.connection_lock = threading.Lock()
        
        # 初始化資料庫
        self._initialize_database()
    
    def _initialize_database(self):
        """初始化資料庫表格"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 駕駛員監控記錄表
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS driver_monitoring (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    driver_id TEXT,
                    ear_value REAL,
                    eye_state TEXT,
                    head_pose TEXT,
                    alerts TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                
                # ADAS 記錄表
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS adas_monitoring (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    lane_detected BOOLEAN,
                    vehicles_count INTEGER,
                    traffic_lights TEXT,
                    alerts TEXT,
                    speed_kmh REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                
                # 影片上傳記錄表
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS video_uploads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    local_path TEXT NOT NULL,
                    cloud_url TEXT,
                    cloud_public_id TEXT,
                    file_size INTEGER,
                    upload_timestamp REAL,
                    alerts TEXT,
                    driver_info TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                
                # 系統統計表
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    cpu_usage REAL,
                    memory_usage REAL,
                    temperature REAL,
                    disk_usage REAL,
                    camera_fps REAL,
                    processing_fps REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                
                # 警報統計表
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS alert_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    alert_code TEXT NOT NULL,
                    alert_count INTEGER DEFAULT 0,
                    total_score INTEGER DEFAULT 0,
                    driver_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date, alert_code, driver_id)
                )
                ''')
                
                # 建立索引以提升查詢效能
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_driver_timestamp ON driver_monitoring(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_adas_timestamp ON adas_monitoring(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_uploads_timestamp ON video_uploads(upload_timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_stats_timestamp ON system_stats(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_alert_date ON alert_summary(date)')
                
                conn.commit()
                logger.info("資料庫初始化完成")
                
        except Exception as e:
            logger.error(f"資料庫初始化失敗: {e}")
    
    def _get_connection(self):
        """取得資料庫連接"""
        return sqlite3.connect(
            self.db_path,
            timeout=30.0,
            check_same_thread=False
        )
    
    def record_driver_monitoring(self, data: Dict):
        """記錄駕駛員監控資料"""
        try:
            with self.connection_lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                    INSERT INTO driver_monitoring 
                    (timestamp, driver_id, ear_value, eye_state, head_pose, alerts)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        data.get('timestamp', time.time()),
                        data.get('driver_id'),
                        data.get('ear_value'),
                        data.get('eye_state'),
                        json.dumps(data.get('head_pose', {}), ensure_ascii=False),
                        json.dumps(data.get('alerts', []), ensure_ascii=False)
                    ))
                    
                    # 更新警報統計
                    self._update_alert_summary(cursor, data.get('alerts', []), data.get('driver_id'))
                    
                    conn.commit()
                    
        except Exception as e:
            logger.error(f"記錄駕駛員監控資料失敗: {e}")
    
    def record_adas_monitoring(self, data: Dict):
        """記錄 ADAS 監控資料"""
        try:
            with self.connection_lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                    INSERT INTO adas_monitoring 
                    (timestamp, lane_detected, vehicles_count, traffic_lights, alerts, speed_kmh)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        data.get('timestamp', time.time()),
                        data.get('lane_detected', False),
                        len(data.get('vehicles_detected', [])),
                        json.dumps(data.get('traffic_lights', []), ensure_ascii=False),
                        json.dumps(data.get('alerts', []), ensure_ascii=False),
                        data.get('speed_kmh', 0)
                    ))
                    
                    # 更新警報統計
                    self._update_alert_summary(cursor, data.get('alerts', []))
                    
                    conn.commit()
                    
        except Exception as e:
            logger.error(f"記錄 ADAS 監控資料失敗: {e}")
    
    def record_upload(self, data: Dict):
        """記錄影片上傳資料"""
        try:
            with self.connection_lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                    INSERT INTO video_uploads 
                    (local_path, cloud_url, cloud_public_id, file_size, upload_timestamp, alerts, driver_info)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        data.get('local_path'),
                        data.get('cloud_url'),
                        data.get('cloud_public_id'),
                        data.get('file_size', 0),
                        data.get('upload_timestamp', time.time()),
                        data.get('alerts', '[]'),
                        data.get('driver_info', '{}')
                    ))
                    
                    conn.commit()
                    
        except Exception as e:
            logger.error(f"記錄上傳資料失敗: {e}")
    
    def record_system_stats(self, data: Dict):
        """記錄系統統計資料"""
        try:
            with self.connection_lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                    INSERT INTO system_stats 
                    (timestamp, cpu_usage, memory_usage, temperature, disk_usage, camera_fps, processing_fps)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        data.get('timestamp', time.time()),
                        data.get('cpu_usage'),
                        data.get('memory_usage'),
                        data.get('temperature'),
                        data.get('disk_usage'),
                        data.get('camera_fps'),
                        data.get('processing_fps')
                    ))
                    
                    conn.commit()
                    
        except Exception as e:
            logger.error(f"記錄系統統計失敗: {e}")
    
    def _update_alert_summary(self, cursor, alerts: List[Dict], driver_id: str = None):
        """更新警報統計"""
        try:
            today = time.strftime('%Y-%m-%d')
            
            for alert in alerts:
                alert_code = alert.get('code', 'UNKNOWN')
                alert_score = alert.get('score', 0)
                
                cursor.execute('''
                INSERT OR REPLACE INTO alert_summary 
                (date, alert_code, alert_count, total_score, driver_id)
                VALUES (
                    ?, ?, 
                    COALESCE((SELECT alert_count FROM alert_summary 
                             WHERE date = ? AND alert_code = ? AND driver_id = ?), 0) + 1,
                    COALESCE((SELECT total_score FROM alert_summary 
                             WHERE date = ? AND alert_code = ? AND driver_id = ?), 0) + ?,
                    ?
                )
                ''', (today, alert_code, today, alert_code, driver_id, 
                     today, alert_code, driver_id, alert_score, driver_id))
                
        except Exception as e:
            logger.error(f"更新警報統計失敗: {e}")
    
    def get_daily_alert_summary(self, date: str = None, driver_id: str = None) -> List[Dict]:
        """取得每日警報統計"""
        try:
            if date is None:
                date = time.strftime('%Y-%m-%d')
            
            with self.connection_lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    query = '''
                    SELECT alert_code, alert_count, total_score, driver_id
                    FROM alert_summary 
                    WHERE date = ?
                    '''
                    params = [date]
                    
                    if driver_id:
                        query += ' AND driver_id = ?'
                        params.append(driver_id)
                    
                    query += ' ORDER BY total_score DESC'
                    
                    cursor.execute(query, params)
                    results = cursor.fetchall()
                    
                    return [
                        {
                            'alert_code': row[0],
                            'alert_count': row[1],
                            'total_score': row[2],
                            'driver_id': row[3]
                        }
                        for row in results
                    ]
                    
        except Exception as e:
            logger.error(f"取得每日警報統計失敗: {e}")
            return []
    
    def get_system_stats(self, hours: int = 24) -> List[Dict]:
        """取得系統統計資料"""
        try:
            since_timestamp = time.time() - (hours * 3600)
            
            with self.connection_lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                    SELECT timestamp, cpu_usage, memory_usage, temperature, 
                           disk_usage, camera_fps, processing_fps
                    FROM system_stats 
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    ''', (since_timestamp,))
                    
                    results = cursor.fetchall()
                    
                    return [
                        {
                            'timestamp': row[0],
                            'cpu_usage': row[1],
                            'memory_usage': row[2],
                            'temperature': row[3],
                            'disk_usage': row[4],
                            'camera_fps': row[5],
                            'processing_fps': row[6]
                        }
                        for row in results
                    ]
                    
        except Exception as e:
            logger.error(f"取得系統統計失敗: {e}")
            return []
    
    def get_driver_performance(self, driver_id: str, days: int = 7) -> Dict:
        """取得駕駛員表現統計"""
        try:
            since_timestamp = time.time() - (days * 24 * 3600)
            
            with self.connection_lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # 取得駕駛時間
                    cursor.execute('''
                    SELECT COUNT(*) * 5 as total_seconds
                    FROM driver_monitoring 
                    WHERE driver_id = ? AND timestamp >= ?
                    ''', (driver_id, since_timestamp))
                    
                    driving_time = cursor.fetchone()[0] if cursor.fetchone() else 0
                    
                    # 取得警報統計
                    cursor.execute('''
                    SELECT alert_code, SUM(alert_count) as count, SUM(total_score) as score
                    FROM alert_summary 
                    WHERE driver_id = ? AND date >= ?
                    GROUP BY alert_code
                    ORDER BY score DESC
                    ''', (driver_id, time.strftime('%Y-%m-%d', time.localtime(since_timestamp))))
                    
                    alert_stats = [
                        {
                            'code': row[0],
                            'count': row[1],
                            'total_score': row[2]
                        }
                        for row in cursor.fetchall()
                    ]
                    
                    total_score = sum(alert['total_score'] for alert in alert_stats)
                    
                    return {
                        'driver_id': driver_id,
                        'driving_time_seconds': driving_time,
                        'total_alert_score': total_score,
                        'alert_breakdown': alert_stats,
                        'safety_rating': max(0, 100 - total_score)  # 簡單的安全評分
                    }
                    
        except Exception as e:
            logger.error(f"取得駕駛員表現統計失敗: {e}")
            return {}
    
    def cleanup_old_records(self, days_to_keep: int = 30):
        """清理舊記錄"""
        try:
            cutoff_timestamp = time.time() - (days_to_keep * 24 * 3600)
            
            with self.connection_lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # 清理舊的監控記錄
                    tables = ['driver_monitoring', 'adas_monitoring', 'system_stats']
                    
                    for table in tables:
                        cursor.execute(f'DELETE FROM {table} WHERE timestamp < ?', (cutoff_timestamp,))
                        deleted = cursor.rowcount
                        if deleted > 0:
                            logger.info(f"已清理 {table} 表中 {deleted} 條舊記錄")
                    
                    # 清理舊的警報統計 (保留更久)
                    cutoff_date = time.strftime('%Y-%m-%d', time.localtime(time.time() - (90 * 24 * 3600)))
                    cursor.execute('DELETE FROM alert_summary WHERE date < ?', (cutoff_date,))
                    
                    # 壓縮資料庫
                    cursor.execute('VACUUM')
                    
                    conn.commit()
                    logger.info("資料庫清理和壓縮完成")
                    
        except Exception as e:
            logger.error(f"清理舊記錄失敗: {e}")
    
    def get_database_info(self) -> Dict:
        """取得資料庫資訊"""
        try:
            with self.connection_lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # 取得各表的記錄數量
                    tables = ['driver_monitoring', 'adas_monitoring', 'video_uploads', 
                             'system_stats', 'alert_summary']
                    
                    table_info = {}
                    for table in tables:
                        cursor.execute(f'SELECT COUNT(*) FROM {table}')
                        table_info[table] = cursor.fetchone()[0]
                    
                    # 取得資料庫檔案大小
                    db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                    
                    return {
                        'database_path': self.db_path,
                        'database_size_mb': db_size / (1024 * 1024),
                        'table_counts': table_info
                    }
                    
        except Exception as e:
            logger.error(f"取得資料庫資訊失敗: {e}")
            return {}

# 測試用的獨立執行
if __name__ == "__main__":
    from config import config
    
    db = DatabaseManager(config)
    
    # 測試記錄
    test_data = {
        'timestamp': time.time(),
        'driver_id': 'test_driver',
        'ear_value': 0.25,
        'eye_state': 'open',
        'head_pose': {'looking_down': False},
        'alerts': [{'code': 'A01', 'score': 25}]
    }
    
    db.record_driver_monitoring(test_data)
    
    # 查看統計
    print("今日警報統計:", db.get_daily_alert_summary())
    print("資料庫資訊:", db.get_database_info())