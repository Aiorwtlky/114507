# blueprints/ai_service.py
"""
AI 服務 API
"""

from flask import Blueprint, jsonify, request
from models import db, Trip, ScoringInterval, EventLog
from services.detection_service import DetectionService
from scoring.score_calculator import ScoreCalculator

ai_service_bp = Blueprint('ai_service', __name__)

@ai_service_bp.route('/start/<int:trip_id>', methods=['POST'])
def start_detection(trip_id):
    """啟動行程的 AI 偵測"""
    
    # 檢查行程是否存在
    trip = Trip.query.get(trip_id)
    if not trip:
        return jsonify({
            'success': False,
            'error': '行程不存在'
        }), 404
    
    # 啟動偵測服務
    success = DetectionService.start_trip_detection(trip_id)
    
    if success:
        return jsonify({
            'success': True,
            'message': 'AI 偵測已啟動',
            'trip_id': trip_id
        })
    else:
        return jsonify({
            'success': False,
            'error': '啟動失敗'
        }), 500

@ai_service_bp.route('/stop/<int:trip_id>', methods=['POST'])
def stop_detection(trip_id):
    """停止行程的 AI 偵測"""
    
    DetectionService.stop_trip_detection(trip_id)
    
    return jsonify({
        'success': True,
        'message': 'AI 偵測已停止',
        'trip_id': trip_id
    })

@ai_service_bp.route('/status/<int:trip_id>', methods=['GET'])
def get_detection_status(trip_id):
    """取得 AI 偵測狀態"""
    
    service = DetectionService.get_trip_service(trip_id)
    
    if not service:
        return jsonify({
            'success': False,
            'error': '服務未啟動'
        }), 404
    
    status = service.get_status()
    
    return jsonify({
        'success': True,
        'data': status
    })

@ai_service_bp.route('/update_gpio/<int:trip_id>', methods=['POST'])
def update_gpio(trip_id):
    """更新 GPIO 狀態（內部 API，由 GPIO 輪詢呼叫）"""
    
    data = request.json
    
    DetectionService.update_trip_gpio(
        trip_id=trip_id,
        left_turn=data.get('left_turn', False),
        right_turn=data.get('right_turn', False),
        speed=data.get('speed', 0)
    )
    
    return jsonify({'success': True})

@ai_service_bp.route('/current_interval/<int:trip_id>', methods=['GET'])
def get_current_interval(trip_id):
    """取得當前區間資訊"""
    
    service = DetectionService.get_trip_service(trip_id)
    
    if not service or not service.interval_manager:
        return jsonify({
            'success': False,
            'error': '服務未啟動'
        }), 404
    
    interval_info = service.interval_manager.get_current_interval_info()
    
    return jsonify({
        'success': True,
        'data': interval_info
    })

@ai_service_bp.route('/score/<int:trip_id>', methods=['GET'])
def get_trip_score(trip_id):
    """取得行程評分"""
    
    score_result = ScoreCalculator.calculate_trip_score(trip_id)
    
    return jsonify({
        'success': True,
        'data': score_result
    })

@ai_service_bp.route('/events/<int:trip_id>', methods=['GET'])
def get_trip_events(trip_id):
    """取得行程的所有事件"""
    
    limit = request.args.get('limit', 10, type=int)
    
    events = EventLog.query.filter_by(trip_id=trip_id)\
        .order_by(EventLog.timestamp.desc())\
        .limit(limit)\
        .all()
    
    event_list = [{
        'id': e.id,
        'event_code': e.event_code,
        'description': e.event_description,
        'timestamp': e.timestamp.isoformat(),
        'deduction_points': e.deduction_points,
        'confidence': e.confidence_score
    } for e in events]
    
    return jsonify({
        'success': True,
        'data': event_list
    })

@ai_service_bp.route('/intervals/<int:trip_id>', methods=['GET'])
def get_trip_intervals(trip_id):
    """取得行程的所有區間評分"""
    
    intervals = ScoringInterval.query.filter_by(trip_id=trip_id)\
        .order_by(ScoringInterval.interval_number)\
        .all()
    
    interval_list = [interval.to_dict() for interval in intervals]
    
    return jsonify({
        'success': True,
        'data': interval_list
    })