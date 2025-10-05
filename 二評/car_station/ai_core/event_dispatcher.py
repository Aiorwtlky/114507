# ai_core/event_dispatcher.py
"""
事件分發器
將 AI 偵測結果寫入資料庫，支援批次寫入
"""

import threading
import time
from queue import Queue
from datetime import datetime
from models import db, EventLog, AIDetectionResult, EventRule
import json

class EventDispatcher:
    """事件分發器 - 將偵測結果寫入資料庫"""
    
    def __init__(self, trip_id, batch_size=10, batch_interval=5.0):
        """
        初始化事件分發器
        
        Args:
            trip_id: 行程 ID
            batch_size: 批次大小（累積多少事件後寫入）
            batch_interval: 批次間隔（秒，超過時間強制寫入）
        """
        self.trip_id = trip_id
        self.batch_size = batch_size
        self.batch_interval = batch_interval
        
        # 事件佇列
        self.event_queue = Queue()
        
        # 批次緩存
        self.event_batch = []
        self.last_batch_time = time.time()
        
        # 執行緒控制
        self.is_running = False
        self.dispatch_thread = None
        
        # 事件去重（3秒內相同事件只記錄一次）
        self.recent_events = {}  # {rule_id: last_timestamp}
        self.dedup_window = 3.0  # 秒
        
        # 統計
        self.total_events = 0
        self.deduplicated_events = 0
        self.written_events = 0
        
        # 載入事件規則
        self.event_rules = self._load_event_rules()
    
    def _load_event_rules(self):
        """載入事件規則"""
        rules = {}
        try:
            from flask import current_app
            with current_app.app_context():
                rule_records = EventRule.query.filter_by(is_active=True).all()
                for rule in rule_records:
                    rules[rule.rule_id] = rule.to_dict()
        except:
            print("[EventDispatcher] 無法載入事件規則，使用預設值")
        
        return rules
    
    def start(self):
        """啟動分發執行緒"""
        if self.is_running:
            return
        
        self.is_running = True
        self.dispatch_thread = threading.Thread(target=self._dispatch_loop, daemon=True)
        self.dispatch_thread.start()
        print(f"[EventDispatcher] 事件分發執行緒已啟動 (Trip ID: {self.trip_id})")
    
    def stop(self):
        """停止分發執行緒"""
        self.is_running = False
        
        # 寫入剩餘事件
        if self.event_batch:
            self._flush_batch()
        
        if self.dispatch_thread:
            self.dispatch_thread.join(timeout=3)
        
        print(f"[EventDispatcher] 事件分發執行緒已停止")
        print(f"  總事件: {self.total_events}")
        print(f"  去重: {self.deduplicated_events}")
        print(f"  寫入: {self.written_events}")
    
    def dispatch_event(self, event_data):
        """
        分發事件
        
        Args:
            event_data: {
                'rule_id': 'A01',
                'timestamp': datetime,
                'confidence': 0.85,
                'detection_data': {...}
            }
        """
        try:
            self.event_queue.put(event_data, block=False)
            self.total_events += 1
        except:
            print("[EventDispatcher] 事件佇列已滿，丟棄事件")
    
    def _dispatch_loop(self):
        """分發迴圈"""
        while self.is_running:
            try:
                # 取得事件
                event_data = self.event_queue.get(timeout=0.5)
                
                # 檢查去重
                if self._should_deduplicate(event_data):
                    self.deduplicated_events += 1
                    continue
                
                # 加入批次
                self.event_batch.append(event_data)
                
                # 檢查是否需要寫入
                should_flush = (
                    len(self.event_batch) >= self.batch_size or
                    (time.time() - self.last_batch_time) >= self.batch_interval
                )
                
                if should_flush:
                    self._flush_batch()
                
            except:
                # 超時，檢查是否需要強制寫入
                if self.event_batch and (time.time() - self.last_batch_time) >= self.batch_interval:
                    self._flush_batch()
    
    def _should_deduplicate(self, event_data):
        """檢查是否需要去重"""
        rule_id = event_data.get('rule_id')
        timestamp = event_data.get('timestamp', datetime.now())
        
        if rule_id in self.recent_events:
            last_time = self.recent_events[rule_id]
            time_diff = (timestamp - last_time).total_seconds()
            
            if time_diff < self.dedup_window:
                return True  # 需要去重
        
        # 更新最後發生時間
        self.recent_events[rule_id] = timestamp
        return False
    
    def _flush_batch(self):
        """寫入批次事件到資料庫"""
        if not self.event_batch:
            return
        
        try:
            from flask import current_app
            with current_app.app_context():
                for event in self.event_batch:
                    self._write_event(event)
                
                db.session.commit()
                self.written_events += len(self.event_batch)
                print(f"[EventDispatcher] 寫入 {len(self.event_batch)} 個事件")
        
        except Exception as e:
            print(f"[EventDispatcher] 寫入失敗: {e}")
            db.session.rollback()
        
        finally:
            self.event_batch = []
            self.last_batch_time = time.time()
    
    def _write_event(self, event_data):
        """寫入單一事件"""
        rule_id = event_data.get('rule_id')
        rule = self.event_rules.get(rule_id)
        
        if not rule:
            print(f"[EventDispatcher] 未知規則: {rule_id}")
            return
        
        # 寫入事件記錄
        event_log = EventLog(
            trip_id=self.trip_id,
            event_code=rule_id,
            event_description=rule['event_name'],
            timestamp=event_data.get('timestamp', datetime.now()),
            confidence_score=event_data.get('confidence'),
            deduction_points=rule['deduction_points'],
            detection_method='ai'
        )
        db.session.add(event_log)
        db.session.flush()  # 取得 event_log.id
        
        # 寫入 AI 偵測詳情
        ai_detection = AIDetectionResult(
            trip_id=self.trip_id,
            timestamp=event_data.get('timestamp', datetime.now()),
            camera_type=rule['category'],
            detection_type=rule_id,
            detection_data=json.dumps(event_data.get('detection_data', {}), ensure_ascii=False),
            event_id=event_log.id
        )
        db.session.add(ai_detection)
    
    def get_status(self):
        """取得分發器狀態"""
        return {
            'trip_id': self.trip_id,
            'is_running': self.is_running,
            'total_events': self.total_events,
            'deduplicated_events': self.deduplicated_events,
            'written_events': self.written_events,
            'pending_events': self.event_queue.qsize(),
            'batch_size': len(self.event_batch)
        }