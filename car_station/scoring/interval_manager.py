# scoring/interval_manager.py
"""
15分鐘區間管理器
自動建立、結算區間評分
"""

import threading
import time
from datetime import datetime, timedelta
from models import db, ScoringInterval, EventLog, EventRule
import json

class IntervalManager:
    """15分鐘區間管理器"""
    
    def __init__(self, trip_id, interval_minutes=15):
        """
        初始化區間管理器
        
        Args:
            trip_id: 行程 ID
            interval_minutes: 區間長度（分鐘）
        """
        self.trip_id = trip_id
        self.interval_minutes = interval_minutes
        self.interval_seconds = interval_minutes * 60
        
        # 當前區間
        self.current_interval = None
        self.interval_number = 0
        
        # 執行緒控制
        self.is_running = False
        self.timer_thread = None
        
        # 事件規則快取
        self.event_rules = {}
        self._load_event_rules()
    
    def _load_event_rules(self):
        """載入事件規則"""
        try:
            from flask import current_app
            with current_app.app_context():
                rules = EventRule.query.filter_by(is_active=True).all()
                for rule in rules:
                    self.event_rules[rule.rule_id] = rule.to_dict()
        except Exception as e:
            print(f"[IntervalManager] 載入規則失敗: {e}")
    
    def start(self):
        """啟動區間管理"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # 建立第一個區間
        self._create_new_interval()
        
        # 啟動計時器執行緒
        self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.timer_thread.start()
        
        print(f"[IntervalManager] 區間管理已啟動 (Trip {self.trip_id}, 每 {self.interval_minutes} 分鐘)")
    
    def stop(self):
        """停止區間管理"""
        self.is_running = False
        
        # 結算最後一個區間
        if self.current_interval:
            self._close_current_interval()
        
        if self.timer_thread:
            self.timer_thread.join(timeout=3)
        
        print(f"[IntervalManager] 區間管理已停止")
    
    def _create_new_interval(self):
        """建立新區間"""
        try:
            from flask import current_app
            with current_app.app_context():
                self.interval_number += 1
                
                interval = ScoringInterval.create_new_interval(
                    trip_id=self.trip_id,
                    interval_number=self.interval_number,
                    start_time=datetime.now()
                )
                
                self.current_interval = interval
                print(f"[IntervalManager] 建立區間 {self.interval_number} (ID: {interval.id})")
                
        except Exception as e:
            print(f"[IntervalManager] 建立區間失敗: {e}")
    
    def _close_current_interval(self):
        """結算當前區間"""
        if not self.current_interval:
            return
        
        try:
            from flask import current_app
            with current_app.app_context():
                interval_id = self.current_interval.id
                
                # 重新查詢（避免 detached 問題）
                interval = ScoringInterval.query.get(interval_id)
                if not interval:
                    return
                
                # 設定結束時間
                interval.interval_end = datetime.now()
                
                # 取得此區間的所有事件
                events = EventLog.query.filter(
                    EventLog.trip_id == self.trip_id,
                    EventLog.timestamp >= interval.interval_start,
                    EventLog.timestamp <= interval.interval_end
                ).all()
                
                # 分類事件
                inside_events = {}
                outside_events = {}
                
                for event in events:
                    rule = self.event_rules.get(event.event_code)
                    if not rule:
                        continue
                    
                    event_dict = {
                        'rule_id': event.event_code,
                        'description': event.event_description,
                        'timestamp': event.timestamp.isoformat(),
                        'deduction': event.deduction_points,
                        'confidence': event.confidence_score
                    }
                    
                    if rule['category'] == 'inside':
                        if event.event_code not in inside_events:
                            inside_events[event.event_code] = []
                        inside_events[event.event_code].append(event_dict)
                    else:
                        if event.event_code not in outside_events:
                            outside_events[event.event_code] = []
                        outside_events[event.event_code].append(event_dict)
                
                # 計算扣分
                inside_deduction = sum(
                    event.deduction_points for event in events
                    if self.event_rules.get(event.event_code, {}).get('category') == 'inside'
                )
                
                outside_deduction = sum(
                    event.deduction_points for event in events
                    if self.event_rules.get(event.event_code, {}).get('category') == 'outside'
                )
                
                # 更新分數
                interval.inside_score = max(0, 100 + inside_deduction)  # deduction 是負數
                interval.outside_score = max(0, 100 + outside_deduction)
                
                # 統計事件數量
                interval.inside_event_count = len([e for e in events if self.event_rules.get(e.event_code, {}).get('category') == 'inside'])
                interval.outside_event_count = len([e for e in events if self.event_rules.get(e.event_code, {}).get('category') == 'outside'])
                
                # 判斷是否不及格
                interval.is_failed = interval.inside_score < 60 or interval.outside_score < 60
                interval.is_completed = True
                
                # 儲存事件詳情
                interval.inside_events = json.dumps(inside_events, ensure_ascii=False)
                interval.outside_events = json.dumps(outside_events, ensure_ascii=False)
                
                db.session.commit()
                
                print(f"[IntervalManager] 區間 {self.interval_number} 結算完成:")
                print(f"  車內評分: {interval.inside_score} 分 ({interval.inside_event_count} 事件)")
                print(f"  車外評分: {interval.outside_score} 分 ({interval.outside_event_count} 事件)")
                print(f"  狀態: {'不及格 ❌' if interval.is_failed else '及格 ✅'}")
                
        except Exception as e:
            print(f"[IntervalManager] 結算區間失敗: {e}")
            import traceback
            traceback.print_exc()
    
    def _timer_loop(self):
        """計時器迴圈"""
        start_time = time.time()
        
        while self.is_running:
            elapsed = time.time() - start_time
            
            if elapsed >= self.interval_seconds:
                # 時間到，結算當前區間
                print(f"[IntervalManager] {self.interval_minutes} 分鐘已到，結算區間...")
                self._close_current_interval()
                
                # 建立新區間
                self._create_new_interval()
                
                # 重設計時器
                start_time = time.time()
            
            # 每秒檢查一次
            time.sleep(1)
    
    def get_current_interval_info(self):
        """取得當前區間資訊"""
        if not self.current_interval:
            return None
        
        elapsed = (datetime.now() - self.current_interval.interval_start).total_seconds()
        remaining = max(0, self.interval_seconds - elapsed)
        
        return {
            'interval_number': self.interval_number,
            'start_time': self.current_interval.interval_start.isoformat(),
            'elapsed_seconds': int(elapsed),
            'remaining_seconds': int(remaining),
            'progress_percent': round((elapsed / self.interval_seconds) * 100, 1)
        }