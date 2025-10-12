# sync/sync_service.py
"""
同步服務
在背景執行緒中定期將本地資料同步到後端
"""

import time
import threading
from typing import Optional
from datetime import datetime
from pathlib import Path

from database.local_db import LocalDatabase
from .api_client import APIClient
from .gcs_uploader import GCSUploader


class SyncService:
    def __init__(self, db: LocalDatabase, api_client: APIClient, gcs_uploader: GCSUploader):
        """
        初始化同步服務
        
        Args:
            db: 資料庫實例
            api_client: API 客戶端
            gcs_uploader: GCS 上傳器
        """
        self.db = db
        self.api = api_client
        self.gcs = gcs_uploader
        
        # 同步狀態
        self.is_running = False
        self.sync_thread: Optional[threading.Thread] = None
        
        # 同步間隔（秒）
        self.sync_interval = 60  # 每 60 秒同步一次
        
        print("[SyncService] Initialized")
    
    def start(self):
        """啟動同步服務"""
        if self.is_running:
            print("[SyncService] Already running")
            return
        
        self.is_running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        print("[SyncService] Started")
    
    def stop(self):
        """停止同步服務"""
        self.is_running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        print("[SyncService] Stopped")
    
    def _sync_loop(self):
        """同步迴圈（在背景執行緒中運行）"""
        while self.is_running:
            try:
                self.sync_all()
            except Exception as e:
                print(f"[SyncService] Sync error: {e}")
            
            # 等待下一次同步
            time.sleep(self.sync_interval)
    
    def sync_all(self):
        """執行一次完整的同步"""
        print("[SyncService] Starting sync...")
        
        # 1. 同步行程
        self._sync_trips()
        
        # 2. 同步事件
        self._sync_events()
        
        # 3. 同步影片
        self._sync_videos()
        
        print("[SyncService] Sync completed")
    
    def _sync_trips(self):
        """同步行程資料"""
        trips = self.db.get_unsynced_trips(limit=10)
        
        for trip in trips:
            try:
                # 更新狀態為 syncing
                self.db.update_trip(trip['trip_id'], sync_status='syncing')
                
                # 如果還沒有 backend_trip_id，表示需要建立
                if not trip.get('backend_trip_id'):
                    # 開始行程
                    trip_data = {
                        'trip_number': trip['trip_number'],
                        'device': trip['device_id'],
                        'personnel': trip['user_id'],
                        'group': trip['group_id'],
                        'start_time': trip['start_time']
                    }
                    backend_data = self.api.start_trip(trip_data)
                    
                    if backend_data:
                        backend_trip_id = backend_data['id']
                        self.db.update_trip(trip['trip_id'], backend_trip_id=backend_trip_id)
                    else:
                        self.db.update_trip(trip['trip_id'], sync_status='failed')
                        continue
                else:
                    backend_trip_id = trip['backend_trip_id']
                
                # 結束行程
                end_data = {
                    'end_time': trip['end_time'],
                    'total_mileage': trip.get('total_mileage', 0.0)
                }
                success = self.api.end_trip(backend_trip_id, end_data)
                
                if success:
                    self.db.update_trip(trip['trip_id'], sync_status='synced')
                    print(f"[SyncService] Trip synced: {trip['trip_number']}")
                else:
                    self.db.update_trip(trip['trip_id'], sync_status='failed')
                    
            except Exception as e:
                print(f"[SyncService] Trip sync error: {e}")
                self.db.update_trip(trip['trip_id'], sync_status='failed')
    
    def _sync_events(self):
        """同步事件資料"""
        events = self.db.get_unsynced_events(limit=50)
        
        for event in events:
            try:
                # 取得對應的 backend_trip_id
                trip = self.db.get_trip(event['trip_id'])
                if not trip or not trip.get('backend_trip_id'):
                    print(f"[SyncService] Event {event['event_id']} skipped: trip not synced yet")
                    continue
                
                # 上傳事件
                # TODO: 需要將 event_code 對應到後端的 ScoringStandard ID
                # 這裡先簡化為直接用 event_code
                event_data = {
                    'trip': trip['backend_trip_id'],
                    'event': self._get_scoring_standard_id(event['event_code']),
                    'timestamp': event['timestamp'],
                    'event_details': event.get('event_details', event['event_name']),
                    'confidence_score': event.get('confidence_score', 0.9)
                }
                
                backend_event_id = self.api.upload_event(event_data)
                
                if backend_event_id:
                    self.db.update_event_sync_status(event['event_id'], 'synced', backend_event_id)
                    print(f"[SyncService] Event synced: {event['event_code']}")
                else:
                    self.db.update_event_sync_status(event['event_id'], 'failed')
                    
            except Exception as e:
                print(f"[SyncService] Event sync error: {e}")
                self.db.update_event_sync_status(event['event_id'], 'failed')
    
    def _sync_videos(self):
        """同步影片資料"""
        videos = self.db.get_unsynced_videos(limit=5)
        
        for video in videos:
            try:
                # 取得對應的 backend_trip_id
                trip = self.db.get_trip(video['trip_id'])
                if not trip or not trip.get('backend_trip_id'):
                    print(f"[SyncService] Video {video['video_id']} skipped: trip not synced yet")
                    continue
                
                # 1. 上傳影片到 GCS
                local_path = Path(video['local_path'])
                if not local_path.exists():
                    print(f"[SyncService] Video file not found: {local_path}")
                    self.db.update_video_sync_status(video['video_id'], 'failed')
                    continue
                
                print(f"[SyncService] Uploading video: {local_path.name}")
                
                # 上傳並追蹤進度
                def progress_callback(percent):
                    self.db.update_video_upload_progress(video['video_id'], percent)
                
                video_url = self.gcs.upload_with_progress(
                    local_path,
                    progress_callback=progress_callback
                )
                
                if not video_url:
                    self.db.update_video_sync_status(video['video_id'], 'failed')
                    continue
                
                # 2. 註冊影片到後端
                video_data = {
                    'trip': trip['backend_trip_id'],
                    'video_url': video_url,
                    'start_time': video['start_time'],
                    'end_time': video['end_time'],
                    'file_size': video.get('file_size', 0)
                }
                
                backend_video_id = self.api.register_video(video_data)
                
                if backend_video_id:
                    self.db.update_video_sync_status(
                        video['video_id'], 
                        'synced', 
                        video_url, 
                        backend_video_id
                    )
                    print(f"[SyncService] Video synced: {video['video_number']}")
                else:
                    self.db.update_video_sync_status(video['video_id'], 'failed')
                    
            except Exception as e:
                print(f"[SyncService] Video sync error: {e}")
                self.db.update_video_sync_status(video['video_id'], 'failed')
    
    def _get_scoring_standard_id(self, event_code: str) -> int:
        """
        將事件代碼對應到後端的 ScoringStandard ID
        
        TODO: 這應該從後端 API 取得對照表
        目前先用硬編碼
        """
        mapping = {
            'A01': 1,
            'A02': 2,
            'A03': 3,
            'A04': 4,
            'A05': 5,
            'B01': 6,
            'B02': 7,
            'B03': 8,
        }
        return mapping.get(event_code, 1)  # 預設回傳 1