# blueprints/trip.py（修正版）
from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from models import db, Trip, Personnel, VehicleDevice, GPIOLog, EventLog, VideoRecord  # 移除 RouteLog
from datetime import datetime
import os
import json
import threading

trip_bp = Blueprint('trip', __name__)

@trip_bp.route('/start')
def start_trip():
    """開始行程頁面"""
    # 檢查是否有進行中的行程
    active_trip = Trip.query.filter_by(status='進行中').first()
    
    if active_trip:
        # 如果有進行中的行程，跳轉到行程監控頁面
        return redirect(url_for('trip.trip_monitor', trip_id=active_trip.id))
    
    return render_template('trip/start.html')

@trip_bp.route('/monitor/<int:trip_id>')
def trip_monitor(trip_id):
    """行程監控頁面"""
    trip = Trip.query.get_or_404(trip_id)
    
    if trip.status != '進行中':
        return redirect(url_for('trip.start_trip'))
    
    return render_template('trip/monitor.html', trip=trip)

@trip_bp.route('/api/start_trip', methods=['POST'])
def api_start_trip():
    """API: 開始行程（模擬刷卡）"""
    try:
        # 檢查是否有進行中的行程
        active_trip = Trip.query.filter_by(status='進行中').first()
        if active_trip:
            return jsonify({
                "status": "error",
                "message": "已有進行中的行程",
                "trip_id": active_trip.id
            }), 400
        
        # 取得測試駕駛員
        test_personnel = Personnel.query.filter_by(personnel_number="TEST001").first()
        if not test_personnel:
            return jsonify({
                "status": "error",
                "message": "找不到測試駕駛員"
            }), 404
        
        # 建立新行程
        trip = Trip.create_new_trip(
            personnel_id=test_personnel.id,
            trip_name=f"測試行程 {datetime.now().strftime('%H:%M')}"
        )
        
        # 更新行程狀態為進行中
        trip.status = '進行中'
        trip.start_time = datetime.now()
        
        # 建立儲存目錄
        storage_base = f"trip_data/{trip.trip_number}"
        os.makedirs(storage_base, exist_ok=True)
        os.makedirs(f"{storage_base}/videos", exist_ok=True)
        
        trip.video_storage_path = f"{storage_base}/videos"
        trip.data_storage_path = f"{storage_base}/data"
        
        db.session.commit()
        
        # 🎬 自動開始錄影
        from blueprints.video import record_camera_worker, recording_status, recording_threads
        from flask import current_app
        
        print(f"🎬 開始行程錄影: {trip.trip_number}")
        
        # 啟動雙鏡頭錄影
        for camera_position in ['inside', 'outside']:
            if not recording_status[camera_position]:
                thread = threading.Thread(
                    target=record_camera_worker,
                    args=(current_app._get_current_object(), trip.id, camera_position),
                    daemon=True
                )
                thread.start()
                recording_threads[camera_position] = thread
                print(f"📹 啟動 {camera_position} 鏡頭錄影")
        
        # 🤖 啟動 AI 偵測服務
        try:
            from services.detection_service import DetectionService
            ai_started = DetectionService.start_trip_detection(trip.id)
            ai_status = "已啟動" if ai_started else "啟動失敗"
            print(f"🤖 AI 偵測服務: {ai_status}")
        except Exception as e:
            print(f"⚠️ AI 服務啟動失敗: {e}")
            ai_status = f"啟動失敗: {str(e)}"
        
        return jsonify({
            "status": "success",
            "message": "行程已開始",
            "trip_id": trip.id,
            "trip_number": trip.trip_number,
            "driver_name": test_personnel.name,
            "start_time": trip.start_time.isoformat(),
            "recording": "已啟動雙鏡頭錄影",
            "ai_detection": ai_status
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"開始行程失敗：{str(e)}"
        }), 500

