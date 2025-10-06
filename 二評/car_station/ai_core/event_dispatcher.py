# ai_core/event_dispatcher.py（完整修正版，內建規則定義）
"""
事件分發器
負責將 AI 偵測到的事件寫入資料庫
"""

import threading
import time
from queue import Queue, Empty
from datetime import datetime

class EventDispatcher:
    """事件分發器"""
    
    # 內建規則定義
    RULES = {
        'A01': {'description': '重度疲勞（閉眼5秒以上）', 'points': -40},
        'A02': {'description': '中度疲勞（閉眼3-5秒）', 'points': -30},
        'A03': {'description': '使用手機', 'points': -15},
        'A04': {'description': '注意力分散（臉部離開畫面）', 'points': -40},
        'B01': {'description': '切換車道未打方向燈', 'points': -15},
        'B02': {'description': '轉彎未打方向燈', 'points': -15},
        'B03': {'description': '未保持安全距離', 'points': -15}
    }
    
    def __init__(self, trip_id, app):
        self.trip_id = trip_id
        self.app = app
        self.event_queue = Queue(maxsize=100)
        self.is_running = False
        self.dispatch_thread = None
    
    def start(self):
        """啟動事件分發執行緒"""
        if self.is_running:
            return
        
        self.is_running = True
        self.dispatch_thread = threading.Thread(target=self._dispatch_loop, daemon=True)
        self.dispatch_thread.start()
        print(f"[EventDispatcher] 事件分發執行緒已啟動 (Trip ID: {self.trip_id})")
    
    def stop(self):
        """停止事件分發"""
        self.is_running = False
        if self.dispatch_thread:
            self.dispatch_thread.join(timeout=2)
    
    def dispatch_event(self, event_data):
        """分發事件到佇列"""
        try:
            self.event_queue.put(event_data, block=False)
        except:
            print(f"[EventDispatcher] 佇列已滿，丟棄事件")
    
    def _dispatch_loop(self):
        """事件分發迴圈"""
        while self.is_running:
            try:
                event_data = self.event_queue.get(timeout=0.5)
                
                # 使用 Flask app context
                with self.app.app_context():
                    self._write_to_database(event_data)
                
            except Empty:
                continue
            except Exception as e:
                print(f"[EventDispatcher] 分發錯誤: {e}")
                time.sleep(0.5)
    
    def _write_to_database(self, event_data):
        """寫入資料庫"""
        try:
            from models import db, EventLog
            
            rule_id = event_data['rule_id']
            rule_info = self.RULES.get(rule_id)
            
            if not rule_info:
                print(f"[EventDispatcher] 未知的規則: {rule_id}")
                return
            
            event = EventLog(
                trip_id=self.trip_id,
                event_code=rule_id,
                event_description=rule_info['description'],
                timestamp=event_data['timestamp'],
                deduction_points=rule_info['points'],
                detection_method='ai'
            )
            
            db.session.add(event)
            db.session.commit()
            
            print(f"[EventDispatcher] ✅ 事件已記錄: {rule_id} - {rule_info['description']} ({rule_info['points']}分)")
            
        except Exception as e:
            print(f"[EventDispatcher] 寫入失敗: {e}")
            import traceback
            traceback.print_exc()
            try:
                db.session.rollback()
            except:
                pass