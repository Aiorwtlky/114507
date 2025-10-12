# core/score_calculator.py
"""
評分計算模組
根據 PDF 規則計算駕駛評分
"""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from database.models import AIEvent, IntervalScore, get_event_info


class ScoreCalculator:
    def __init__(self):
        """初始化評分計算器"""
        self.INTERVAL_DURATION = 15  # 15 分鐘為一個區間
        self.BASE_SCORE = 100  # 基礎分數
        self.MAX_DEDUCTION_PER_INTERVAL = 100  # 每個區間最多扣 100 分
    
    def calculate_trip_score(self, events: List[Dict], trip_start: datetime, trip_end: datetime) -> Dict:
        """
        計算整趟行程的評分
        
        Args:
            events: AI 事件列表
            trip_start: 行程開始時間
            trip_end: 行程結束時間
        
        Returns:
            包含總分、A類分數、B類分數、建議的字典
        """
        # 1. 將行程分割成 15 分鐘區間
        intervals = self._create_intervals(trip_start, trip_end)
        
        # 2. 將事件分配到對應的區間
        interval_events = self._assign_events_to_intervals(events, intervals)
        
        # 3. 計算每個區間的 A、B 類扣分
        interval_scores = []
        for interval_num, (start, end) in enumerate(intervals, 1):
            events_in_interval = interval_events.get(interval_num, [])
            
            a_deductions, b_deductions = self._calculate_interval_deductions(events_in_interval)
            
            # 每個區間最多扣 100 分
            a_deductions = min(a_deductions, self.MAX_DEDUCTION_PER_INTERVAL)
            b_deductions = min(b_deductions, self.MAX_DEDUCTION_PER_INTERVAL)
            
            # 計算區間分數
            a_score = self.BASE_SCORE - a_deductions
            b_score = self.BASE_SCORE - b_deductions
            
            interval_scores.append({
                'interval_number': interval_num,
                'start_time': start,
                'end_time': end,
                'category_a_deductions': a_deductions,
                'category_b_deductions': b_deductions,
                'category_a_score': a_score,
                'category_b_score': b_score
            })
        
        # 4. 計算總分（所有區間的平均）
        if interval_scores:
            avg_a_score = sum(i['category_a_score'] for i in interval_scores) / len(interval_scores)
            avg_b_score = sum(i['category_b_score'] for i in interval_scores) / len(interval_scores)
            total_score = (avg_a_score + avg_b_score) / 2
        else:
            avg_a_score = avg_b_score = total_score = self.BASE_SCORE
        
        # 5. 生成 AI 建議
        ai_suggestion = self._generate_suggestion(events, avg_a_score, avg_b_score)
        
        return {
            'score': round(total_score, 2),
            'in_car_score': round(avg_a_score, 2),
            'out_car_score': round(avg_b_score, 2),
            'ai_suggestion': ai_suggestion,
            'intervals': interval_scores
        }
    
    def _create_intervals(self, start: datetime, end: datetime) -> List[Tuple[datetime, datetime]]:
        """
        將行程時間分割成 15 分鐘區間
        
        Returns:
            [(start1, end1), (start2, end2), ...]
        """
        intervals = []
        current_start = start
        
        while current_start < end:
            current_end = min(current_start + timedelta(minutes=self.INTERVAL_DURATION), end)
            intervals.append((current_start, current_end))
            current_start = current_end
        
        return intervals
    
    def _assign_events_to_intervals(self, events: List[Dict], intervals: List[Tuple[datetime, datetime]]) -> Dict[int, List[Dict]]:
        """
        將事件分配到對應的區間
        
        Returns:
            {interval_number: [event1, event2, ...]}
        """
        interval_events = {}
        
        for event in events:
            # 解析事件時間
            if isinstance(event['timestamp'], str):
                event_time = datetime.fromisoformat(event['timestamp'])
            else:
                event_time = event['timestamp']
            
            # 找到對應的區間
            for interval_num, (start, end) in enumerate(intervals, 1):
                if start <= event_time < end:
                    if interval_num not in interval_events:
                        interval_events[interval_num] = []
                    interval_events[interval_num].append(event)
                    break
        
        return interval_events
    
    def _calculate_interval_deductions(self, events: List[Dict]) -> Tuple[int, int]:
        """
        計算單一區間的 A、B 類扣分
        
        Returns:
            (a_deductions, b_deductions)
        """
        a_deductions = 0
        b_deductions = 0
        
        for event in events:
            event_code = event.get('event_code', '')
            deduction = event.get('deduction_points', 0)
            
            if event_code.startswith('A'):
                a_deductions += deduction
            elif event_code.startswith('B'):
                b_deductions += deduction
        
        return a_deductions, b_deductions
    
    def _generate_suggestion(self, events: List[Dict], a_score: float, b_score: float) -> str:
        """
        根據事件和分數生成 AI 建議
        
        Returns:
            建議文字
        """
        suggestions = []
        
        # 統計各類事件
        event_counts = {}
        for event in events:
            code = event.get('event_code', 'UNKNOWN')
            event_counts[code] = event_counts.get(code, 0) + 1
        
        # A 類建議
        if a_score < 70:
            suggestions.append("⚠️ 車內行為需要改善：")
            if event_counts.get('A01', 0) > 0 or event_counts.get('A02', 0) > 0:
                suggestions.append("  - 請注意休息，避免疲勞駕駛")
            if event_counts.get('A03', 0) > 0:
                suggestions.append("  - 請勿使用手機")
            if event_counts.get('A04', 0) > 0 or event_counts.get('A05', 0) > 0:
                suggestions.append("  - 請保持專注，視線不要長時間離開前方")
        elif a_score < 85:
            suggestions.append("✓ 車內行為良好，但仍有改善空間")
        else:
            suggestions.append("✓ 車內行為優秀！")
        
        # B 類建議
        if b_score < 70:
            suggestions.append("\n⚠️ 車外行為需要改善：")
            if event_counts.get('B01', 0) > 0 or event_counts.get('B02', 0) > 0:
                suggestions.append("  - 變換車道或轉彎時請記得打方向燈")
            if event_counts.get('B03', 0) > 0:
                suggestions.append("  - 請保持安全車距，避免追撞風險")
        elif b_score < 85:
            suggestions.append("\n✓ 車外行為良好，但仍有改善空間")
        else:
            suggestions.append("\n✓ 車外行為優秀！")
        
        # 總評
        if a_score >= 85 and b_score >= 85:
            suggestions.append("\n🎉 整體表現優異，繼續保持！")
        
        return '\n'.join(suggestions) if suggestions else "表現良好，繼續保持安全駕駛。"