@trip_bp.route('/api/end_trip', methods=['POST'])
def api_end_trip():
    """API: 結束行程（模擬刷卡）"""
    try:
        # 找到進行中的行程
        active_trip = Trip.query.filter_by(status='進行中').first()
        if not active_trip:
            return jsonify({
                "status": "error",
                "message": "沒有進行中的行程"
            }), 404
        
        # 🤖 停止 AI 偵測服務
        try:
            from services.detection_service import DetectionService
            DetectionService.stop_trip_detection(active_trip.id)
            print(f"🤖 AI 偵測服務已停止")
        except Exception as e:
            print(f"⚠️ AI 服務停止失敗: {e}")
        
        # 結束行程
        active_trip.status = '已完成'
        active_trip.end_time = datetime.now()
        
        # 🛑 停止錄影
        from blueprints.video import recording_status
        
        print(f"🛑 停止行程錄影: {active_trip.trip_number}")
        
        stopped_cameras = []
        for camera_position in ['inside', 'outside']:
            if recording_status[camera_position]:
                recording_status[camera_position] = False
                stopped_cameras.append(camera_position)
                print(f"📹 停止 {camera_position} 鏡頭錄影")
        
        # 等待錄影線程完成並強制更新影片狀態
        import time
        time.sleep(2)
        
        # 強制更新該行程的所有影片記錄狀態
        from models import VideoRecord
        incomplete_videos = VideoRecord.query.filter_by(
            trip_id=active_trip.id,
            recording_status='recording'
        ).all()
        
        for video in incomplete_videos:
            print(f"📄 強制更新影片狀態: {video.video_number}")
            
            if video.file_path and os.path.exists(video.file_path):
                file_size = os.path.getsize(video.file_path)
                video.file_size = file_size
                
                if file_size > 0:
                    video.recording_status = 'completed'
                    video.end_time = active_trip.end_time
                    print(f"✅ 影片 {video.video_number} 標記為完成")
                else:
                    video.recording_status = 'failed'
                    video.end_time = active_trip.end_time
                    print(f"❌ 影片 {video.video_number} 標記為失敗（檔案為空）")
            else:
                video.recording_status = 'failed'
                video.end_time = active_trip.end_time
                video.file_size = 0
                print(f"❌ 影片 {video.video_number} 標記為失敗（檔案不存在）")
        
        # 計算行程時長
        if active_trip.start_time:
            duration = (active_trip.end_time - active_trip.start_time).total_seconds()
        else:
            duration = 0
        
        # 提交所有變更
        db.session.commit()
        
        print(f"✅ 行程完成: {active_trip.trip_number} (時長: {int(duration)}秒)")
        print(f"📄 已更新 {len(incomplete_videos)} 個影片記錄狀態")
        
        return jsonify({
            "status": "success",
            "message": "行程已結束",
            "trip_id": active_trip.id,
            "trip_number": active_trip.trip_number,
            "duration_seconds": duration,
            "end_time": active_trip.end_time.isoformat(),
            "stopped_cameras": stopped_cameras,
            "updated_videos": len(incomplete_videos)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"結束行程失敗：{str(e)}"
        }), 500

@trip_bp.route('/api/trip_status')
def api_trip_status():
    """API: 取得當前行程狀態"""
    active_trip = Trip.query.filter_by(status='進行中').first()
    
    if active_trip:
        # 計算行程時長
        if active_trip.start_time:
            duration = (datetime.now() - active_trip.start_time).total_seconds()
        else:
            duration = 0
            
        return jsonify({
            "status": "active",
            "trip": active_trip.to_dict(),
            "duration_seconds": duration,
            "driver_name": active_trip.personnel.name if active_trip.personnel else "未知"
        })
    else:
        return jsonify({
            "status": "inactive",
            "message": "沒有進行中的行程"
        })

@trip_bp.route('/api/add_event', methods=['POST'])
def api_add_event():
    """API: 新增評分事件（模擬按鈕）"""
    try:
        data = request.get_json()
        event_code = data.get('event_code')
        
        # 事件定義（更新為新的規則）
        event_definitions = {
            'A01': {'description': '重度疲勞（閉眼5秒以上）', 'points': 40},
            'A02': {'description': '中度疲勞（閉眼3-5秒）', 'points': 30},
            'A03': {'description': '使用手機', 'points': 15},
            'A04': {'description': '注意力分散（臉部離開畫面）', 'points': 40},
            'B01': {'description': '切換車道未打方向燈', 'points': 15},
            'B02': {'description': '轉彎未打方向燈', 'points': 15},
            'B03': {'description': '未保持安全距離', 'points': 15}
        }
        
        if event_code not in event_definitions:
            return jsonify({
                "status": "error",
                "message": "未知的事件代碼"
            }), 400
        
        # 找到進行中的行程
        active_trip = Trip.query.filter_by(status='進行中').first()
        if not active_trip:
            return jsonify({
                "status": "error",
                "message": "沒有進行中的行程"
            }), 404
        
        # 新增事件記錄
        event = EventLog(
            trip_id=active_trip.id,
            event_code=event_code,
            event_description=event_definitions[event_code]['description'],
            timestamp=datetime.now(),
            deduction_points=-event_definitions[event_code]['points'],  # 負數表示扣分
            detection_method='manual'
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": f"已記錄事件：{event.event_description}",
            "event": {
                "code": event_code,
                "description": event.event_description,
                "points": event.deduction_points,
                "timestamp": event.timestamp.isoformat()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"新增事件失敗：{str(e)}"
        }), 500

