# blueprints/video.py
from flask import Blueprint, jsonify, current_app, render_template, Response, request, send_file
import os
import threading
import time
import cv2
import re
from datetime import datetime
from models import db, VideoRecord, Trip
from config import CAMERA_URLS, CAMERA_CONFIG
import uuid

video_bp = Blueprint('video', __name__)

# 全域變數管理錄影狀態
recording_threads = {}
recording_status = {
    'inside': False,
    'outside': False
}

def create_dummy_video_file(file_path, duration_seconds=60):
    """建立模擬影片檔案（開發測試用）"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 建立一個模擬的影片檔案（實際專案中這裡會是真正的錄影邏輯）
        with open(file_path, 'w') as f:
            f.write(f"模擬影片檔案\n")
            f.write(f"建立時間: {datetime.now()}\n")
            f.write(f"模擬時長: {duration_seconds} 秒\n")
            f.write(f"攝影機位置: {os.path.basename(file_path).split('_')[0]}\n")
            
        # 模擬檔案大小（每秒約1MB）
        file_size = duration_seconds * 1024 * 1024
        
        return file_size
    except Exception as e:
        print(f"建立模擬影片檔案失敗: {e}")
        return 0

def record_ip_camera(file_path, camera_position, video_record_id):
    """實際的 IP camera 錄影函數"""
    try:
        camera_url = CAMERA_URLS.get(camera_position)
        if not camera_url:
            print(f"❌ 找不到攝影機 URL: {camera_position}")
            return False
            
        print(f"🎬 嘗試連接 {camera_position} IP camera: {camera_url}")
        
        # OpenCV 錄影設定
        cap = cv2.VideoCapture(camera_url)
        
        # 設定連接參數
        cap.set(cv2.CAP_PROP_BUFFERSIZE, CAMERA_CONFIG['BUFFER_SIZE'])
        cap.set(cv2.CAP_PROP_FPS, CAMERA_CONFIG['FPS'])
        
        if not cap.isOpened():
            print(f"❌ 無法連接攝影機: {camera_url}")
            return False
            
        print(f"✅ 成功連接 {camera_position} 攝影機")
        
        # 讀取第一幀來取得實際解析度
        ret, frame = cap.read()
        if not ret:
            print(f"❌ 無法讀取 {camera_position} 攝影機畫面")
            cap.release()
            return False
            
        # 取得實際畫面尺寸或使用預設值
        if frame is not None:
            height, width = frame.shape[:2]
            frame_size = (width, height)
        else:
            frame_size = (CAMERA_CONFIG['FRAME_WIDTH'], CAMERA_CONFIG['FRAME_HEIGHT'])
            
        print(f"📹 {camera_position} 影片解析度: {frame_size}")
        
        # 設定影片編碼器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 或試試 'XVID'
        fps = CAMERA_CONFIG['FPS']
        
        out = cv2.VideoWriter(file_path, fourcc, fps, frame_size)
        
        if not out.isOpened():
            print(f"❌ 無法建立 {camera_position} 影片寫入器")
            cap.release()
            return False
            
        print(f"🎬 開始錄製 {camera_position} IP camera 到: {file_path}")
        
        frame_count = 0
        last_status_time = time.time()
        
        # 重新讀取第一幀（因為上面已經讀過一次）
        ret, frame = cap.read()
        
        while recording_status[camera_position] and ret:
            try:
                # 調整畫面尺寸（如果需要）
                if frame.shape[:2][::-1] != frame_size:
                    frame = cv2.resize(frame, frame_size)
                
                # 寫入影片
                out.write(frame)
                frame_count += 1
                
                # 每30秒顯示一次進度
                current_time = time.time()
                if current_time - last_status_time >= 30:
                    seconds = frame_count // fps
                    print(f"📹 {camera_position} 已錄製: {seconds}秒 ({frame_count}幀)")
                    last_status_time = current_time
                
                # 讀取下一幀
                ret, frame = cap.read()
                
                if not ret:
                    print(f"⚠️ {camera_position} 讀取畫面失敗，嘗試重新連接...")
                    # 嘗試重新連接
                    cap.release()
                    time.sleep(2)
                    cap = cv2.VideoCapture(camera_url)
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, CAMERA_CONFIG['BUFFER_SIZE'])
                    if cap.isOpened():
                        ret, frame = cap.read()
                        print(f"✅ {camera_position} 重新連接成功")
                    else:
                        print(f"❌ {camera_position} 重新連接失敗")
                        break
                        
            except Exception as e:
                print(f"⚠️ {camera_position} 錄影過程發生錯誤: {e}")
                break
                
        cap.release()
        out.release()
        
        total_seconds = frame_count // fps if fps > 0 else 0
        print(f"✅ {camera_position} IP camera 錄製完成: {total_seconds}秒, {frame_count}幀")
        
        # 檢查檔案是否成功建立
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"📁 {camera_position} 影片檔案大小: {file_size/1024/1024:.1f}MB")
            return True
        else:
            print(f"❌ {camera_position} 影片檔案建立失敗")
            return False
            
    except Exception as e:
        print(f"❌ IP camera 錄影錯誤 {camera_position}: {e}")
        return False

def record_camera_worker(app, trip_id, camera_position):
    """錄影工作線程 - 修正版"""
    global recording_status
    
    # 使用傳入的 app 實例建立上下文
    with app.app_context():
        video_record = None
        try:
            trip = Trip.query.get(trip_id)
            if not trip:
                print(f"❌ 找不到行程 ID: {trip_id}")
                return
            
            # 產生影片檔案名稱
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            video_number = f"VID_{trip.trip_number}_{camera_position}_{timestamp}"
            file_name = f"{camera_position}_{timestamp}.mp4"
            
            # 建立儲存路徑
            video_dir = trip.video_storage_path or f"trip_data/{trip.trip_number}/videos"
            os.makedirs(video_dir, exist_ok=True)
            file_path = os.path.join(video_dir, file_name)
            
            # 記錄開始時間
            start_time = datetime.now()
            recording_status[camera_position] = True
            
            print(f"📹 開始錄製 {camera_position} 攝影機: {file_path}")
            
            # 關鍵修正：先建立資料庫記錄，狀態設為 'recording'
            video_record = VideoRecord(
                video_number=video_number,
                trip_id=trip_id,
                camera_position=camera_position,
                start_time=start_time,
                file_path=file_path,
                uploaded=False,
                recording_status='recording'  # 明確設定為錄製中
            )
            
            # 這裡會成功，因為 end_time 現在允許 NULL
            db.session.add(video_record)
            db.session.commit()
            
            print(f"✅ 已建立 {camera_position} 錄影記錄: ID {video_record.id}")
            
            # 實際錄影邏輯
            recording_success = False
            
            # 檢查是否為實際的 IP camera 環境
            camera_url = CAMERA_URLS.get(camera_position)
            if camera_url and (camera_url.startswith('rtsp://') or camera_url.startswith('http://')):
                print(f"🎥 使用 IP camera 錄影: {camera_position}")
                recording_success = record_ip_camera(file_path, camera_position, video_record.id)
            else:
                print(f"🎭 使用模擬錄影: {camera_position} (開發模式)")
                # 模擬錄影過程（開發測試用）
                chunk_duration = 10  # 每10秒更新一次
                total_duration = 0
                
                while recording_status[camera_position]:
                    trip = Trip.query.get(trip_id)
                    if not trip or trip.status != '進行中':
                        print(f"⚠️  行程已結束，停止 {camera_position} 錄影")
                        break
                    
                    # 模擬寫入影片資料
                    create_dummy_video_file(file_path, total_duration + chunk_duration)
                    total_duration += chunk_duration
                    
                    if total_duration % 30 == 0:
                        print(f"📹 {camera_position} 已錄製: {total_duration}秒")
                    
                    time.sleep(chunk_duration)
                
                recording_success = True
            
            # 錄影結束，更新資料庫 - 關鍵修正
            end_time = datetime.now()
            
            # 取得實際檔案大小
            if os.path.exists(file_path):
                final_file_size = os.path.getsize(file_path)
                if final_file_size > 0:
                    recording_success = True
                else:
                    recording_success = False
            else:
                final_file_size = 0
                recording_success = False
            
            # 🔑 關鍵修正：正確更新所有欄位
            video_record.end_time = end_time
            video_record.file_size = final_file_size
            video_record.recording_status = 'completed' if recording_success else 'failed'
            
            # 🔑 重要：確保提交到資料庫
            db.session.commit()
            
            duration = (end_time - start_time).total_seconds()
            status_msg = "完成" if recording_success else "失敗"
            print(f"✅ {camera_position} 錄製{status_msg}: {int(duration)}秒, {final_file_size/1024/1024:.1f}MB")
            print(f"📄 資料庫狀態已更新為: {video_record.recording_status}")
            
        except Exception as e:
            print(f"❌ 錄影錯誤 {camera_position}: {e}")
            # 錯誤處理：標記為失敗
            if video_record:
                try:
                    video_record.end_time = datetime.now()
                    video_record.file_size = 0
                    video_record.recording_status = 'failed'
                    db.session.commit()
                    print(f"📄 {camera_position} 錄影失敗，狀態已標記為 failed")
                except Exception as commit_error:
                    print(f"❌ 更新失敗狀態時發生錯誤: {commit_error}")
                    
        finally:
            recording_status[camera_position] = False
            if camera_position in recording_threads:
                del recording_threads[camera_position]

@video_bp.route('/api/start_recording/<int:trip_id>')
def start_recording(trip_id):
    """開始錄影"""
    global recording_threads, recording_status
    
    trip = Trip.query.get_or_404(trip_id)
    
    if trip.status != '進行中':
        return jsonify({
            "status": "error",
            "message": "行程未進行中"
        }), 400
    
    # 確保錄影目錄存在
    video_dir = f"trip_data/{trip.trip_number}/videos"
    os.makedirs(video_dir, exist_ok=True)
    trip.video_storage_path = video_dir
    db.session.commit()
    
    started_cameras = []
    
    # 開始錄製雙鏡頭
    for camera_position in ['inside', 'outside']:
        if not recording_status[camera_position]:
            thread = threading.Thread(
                target=record_camera_worker,
                args=(current_app._get_current_object(), trip_id, camera_position),
                daemon=True
            )
            thread.start()
            recording_threads[camera_position] = thread
            started_cameras.append(camera_position)
    
    return jsonify({
        "status": "success",
        "message": f"開始錄製: {', '.join(started_cameras)}",
        "recording_cameras": started_cameras,
        "storage_path": video_dir
    })

@video_bp.route('/api/stop_recording')
def stop_recording():
    """停止錄影"""
    global recording_status
    
    stopped_cameras = []
    
    for camera_position in ['inside', 'outside']:
        if recording_status[camera_position]:
            recording_status[camera_position] = False
            stopped_cameras.append(camera_position)
    
    return jsonify({
        "status": "success",
        "message": f"停止錄製: {', '.join(stopped_cameras)}",
        "stopped_cameras": stopped_cameras
    })

@video_bp.route('/api/recording_status')
def get_recording_status():
    """取得錄影狀態"""
    return jsonify({
        "status": "success",
        "recording_status": recording_status,
        "active_threads": list(recording_threads.keys()),
        "camera_urls": CAMERA_URLS
    })

@video_bp.route('/api/trip_videos/<int:trip_id>')
def get_trip_videos(trip_id):
    """取得行程的所有影片"""
    videos = VideoRecord.query.filter_by(trip_id=trip_id).all()
    
    video_list = []
    for video in videos:
        # 檢查檔案是否存在
        file_exists = os.path.exists(video.file_path) if video.file_path else False
        file_size = video.file_size or 0
        
        duration = 0
        if video.start_time and video.end_time:
            duration = (video.end_time - video.start_time).total_seconds()
        
        video_list.append({
            "video_number": video.video_number,
            "camera_position": video.camera_position,
            "start_time": video.start_time.isoformat() if video.start_time else None,
            "end_time": video.end_time.isoformat() if video.end_time else None,
            "duration": duration,
            "file_path": video.file_path,
            "file_size": file_size,
            "file_size_mb": round(file_size / 1024 / 1024, 2) if file_size else 0,
            "file_exists": file_exists,
            "uploaded": video.uploaded
        })
    
    return jsonify({
        "status": "success",
        "trip_id": trip_id,
        "video_count": len(video_list),
        "videos": video_list
    })

# 在 blueprints/video.py 中修正 video_management 路由

@video_bp.route('/manage')
def video_management():
    """影片管理頁面"""
    # 取得所有有影片的行程，按建立時間降序排列（最新的在前面）
    trips_with_videos = db.session.query(Trip).join(VideoRecord).distinct().order_by(Trip.created_at.desc()).all()
    
    video_stats = {
        'total_trips': len(trips_with_videos),
        'total_videos': VideoRecord.query.count(),
        'total_size': 0,
        'completed_videos': VideoRecord.query.filter_by(recording_status='completed').count()
    }
    
    # 計算總檔案大小
    total_size = db.session.query(db.func.sum(VideoRecord.file_size)).scalar() or 0
    video_stats['total_size'] = total_size
    
    return render_template('video/manage.html', 
                         trips=trips_with_videos, 
                         stats=video_stats)

@video_bp.route('/trip/<int:trip_id>/videos')
def trip_videos(trip_id):
    """特定行程的影片查看頁面"""
    trip = Trip.query.get_or_404(trip_id)
    videos = VideoRecord.query.filter_by(trip_id=trip_id).all()
    
    # 整理影片資料
    video_data = []
    for video in videos:
        file_exists = os.path.exists(video.file_path) if video.file_path else False
        duration = 0
        if video.start_time and video.end_time:
            duration = (video.end_time - video.start_time).total_seconds()
        
        video_data.append({
            'id': video.id,
            'camera': video.camera_position,
            'start_time': video.start_time,
            'end_time': video.end_time,
            'duration': duration,
            'file_path': video.file_path,
            'file_size': video.file_size or 0,
            'file_exists': file_exists,
            'status': video.recording_status or 'unknown'
        })
    
    return render_template('video/trip_videos.html', 
                         trip=trip, 
                         videos=video_data)

@video_bp.route('/stream/<int:video_id>')
def stream_video(video_id):
    """串流播放影片 - 修正版本"""
    video = VideoRecord.query.get_or_404(video_id)
    
    print(f"🎬 播放請求: {video.video_number}")
    print(f"📁 檔案路徑: {video.file_path}")
    print(f"📄 錄影狀態: {video.recording_status}")
    
    # 檢查影片狀態
    if video.recording_status == 'recording':
        return "影片仍在錄製中，無法播放", 400
    
    if not video.file_path:
        return "影片檔案路徑不存在", 404
    
    # 使用絕對路徑
    if not os.path.isabs(video.file_path):
        file_path = os.path.abspath(video.file_path)
    else:
        file_path = video.file_path
    
    print(f"📍 絕對路徑: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ 檔案不存在: {file_path}")
        return f"影片檔案不存在: {file_path}", 404
    
    # 檢查檔案大小
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        return "影片檔案為空", 404
    
    print(f"✅ 檔案檢查通過，大小: {file_size/1024/1024:.1f}MB")
    
    try:
        # 檢查是否是 Range 請求
        range_header = request.headers.get('Range', None)
        
        if range_header:
            # 處理 Range 請求（用於影片播放的尋軸功能）
            byte_start = 0
            byte_end = file_size - 1
            
            match = re.search(r'bytes=(\d+)-(\d*)', range_header)
            if match:
                byte_start = int(match.group(1))
                if match.group(2):
                    byte_end = int(match.group(2))
            
            # 讀取指定範圍的資料
            def generate_range():
                with open(file_path, 'rb') as f:
                    f.seek(byte_start)
                    remaining = byte_end - byte_start + 1
                    
                    while remaining > 0:
                        chunk_size = min(1024 * 1024, remaining)  # 1MB chunks
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk
                        remaining -= len(chunk)
            
            response = Response(generate_range(), 
                              status=206,  # Partial Content
                              mimetype='video/mp4')
            response.headers['Content-Range'] = f'bytes {byte_start}-{byte_end}/{file_size}'
            response.headers['Accept-Ranges'] = 'bytes'
            response.headers['Content-Length'] = str(byte_end - byte_start + 1)
            
        else:
            # 完整檔案傳輸
            def generate_full():
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(1024 * 1024)  # 1MB chunks
                        if not chunk:
                            break
                        yield chunk
            
            response = Response(generate_full(), mimetype='video/mp4')
            response.headers['Content-Length'] = str(file_size)
            response.headers['Accept-Ranges'] = 'bytes'
        
        # 設定快取標頭
        response.headers['Cache-Control'] = 'public, max-age=3600'
        response.headers['Content-Disposition'] = f'inline; filename="{video.video_number}.mp4"'
        
        print(f"🎬 開始串流: {video.video_number}")
        return response
        
    except Exception as e:
        print(f"❌ 串流播放錯誤: {e}")
        return f"串流播放錯誤: {str(e)}", 500
    
@video_bp.route('/download/<int:video_id>')
def download_video(video_id):
    """下載影片檔案"""
    video = VideoRecord.query.get_or_404(video_id)
    
    if not os.path.exists(video.file_path):
        return "影片檔案不存在", 404
    
    # 生成友善的檔案名稱
    filename = f"{video.trip.trip_number}_{video.camera_position}_{video.start_time.strftime('%Y%m%d_%H%M%S')}.mp4"
    
    return send_file(video.file_path, 
                    as_attachment=True, 
                    download_name=filename)

@video_bp.route('/api/video_info/<int:video_id>')
def api_video_info(video_id):
    """取得影片詳細資訊 API"""
    video = VideoRecord.query.get_or_404(video_id)
    
    file_exists = os.path.exists(video.file_path) if video.file_path else False
    duration = 0
    if video.start_time and video.end_time:
        duration = (video.end_time - video.start_time).total_seconds()
    
    return jsonify({
        'id': video.id,
        'video_number': video.video_number,
        'camera_position': video.camera_position,
        'start_time': video.start_time.isoformat() if video.start_time else None,
        'end_time': video.end_time.isoformat() if video.end_time else None,
        'duration': duration,
        'file_path': video.file_path,
        'file_size': video.file_size or 0,
        'file_exists': file_exists,
        'status': video.recording_status or 'unknown',
        'trip': {
            'id': video.trip.id,
            'trip_number': video.trip.trip_number,
            'name': video.trip.name
        }
    })

@video_bp.route('/api/delete_video/<int:video_id>', methods=['DELETE'])
def api_delete_video(video_id):
    """刪除影片檔案和記錄"""
    video = VideoRecord.query.get_or_404(video_id)
    
    try:
        # 刪除實體檔案
        if video.file_path and os.path.exists(video.file_path):
            os.remove(video.file_path)
            
        # 刪除資料庫記錄
        db.session.delete(video)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'影片 {video.video_number} 已刪除'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'刪除影片失敗: {str(e)}'
        }), 500

@video_bp.route('/api/camera_test/<camera_position>')
def test_camera_connection(camera_position):
    """測試攝影機連線"""
    if camera_position not in CAMERA_URLS:
        return jsonify({
            "status": "error",
            "message": f"未知的攝影機位置: {camera_position}"
        }), 400
    
    camera_url = CAMERA_URLS[camera_position]
    
    try:
        # 測試連線
        cap = cv2.VideoCapture(camera_url)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                height, width = frame.shape[:2]
                cap.release()
                
                return jsonify({
                    "status": "success",
                    "camera_position": camera_position,
                    "camera_url": camera_url,
                    "resolution": f"{width}x{height}",
                    "message": "攝影機連線正常"
                })
            else:
                cap.release()
                return jsonify({
                    "status": "error",
                    "camera_position": camera_position,
                    "camera_url": camera_url,
                    "message": "攝影機無法讀取畫面"
                })
        else:
            return jsonify({
                "status": "error",
                "camera_position": camera_position,
                "camera_url": camera_url,
                "message": "無法開啟攝影機連線"
            })
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "camera_position": camera_position,
            "camera_url": camera_url,
            "message": f"攝影機測試錯誤: {str(e)}"
        })

@video_bp.route('/api/refresh_video_status')
def refresh_video_status():
    """重新檢查所有影片的狀態"""
    videos = VideoRecord.query.all()
    updated = 0
    
    for video in videos:
        old_status = video.recording_status
        
        # 重新檢查檔案狀態
        if video.file_path and os.path.exists(video.file_path):
            file_size = os.path.getsize(video.file_path)
            video.file_size = file_size  # 更新檔案大小
            
            if file_size > 0 and video.end_time:
                video.recording_status = 'completed'
            elif not video.end_time:
                video.recording_status = 'recording'
            else:
                video.recording_status = 'failed'
        else:
            video.recording_status = 'failed'
            video.file_size = 0
        
        if old_status != video.recording_status:
            updated += 1
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': f'已更新 {updated} 個影片狀態',
        'total_videos': len(videos)
    })

# 清理函數 - 應用程式關閉時呼叫
def cleanup_recording():
    """清理錄影資源"""
    global recording_status, recording_threads
    
    print("🛑 清理錄影資源...")
    
    # 停止所有錄影
    for camera_position in recording_status:
        recording_status[camera_position] = False
    
    # 等待所有線程結束
    for thread in recording_threads.values():
        if thread.is_alive():
            thread.join(timeout=5)
    
    recording_threads.clear()
    print("✅ 錄影資源清理完成")

# 在 blueprints/video.py 中新增一個強制修正所有影片狀態的端點

@video_bp.route('/api/force_fix_all_videos')
def force_fix_all_videos():
    """強制修正所有影片狀態 - 偵錯用"""
    try:
        # 取得所有狀態為 'recording' 的影片
        recording_videos = VideoRecord.query.filter_by(recording_status='recording').all()
        
        fixed_count = 0
        failed_count = 0
        
        for video in recording_videos:
            print(f"🔧 檢查影片: {video.video_number}")
            
            # 檢查對應的行程是否已結束
            trip = Trip.query.get(video.trip_id)
            if trip and trip.status in ['已完成', '已上傳']:
                # 行程已結束，但影片仍標記為錄製中
                print(f"📄 行程 {trip.trip_number} 已結束，修正影片狀態")
                
                if video.file_path and os.path.exists(video.file_path):
                    file_size = os.path.getsize(video.file_path)
                    video.file_size = file_size
                    
                    if file_size > 0:
                        video.recording_status = 'completed'
                        video.end_time = trip.end_time or datetime.now()
                        fixed_count += 1
                        print(f"✅ 修正為完成: {video.video_number}")
                    else:
                        video.recording_status = 'failed'
                        video.end_time = trip.end_time or datetime.now()
                        failed_count += 1
                        print(f"❌ 標記為失敗: {video.video_number} (檔案為空)")
                else:
                    video.recording_status = 'failed'
                    video.end_time = trip.end_time or datetime.now()
                    video.file_size = 0
                    failed_count += 1
                    print(f"❌ 標記為失敗: {video.video_number} (檔案不存在)")
            else:
                print(f"⚠️ 跳過: {video.video_number} (行程仍進行中或不存在)")
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'修正完成！成功: {fixed_count}, 失敗: {failed_count}',
            'fixed_count': fixed_count,
            'failed_count': failed_count,
            'total_checked': len(recording_videos)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'修正失敗: {str(e)}'
        }), 500