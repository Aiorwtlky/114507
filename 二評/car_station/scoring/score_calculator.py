# scoring/score_calculator.py
"""
評分計算器
計算最終行程評分
"""

from models import db, Trip, ScoringInterval
import json

class ScoreCalculator:
    """評分計算器"""
    
    @staticmethod
    def calculate_trip_score(trip_id):
        """
        計算行程最終評分
        
        評分規則：
        1. 每個區間有車內、車外分數
        2. 若兩者皆 >= 60，取平均值
        3. 若有任一 < 60，該區間以最低分計
        4. 最終分數 = 所有區間分數平均
        5. 但若有任一區間 < 60，則該區間單獨計入（不平均）
        
        Args:
            trip_id: 行程 ID
        
        Returns:
            dict: {
                'total_score': float,
                'inside_avg': float,
                'outside_avg': float,
                'intervals': list,
                'passed': bool
            }
        """
        intervals = ScoringInterval.query.filter_by(
            trip_id=trip_id,
            is_completed=True
        ).order_by(ScoringInterval.interval_number).all()
        
        if not intervals:
            return {
                'total_score': 100.0,
                'inside_avg': 100.0,
                'outside_avg': 100.0,
                'intervals': [],
                'passed': True
            }
        
        interval_scores = []
        failed_intervals = []
        
        for interval in intervals:
            # 計算該區間的分數
            if interval.inside_score >= 60 and interval.outside_score >= 60:
                # 兩者都及格，取平均
                interval_score = (interval.inside_score + interval.outside_score) / 2
            else:
                # 有一項不及格，取最低分
                interval_score = min(interval.inside_score, interval.outside_score)
                failed_intervals.append(interval.interval_number)
            
            interval_scores.append({
                'number': interval.interval_number,
                'inside': interval.inside_score,
                'outside': interval.outside_score,
                'final': interval_score,
                'failed': interval.is_failed
            })
        
        # 計算平均
        inside_avg = sum(i.inside_score for i in intervals) / len(intervals)
        outside_avg = sum(i.outside_score for i in intervals) / len(intervals)
        
        # 最終分數計算
        if failed_intervals:
            # 有不及格區間，該區間單獨計入
            # 規則：取最低的不及格區間分數
            failed_scores = [s['final'] for s in interval_scores if s['failed']]
            total_score = min(failed_scores)
        else:
            # 全部及格，取平均
            total_score = sum(s['final'] for s in interval_scores) / len(interval_scores)
        
        # 判斷是否及格（總分 >= 80）
        passed = total_score >= 80
        
        return {
            'total_score': round(total_score, 1),
            'inside_avg': round(inside_avg, 1),
            'outside_avg': round(outside_avg, 1),
            'intervals': interval_scores,
            'failed_intervals': failed_intervals,
            'passed': passed
        }
    
    @staticmethod
    def update_trip_score(trip_id):
        """
        更新 Trip 表的分數
        
        Args:
            trip_id: 行程 ID
        """
        try:
            score_result = ScoreCalculator.calculate_trip_score(trip_id)
            
            trip = Trip.query.get(trip_id)
            if trip:
                trip.score = score_result['total_score']
                db.session.commit()
                
                print(f"[ScoreCalculator] Trip {trip_id} 最終評分: {trip.score} 分")
                return score_result
            
        except Exception as e:
            print(f"[ScoreCalculator] 更新評分失敗: {e}")
            db.session.rollback()
            return None