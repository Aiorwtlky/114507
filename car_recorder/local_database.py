# local_database.py
import sqlite3
import os
from datetime import datetime

DB_FILE = "upload_queue.db"

class LocalDatabase:
    def __init__(self):
        self.db_path = DB_FILE
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.init_db()

    def init_db(self):
        """初始化資料庫和資料表"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_code TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                driver_id TEXT NOT NULL,
                local_video_path TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'unsynced' -- 'unsynced' or 'synced'
            );
        """)
        self.conn.commit()
        print(f"Local database '{self.db_path}' initialized.")

    def add_event(self, event_code, driver_id, local_video_path):
        """新增一筆待上傳的事件到佇列"""
        cursor = self.conn.cursor()
        timestamp = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO event_queue (event_code, timestamp, driver_id, local_video_path, status)
            VALUES (?, ?, ?, ?, ?)
        """, (event_code, timestamp, driver_id, local_video_path, 'unsynced'))
        self.conn.commit()
        print(f"[DB] Event '{event_code}' cached locally.")
        return cursor.lastrowid

    def get_unsynced_events(self, limit=5):
        """取得數筆尚未同步的事件"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM event_queue WHERE status = 'unsynced' ORDER BY id ASC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    def mark_event_as_synced(self, event_id):
        """將指定的事件標記為已同步"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE event_queue SET status = 'synced' WHERE id = ?", (event_id,))
        self.conn.commit()
        print(f"[DB] Event ID {event_id} marked as synced.")
        
    def close(self):
        self.conn.close()