@trip_bp.route('/history')
def trip_history():
    """過往行程頁面"""
    # 取得所有已完成的行程，按建立時間降序排列
    completed_trips = Trip.query.filter(
        Trip.status.in_(['已完成', '已上傳'])
    ).order_by(Trip.created_at.desc()).all()
    
    # 計算尚未計算分數的行程
    for trip in completed_trips:
        if trip.score is None:
            # 使用新的評分系統計算
            try:
                from scoring.score_calculator import ScoreCalculator
                score_result = ScoreCalculator.calculate_trip_score(trip.id)
                trip.score = score_result['total_score']
            except:
                # 若評分系統失敗，使用舊方法
                total_deduction = db.session.query(db.func.sum(EventLog.deduction_points)).filter_by(trip_id=trip.id).scalar() or 0
                trip.score = max(0, 100 + total_deduction)  # total_deduction 是負數
    
    db.session.commit()
    
    return render_template('trip/history.html', trips=completed_trips)

@trip_bp.route('/api/trip_summary/<int:trip_id>')
def api_trip_summary(trip_id):
    """API: 行程總結"""
    trip = Trip.query.get_or_404(trip_id)
    
    # 使用新的評分系統
    try:
        from scoring.score_calculator import ScoreCalculator
        score_result = ScoreCalculator.calculate_trip_score(trip_id)
        score = score_result['total_score']
        intervals = score_result.get('intervals', [])
    except:
        # 若評分系統失敗，使用舊方法
        total_deduction = db.session.query(db.func.sum(EventLog.deduction_points)).filter_by(trip_id=trip_id).scalar() or 0
        score = max(0, 100 + total_deduction)
        intervals = []
    
    # 更新行程評分
    trip.score = score
    db.session.commit()
    
    # 取得事件記錄
    events = EventLog.query.filter_by(trip_id=trip_id).all()
    
    # 取得 GPIO 記錄統計
    gpio_stats = {
        'left_turn_count': GPIOLog.query.filter_by(trip_id=trip_id, gpio_type='left_turn', action='on').count(),
        'right_turn_count': GPIOLog.query.filter_by(trip_id=trip_id, gpio_type='right_turn', action='on').count(),
        'reverse_count': GPIOLog.query.filter_by(trip_id=trip_id, gpio_type='reverse', action='on').count()
    }
    
    # 取得影片資訊
    videos = VideoRecord.query.filter_by(trip_id=trip_id).all()
    video_info = []
    
    for video in videos:
        file_exists = os.path.exists(video.file_path) if video.file_path else False
        duration = 0
        if video.start_time and video.end_time:
            duration = (video.end_time - video.start_time).total_seconds()
        
        file_size_mb = (video.file_size / 1024 / 1024) if video.file_size else 0
        
        video_info.append({
            "camera": video.camera_position,
            "duration": int(duration),
            "size_mb": round(file_size_mb, 2),
            "exists": file_exists,
            "path": video.file_path,
            "status": video.recording_status
        })
    
    return jsonify({
        "trip": trip.to_dict(),
        "score": score,
        "intervals": intervals,  # 15分鐘區間評分
        "events": [
            {
                "code": event.event_code,
                "description": event.event_description,
                "points": event.deduction_points,
                "timestamp": event.timestamp.isoformat(),
                "method": event.detection_method
            } for event in events
        ],
        "gpio_stats": gpio_stats,
        "videos": video_info,
        "duration_seconds": (trip.end_time - trip.start_time).total_seconds() if trip.end_time and trip.start_time else 0
    })