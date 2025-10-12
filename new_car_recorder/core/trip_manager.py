# core/trip_manager.py
"""
行程管理模組
負責管理行程的開始、結束、評分計算
"""

from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
import configparser

from database.local_db import LocalDatabase
from database.models import Trip, AIEvent, VideoRecord, NFCMapping, IntervalScore, parse_event_code, get_event_info
from .score_calculator import ScoreCalculator
from .video_recorder import VideoRecorder
from .storage_manager import StorageManager


class TripManager:
    def __init__(self, db: LocalDatabase, config_path: str = "config.ini"):
        """
        初始化行程管理器
        
        Args:
            db: 資料庫實例
            config_path: 設定檔路徑
        """
        self.db = db
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        # 取得設備資訊
        self.device_id = self.config.get('device', 'device_id', fallback='UNKNOWN')
        
        # 初始化子模組
        self.score_calculator = ScoreCalculator()
        self.video_recorder = VideoRecorder(config_path)
        self.storage_manager = StorageManager()
        
        # 目前進行中的行程
        self.current_trip: Optional[Dict] = None
        self.current_trip_id: Optional[int] = None
        
        print(f"[TripManager] Initialized with device_id: {self.device_id}")
    
    def start_trip(self, nfc_uid: str, user_info: Dict) -> Optional[int]:
        """
        開始一趟新行程
        
        Args:
            nfc_uid: NFC 卡片 UID
            user_info: 使用者資訊（從 API 或本地快取取得）
        
        Returns:
            trip_id (本地資料庫 ID)
        """
        # 檢查是否已有進行中的行程
        if self.current_trip:
            print("[TripManager] ERROR: There is already an active trip!")
            return None
        
        # 生成行程編號
        trip_number = self._generate_trip_number()
        
        # 取得使用者的群組（如果有的話，取第一個）
        groups = user_info.get('groups', [])
        group_id = groups[0]['group_id'] if groups else None
        
        # 建立 Trip 物件
        trip = Trip(
            trip_number=trip_number,
            user_id=user_info['user_id'],
            nfc_uid=nfc_uid,
            device_id=1,  # TODO: 從設定檔或資料庫取得真實的 device ID
            group_id=group_id,
            start_time=datetime.now(),
            sync_status='pending'
        )
        
        # 寫入資料庫
        trip_id = self.db.create_trip(trip)
        
        # 更新目前行程
        self.current_trip_id = trip_id
        self.current_trip = self.db.get_trip(trip_id)
        
        # 開始錄影
        self._start_recording(trip_number, datetime.now())
        
        print(f"[TripManager] Trip started: {trip_number} (trip_id={trip_id})")
        return trip_id
    
    def end_trip(self, total_mileage: float = 0.0) -> Optional[Dict]:
        """
        結束目前的行程
        
        Args:
            total_mileage: 總里程數
        
        Returns:
            包含評分結果的字典
        """
        if not self.current_trip:
            print("[TripManager] ERROR: No active trip to end!")
            return None
        
        trip_id = self.current_trip_id
        end_time = datetime.now()
        
        # 停止錄影
        inner_video, outer_video = self.video_recorder.stop_recording()
        
        # 將影片記錄寫入資料庫
        if outer_video and outer_video.exists():
            video_record = VideoRecord(
                trip_id=trip_id,
                video_number=f"VID_{self.current_trip['trip_number']}",
                start_time=datetime.fromisoformat(self.current_trip['start_time']),
                end_time=end_time,
                local_path=str(outer_video),
                file_size=outer_video.stat().st_size,
                camera_type='outer',
                sync_status='pending'
            )
            self.db.add_video_record(video_record)
            print(f"[TripManager] Video recorded: {outer_video}")
        
        # 計算評分
        score_result = self._calculate_scores(trip_id, end_time)
        
        # 更新行程
        self.db.update_trip(
            trip_id,
            end_time=end_time.isoformat(),
            total_mileage=total_mileage,
            score=score_result['score'],
            in_car_score=score_result['in_car_score'],
            out_car_score=score_result['out_car_score'],
            ai_suggestion=score_result['ai_suggestion']
        )
        
        # 儲存區間評分
        for interval in score_result['intervals']:
            interval_obj = IntervalScore(
                trip_id=trip_id,
                interval_number=interval['interval_number'],
                start_time=interval['start_time'],
                end_time=interval['end_time'],
                category_a_deductions=interval['category_a_deductions'],
                category_b_deductions=interval['category_b_deductions'],
                category_a_score=interval['category_a_score'],
                category_b_score=interval['category_b_score']
            )
            self.db.add_interval_score(interval_obj)
        
        print(f"[TripManager] Trip ended: {self.current_trip['trip_number']}")
        print(f"  - Score: {score_result['score']:.2f}")
        print(f"  - In-car: {score_result['in_car_score']:.2f}")
        print(f"  - Out-car: {score_result['out_car_score']:.2f}")
        
        # 重置目前行程
        result = {
            'trip_id': trip_id,
            'trip_number': self.current_trip['trip_number'],
            **score_result
        }
        
        self.current_trip = None
        self.current_trip_id = None
        
        return result
    
    def add_event(self, event_string: str, camera_mode: str, confidence: float = 0.9) -> Optional[int]:
        """
        新增一筆 AI 事件
        
        Args:
            event_string: 事件字串（例如 "A01: 重度疲勞"）
            camera_mode: 'inner' or 'outer'
            confidence: 信心分數
        
        Returns:
            event_id
        """
        if not self.current_trip:
            print("[TripManager] WARNING: No active trip, event not recorded.")
            return None
        
        # 解析事件代碼
        event_code, event_name = parse_event_code(event_string)
        event_info = get_event_info(event_code)
        
        # 計算目前屬於第幾個 15 分鐘區間
        trip_start = datetime.fromisoformat(self.current_trip['start_time'])
        elapsed = (datetime.now() - trip_start).total_seconds() / 60  # 分鐘
        interval_number = int(elapsed // 15) + 1
        
        # 建立事件
        event = AIEvent(
            trip_id=self.current_trip_id,
            event_code=event_code,
            event_name=event_name,
            timestamp=datetime.now(),
            camera_mode=camera_mode,
            confidence_score=confidence,
            deduction_points=event_info['deduction'],
            interval_number=interval_number,
            sync_status='pending'
        )
        
        event_id = self.db.add_event(event)
        print(f"[TripManager] Event added: {event_code} - {event_name} (interval {interval_number})")
        
        return event_id
    
    def get_current_trip_info(self) -> Optional[Dict]:
        """取得目前行程的資訊"""
        if not self.current_trip:
            return None
        
        # 計算行程時長
        start_time = datetime.fromisoformat(self.current_trip['start_time'])
        duration = (datetime.now() - start_time).total_seconds()
        
        # 取得事件數量
        events = self.db.get_events_by_trip(self.current_trip_id)
        
        return {
            'trip_number': self.current_trip['trip_number'],
            'start_time': start_time,
            'duration_seconds': duration,
            'event_count': len(events),
            'is_recording': self.video_recorder.is_recording_active()
        }
    
    def _generate_trip_number(self) -> str:
        """生成唯一的行程編號"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"TRIP_{timestamp}"
    
    def _start_recording(self, trip_number: str, start_time: datetime):
        """開始錄影"""
        outer_path = self.storage_manager.get_video_path(trip_number, start_time, 'outer')
        inner_path = self.storage_manager.get_video_path(trip_number, start_time, 'inner')
        
        self.video_recorder.start_recording(inner_path=inner_path, outer_path=outer_path)
    
    def _calculate_scores(self, trip_id: int, end_time: datetime) -> Dict:
        """計算行程評分"""
        events = self.db.get_events_by_trip(trip_id)
        trip_start = datetime.fromisoformat(self.current_trip['start_time'])
        
        return self.score_calculator.calculate_trip_score(events, trip_start, end_time)