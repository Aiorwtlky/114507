# blueprints/camera.py
from flask import Blueprint, Response, render_template, jsonify, current_app
import cv2
import numpy as np
import threading
import time
from config import CAMERA_URLS, CAMERA_CONFIG

camera_bp = Blueprint('camera', __name__)


# ==================== 攝影機串流類別 ====================

class CameraStream:
    """攝影機串流管理類別"""
    
    def __init__(self, cam_id, resolution=None):
        self.cam_id = cam_id
        self.url = CAMERA_URLS.get(cam_id)
        if not self.url:
            raise ValueError(f"Camera ID '{cam_id}' not found in config")
        
        self.resolution = resolution or (
            CAMERA_CONFIG['FRAME_WIDTH'], 
            CAMERA_CONFIG['FRAME_HEIGHT']
        )
        
        self.frame = self._blank_frame()
        self.lock = threading.Lock()
        self.running = True
        self.cap = None
        self.reconnect_attempts = 0
        self.max_attempts = CAMERA_CONFIG['MAX_RECONNECT_ATTEMPTS']
        
        # 啟動串流線程
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()
    
    def _blank_frame(self):
        """建立空白畫面"""
        w, h = self.resolution
        blank = np.full((h, w, 3), 64, dtype=np.uint8)
        
        cv2.putText(
            blank, 
            f'Camera: {self.cam_id}', 
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.7, 
            (255, 255, 255), 
            2
        )
        cv2.putText(
            blank, 
            'Connecting...', 
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.5, 
            (0, 255, 255), 
            1
        )
        
        return blank
    
    def _connect_camera(self):
        """連接攝影機"""
        try:
            if self.cap:
                self.cap.release()
            
            self.cap = cv2.VideoCapture(self.url)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.cap.set(cv2.CAP_PROP_FPS, CAMERA_CONFIG['FPS'])
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, CAMERA_CONFIG['BUFFER_SIZE'])
            
            ret, frame = self.cap.read()
            if ret:
                print(f"[Camera {self.cam_id}] Connected successfully")
                self.reconnect_attempts = 0
                return True
            else:
                print(f"[Camera {self.cam_id}] Failed to read frame")
                return False
                
        except Exception as e:
            print(f"[Camera {self.cam_id}] Connection error: {e}")
            return False
    
    def _update(self):
        """主要串流更新迴圈"""
        while self.running:
            try:
                if not self.cap or not self.cap.isOpened():
                    if self.reconnect_attempts < self.max_attempts:
                        print(
                            f"[Camera {self.cam_id}] Attempting to connect... "
                            f"({self.reconnect_attempts + 1}/{self.max_attempts})"
                        )
                        if self._connect_camera():
                            continue
                        else:
                            self.reconnect_attempts += 1
                            time.sleep(CAMERA_CONFIG['RECONNECT_TIMEOUT'])
                            continue
                    else:
                        print(f"[Camera {self.cam_id}] Max reconnect attempts reached")
                        time.sleep(10)
                        self.reconnect_attempts = 0
                        continue
                
                ret, frame = self.cap.read()
                if ret:
                    if frame.shape[:2][::-1] != self.resolution:
                        frame = cv2.resize(frame, self.resolution)
                    
                    with self.lock:
                        self.frame = frame
                else:
                    print(f"[Camera {self.cam_id}] Failed to read frame, reconnecting...")
                    self.cap.release()
                    self.cap = None
                    
            except Exception as e:
                print(f"[Camera {self.cam_id}] Update error: {e}")
                time.sleep(1)
    
    def get_frame(self):
        """取得當前畫面"""
        with self.lock:
            return self.frame.copy()
    
    def generate_frames(self):
        """產生 MJPEG 串流"""
        while self.running:
            frame = self.get_frame()
            
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ret:
                frame_bytes = buffer.tobytes()
                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + 
                    frame_bytes + 
                    b'\r\n'
                )
            
            time.sleep(1.0 / CAMERA_CONFIG['FPS'])
    
    def stop(self):
        """停止串流"""
        self.running = False
        if self.cap:
            self.cap.release()
        self.thread.join()


# ==================== 攝影機池管理 ====================

camera_pool = {}

def get_camera(cam_id):
    """取得攝影機實例"""
    if cam_id not in camera_pool:
        try:
            camera_pool[cam_id] = CameraStream(cam_id)
        except ValueError as e:
            print(f"Error creating camera {cam_id}: {e}")
            return None
    return camera_pool[cam_id]

def stop_all_cameras():
    """停止所有攝影機"""
    for cam in camera_pool.values():
        cam.stop()
    camera_pool.clear()


# ==================== Flask 路由 ====================

@camera_bp.route('/test')
def camera_test():
    """測試 camera blueprint 是否正常運作"""
    return jsonify({
        "status": "ok",
        "message": "Camera blueprint is working",
        "available_cameras": list(CAMERA_URLS.keys()),
        "camera_urls": CAMERA_URLS
    })

@camera_bp.route('/<cam_id>')
def camera_view(cam_id):
    """攝影機檢視頁面"""
    if cam_id not in CAMERA_URLS:
        return f"Camera '{cam_id}' not found", 404
    
    return render_template(
        'camera/view.html',
        cam_id=cam_id,
        camera_name=cam_id.replace('_', ' ').title()
    )

