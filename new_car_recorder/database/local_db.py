# database/local_db.py
"""
本地資料庫管理
使用 SQLite 儲存行程、事件、影片等資料
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path

from .models import Trip, AIEvent, VideoRecord, NFCMapping, IntervalScore


class LocalDatabase:
    def __init__(self, db_path: str = "car_recorder.db"):
        """初始化資料庫連線"""
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # 讓查詢結果可以用欄位名稱存取
        self.init_db()
    
    def init_db(self):
        """建立資料表"""
        cursor = self.conn.cursor()
        
        # 1. 行程表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trips (
                trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_number TEXT UNIQUE,
                user_id INTEGER,
                nfc_uid TEXT,
                device_id INTEGER,
                group_id INTEGER,
                start_time TEXT NOT NULL,
                end_time TEXT,
                score REAL,
                in_car_score REAL,
                out_car_score REAL,
                ai_suggestion TEXT,
                total_mileage REAL,
                sync_status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                backend_trip_id INTEGER
            );
        """)
        
        # 2. AI 事件表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id INTEGER NOT NULL,
                event_code TEXT NOT NULL,
                event_name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                camera_mode TEXT NOT NULL,
                confidence_score REAL,
                event_details TEXT,
                deduction_points INTEGER DEFAULT 0,
                interval_number INTEGER,
                video_clip_path TEXT,
                video_clip_url TEXT,
                sync_status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                backend_event_id INTEGER,
                FOREIGN KEY (trip_id) REFERENCES trips(trip_id)
            );
        """)
        
        # 3. 影片記錄表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS video_records (
                video_id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id INTEGER NOT NULL,
                video_number TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                local_path TEXT NOT NULL,
                video_url TEXT,
                file_size INTEGER,
                camera_type TEXT DEFAULT 'outer',
                sync_status TEXT DEFAULT 'pending',
                upload_progress REAL DEFAULT 0.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                backend_video_id INTEGER,
                FOREIGN KEY (trip_id) REFERENCES trips(trip_id)
            );
        """)
        
        # 4. NFC 對應表（本地快取）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nfc_mapping (
                nfc_uid TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                groups TEXT,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 5. 區間評分表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interval_scores (
                interval_id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id INTEGER NOT NULL,
                interval_number INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                category_a_deductions INTEGER DEFAULT 0,
                category_b_deductions INTEGER DEFAULT 0,
                category_a_score REAL,
                category_b_score REAL,
                FOREIGN KEY (trip_id) REFERENCES trips(trip_id)
            );
        """)
        
        # 建立索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trips_sync ON trips(sync_status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_trip ON ai_events(trip_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_sync ON ai_events(sync_status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_videos_trip ON video_records(trip_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_videos_sync ON video_records(sync_status);")
        
        self.conn.commit()
        print(f"[DB] Database '{self.db_path}' initialized.")
    
    # ==================== Trip 相關 ====================
    
    def create_trip(self, trip: Trip) -> int:
        """建立新行程"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO trips (
                trip_number, user_id, nfc_uid, device_id, group_id,
                start_time, sync_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            trip.trip_number, trip.user_id, trip.nfc_uid, trip.device_id,
            trip.group_id, trip.start_time.isoformat(), trip.sync_status
        ))
        self.conn.commit()
        print(f"[DB] Trip created: {trip.trip_number}")
        return cursor.lastrowid
    
    def update_trip(self, trip_id: int, **kwargs):
        """更新行程資料"""
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [trip_id]
        
        cursor = self.conn.cursor()
        cursor.execute(f"UPDATE trips SET {set_clause} WHERE trip_id = ?", values)
        self.conn.commit()
        print(f"[DB] Trip {trip_id} updated.")
    
    def get_trip(self, trip_id: int) -> Optional[Dict]:
        """取得單一行程"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM trips WHERE trip_id = ?", (trip_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_active_trip(self) -> Optional[Dict]:
        """取得進行中的行程（end_time 為 NULL）"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM trips WHERE end_time IS NULL ORDER BY trip_id DESC LIMIT 1")
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_unsynced_trips(self, limit: int = 10) -> List[Dict]:
        """取得未同步的行程"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM trips 
            WHERE sync_status = 'pending' AND end_time IS NOT NULL
            ORDER BY trip_id ASC LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== AI Event 相關 ====================
    
    def add_event(self, event: AIEvent) -> int:
        """新增 AI 事件"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO ai_events (
                trip_id, event_code, event_name, timestamp, camera_mode,
                confidence_score, event_details, deduction_points, interval_number,
                sync_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.trip_id, event.event_code, event.event_name,
            event.timestamp.isoformat(), event.camera_mode,
            event.confidence_score, event.event_details, event.deduction_points,
            event.interval_number, event.sync_status
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_events_by_trip(self, trip_id: int) -> List[Dict]:
        """取得某行程的所有事件"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM ai_events WHERE trip_id = ? ORDER BY timestamp", (trip_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_unsynced_events(self, limit: int = 50) -> List[Dict]:
        """取得未同步的事件"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM ai_events 
            WHERE sync_status = 'pending'
            ORDER BY event_id ASC LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    def update_event_sync_status(self, event_id: int, status: str, backend_id: int = None):
        """更新事件同步狀態"""
        cursor = self.conn.cursor()
        if backend_id:
            cursor.execute("""
                UPDATE ai_events 
                SET sync_status = ?, backend_event_id = ? 
                WHERE event_id = ?
            """, (status, backend_id, event_id))
        else:
            cursor.execute("UPDATE ai_events SET sync_status = ? WHERE event_id = ?", (status, event_id))
        self.conn.commit()
    
    # ==================== Video Record 相關 ====================
    
    def add_video_record(self, video: VideoRecord) -> int:
        """新增影片記錄"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO video_records (
                trip_id, video_number, start_time, end_time, local_path,
                camera_type, file_size, sync_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            video.trip_id, video.video_number, video.start_time.isoformat(),
            video.end_time.isoformat() if video.end_time else None,
            video.local_path, video.camera_type, video.file_size, video.sync_status
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def update_video_upload_progress(self, video_id: int, progress: float):
        """更新影片上傳進度"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE video_records SET upload_progress = ? WHERE video_id = ?", (progress, video_id))
        self.conn.commit()
    
    def update_video_sync_status(self, video_id: int, status: str, video_url: str = None, backend_id: int = None):
        """更新影片同步狀態"""
        cursor = self.conn.cursor()
        if video_url:
            cursor.execute("""
                UPDATE video_records 
                SET sync_status = ?, video_url = ?, backend_video_id = ?
                WHERE video_id = ?
            """, (status, video_url, backend_id, video_id))
        else:
            cursor.execute("UPDATE video_records SET sync_status = ? WHERE video_id = ?", (status, video_id))
        self.conn.commit()
    
    def get_unsynced_videos(self, limit: int = 5) -> List[Dict]:
        """取得未同步的影片"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM video_records 
            WHERE sync_status = 'pending'
            ORDER BY video_id ASC LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== NFC Mapping 相關 ====================
    
    def cache_nfc_mapping(self, mapping: NFCMapping):
        """快取 NFC 對應資訊"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO nfc_mapping (
                nfc_uid, user_id, username, first_name, last_name, groups, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            mapping.nfc_uid, mapping.user_id, mapping.username,
            mapping.first_name, mapping.last_name,
            json.dumps(mapping.groups) if mapping.groups else None,
            datetime.now().isoformat()
        ))
        self.conn.commit()
    
    def get_nfc_mapping(self, nfc_uid: str) -> Optional[Dict]:
        """取得 NFC 對應資訊"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM nfc_mapping WHERE nfc_uid = ?", (nfc_uid,))
        row = cursor.fetchone()
        if row:
            data = dict(row)
            if data['groups']:
                data['groups'] = json.loads(data['groups'])
            return data
        return None
    
    # ==================== Interval Score 相關 ====================
    
    def add_interval_score(self, interval: IntervalScore) -> int:
        """新增區間評分"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO interval_scores (
                trip_id, interval_number, start_time, end_time,
                category_a_deductions, category_b_deductions,
                category_a_score, category_b_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            interval.trip_id, interval.interval_number,
            interval.start_time.isoformat(), interval.end_time.isoformat(),
            interval.category_a_deductions, interval.category_b_deductions,
            interval.category_a_score, interval.category_b_score
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_intervals_by_trip(self, trip_id: int) -> List[Dict]:
        """取得某行程的所有區間評分"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM interval_scores 
            WHERE trip_id = ? 
            ORDER BY interval_number
        """, (trip_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """關閉資料庫連線"""
        self.conn.close()
        print("[DB] Database connection closed.")