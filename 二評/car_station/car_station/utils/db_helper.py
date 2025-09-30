# utils/db_helper.py
from datetime import datetime
from typing import List, Dict, Optional
from models import db

class LocalEventHelper:
    """本地事件資料庫操作"""
    
    @staticmethod
    def create_event(
        trip_id: int,
        camera_type: str,
        event_number: str,
        event_description: str,
        confidence_score: float,
        deduction_points: int,
        event_details: Optional[Dict] = None,
        local_image_path: Optional[str] = None
    ):
        """建立本地事件記錄"""
        from models import EventLogLocal
        
        event = EventLogLocal(
            trip_id=trip_id,
            camera_type=camera_type,
            event_number=event_number,
            event_description=event_description,
            timestamp=datetime.now(),
            confidence_score=confidence_score,
            deduction_points=deduction_points,
            event_details=event_details,
            local_image_path=local_image_path,
            uploaded=False
        )
        
        db.session.add(event)
        db.session.commit()
        
        print(f"✅ 本地事件已記錄: {event_number} - {event_description}")
        return event
    
    @staticmethod
    def get_pending_events(trip_id: int):
        """取得待上傳的事件"""
        from models import EventLogLocal
        return EventLogLocal.query.filter_by(trip_id=trip_id, uploaded=False).all()
    
    @staticmethod
    def get_trip_events_summary(trip_id: int) -> Dict:
        """取得行程事件摘要"""
        from models import EventLogLocal
        events = EventLogLocal.query.filter_by(trip_id=trip_id).all()
        
        total_deduction = sum(e.deduction_points for e in events)
        event_counts = {}
        for event in events:
            event_counts[event.event_number] = event_counts.get(event.event_number, 0) + 1
        
        return {
            'total_events': len(events),
            'total_deduction': total_deduction,
            'event_counts': event_counts,
            'uploaded_count': sum(1 for e in events if e.uploaded),
            'pending_count': sum(1 for e in events if not e.uploaded)
        }

class UploadQueueHelper:
    """上傳佇列管理"""
    
    @staticmethod
    def add_to_queue(trip_id: int, task_type: str, task_data: Dict, priority: int = 5):
        """新增任務到上傳佇列"""
        from models import UploadQueue
        
        task = UploadQueue(
            trip_id=trip_id,
            task_type=task_type,
            task_data=task_data,
            priority=priority,
            status='pending',
            retry_count=0,
            created_at=datetime.now()
        )
        db.session.add(task)
        db.session.commit()
        return task