@camera_bp.route('/<cam_id>/stream')
def camera_stream(cam_id):
    """攝影機 MJPEG 串流"""
    camera = get_camera(cam_id)
    if not camera:
        return f"Camera '{cam_id}' not available", 404
    
    return Response(
        camera.generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@camera_bp.route('/<cam_id>/status')
def camera_status(cam_id):
    """攝影機狀態 API"""
    if cam_id not in CAMERA_URLS:
        return jsonify({"error": f"Camera '{cam_id}' not found"}), 404
    
    camera = get_camera(cam_id)
    if not camera:
        return jsonify({
            "cam_id": cam_id,
            "status": "error",
            "message": "Camera not available"
        })
    
    return jsonify({
        "cam_id": cam_id,
        "status": "running" if camera.running else "stopped",
        "url": camera.url,
        "resolution": camera.resolution,
        "reconnect_attempts": camera.reconnect_attempts
    })

@camera_bp.route('/list')
def cameras_list():
    """列出所有可用攝影機"""
    return jsonify({
        "cameras": list(CAMERA_URLS.keys()),
        "urls": CAMERA_URLS
    })


# ==================== AI 監控整合 ====================

ai_monitoring_active = {'inside': False, 'outside': False}

def ai_monitoring_worker(camera_id, trip_id, interval=2):
    """
    AI 監控執行緒
    
    Args:
        camera_id: 'inside' 或 'outside'
        trip_id: 行程 ID
        interval: 偵測間隔（秒）
    """
    print(f"========== AI 監控執行緒啟動 ==========")
    print(f"camera_id={camera_id}, trip_id={trip_id}")
    
    try:
        from models import Trip, db
        from utils.image_recognition import get_vision_system
        from utils.db_helper import LocalEventHelper
        
        print("[1/3] 模組導入成功")
        
        # 初始化
        with current_app.app_context():
            trip = Trip.query.get(trip_id)
            if not trip:
                print(f"錯誤: 找不到行程 ID {trip_id}")
                return
            
            vision_system = get_vision_system()
            print("[2/3] 視覺系統初始化成功")
            
            # 設定駕駛員（用於個體化校準）
            if trip.personnel:
                vision_system.set_driver(trip.personnel.personnel_number)
            
            # 內鏡頭需要校準
            if camera_id == 'inside':
                vision_system.start_calibration()
                print("開始駕駛員校準...")
        
        # 取得攝影機
        camera = get_camera(camera_id)
        if not camera:
            print(f"錯誤: 無法取得 {camera_id} 攝影機")
            return
        
        print(f"[3/3] {camera_id} 攝影機已就緒")
        print(f"========== {camera_id} AI 監控開始運行 ==========")
        
        # 主偵測迴圈
        frame_count = 0
        while ai_monitoring_active[camera_id]:
            try:
                frame = camera.get_frame()
                if frame is None:
                    time.sleep(interval)
                    continue
                
                frame_count += 1
                
                # 準備 GPIO 數據（外鏡頭需要）
                gpio_data = None
                if camera_id == 'outside':
                    try:
                        from blueprints.gpio import read_gpio_from_pico
                        gpio_result = read_gpio_from_pico()
                        if gpio_result['status'] == 'success':
                            gpio_data = {
                                'left_turn': gpio_result['left'] == 1,
                                'right_turn': gpio_result['right'] == 1
                            }
                    except Exception:
                        pass
                
                # 執行 AI 偵測
                event_record = vision_system.predict_from_frame(
                    frame,
                    camera_id,
                    save_image=False,
                    gpio_data=gpio_data,
                    gps_data=None
                )
                
                # 如果偵測到事件，儲存到資料庫
                if event_record:
                    with current_app.app_context():
                        try:
                            LocalEventHelper.create_event(
                                trip_id=trip_id,
                                camera_type=event_record['camera_type'],
                                event_number=event_record['event_number'],
                                event_description=event_record['event_description'],
                                confidence_score=event_record['confidence_score'],
                                deduction_points=event_record['deduction_points'],
                                event_details=event_record.get('event_details'),
                                local_image_path=event_record.get('local_image_path')
                            )
                        except Exception as e:
                            print(f"儲存事件失敗: {e}")
                
                # 每 100 幀顯示一次狀態
                if frame_count % 100 == 0:
                    print(f"[{camera_id}] 已處理 {frame_count} 幀")
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"[{camera_id}] AI 偵測錯誤: {e}")
                time.sleep(1)
    
    except Exception as e:
        print(f"========== AI 監控執行緒初始化失敗 ==========")
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"========== {camera_id} AI 監控已停止 ==========")


@camera_bp.route('/<cam_id>/start_ai/<int:trip_id>', methods=['POST'])
def start_ai_monitoring(cam_id, trip_id):
    """啟動 AI 監控"""
    if cam_id not in ['inside', 'outside']:
        return jsonify({"error": "無效的鏡頭 ID"}), 400
    
    if ai_monitoring_active.get(cam_id):
        return jsonify({
            "status": "warning",
            "message": f"{cam_id} AI 監控已在運行中"
        })
    
    ai_monitoring_active[cam_id] = True
    thread = threading.Thread(
        target=ai_monitoring_worker,
        args=(cam_id, trip_id, 2),
        daemon=True
    )
    thread.start()
    
    return jsonify({
        "status": "success",
        "message": f"{cam_id} AI 監控已啟動",
        "trip_id": trip_id
    })


@camera_bp.route('/<cam_id>/stop_ai', methods=['POST'])
def stop_ai_monitoring(cam_id):
    """停止 AI 監控"""
    if cam_id not in ['inside', 'outside']:
        return jsonify({"error": "無效的鏡頭 ID"}), 400
    
    ai_monitoring_active[cam_id] = False
    return jsonify({
        "status": "success",
        "message": f"{cam_id} AI 監控已停止"
    })


@camera_bp.route('/ai_monitoring_status')
def get_ai_monitoring_status():
    """取得所有攝影機的 AI 監控狀態"""
    return jsonify({
        "status": "success",
        "monitoring": {
            "inside": ai_monitoring_active.get('inside', False),
            "outside": ai_monitoring_active.get('outside', False)
        }
    })