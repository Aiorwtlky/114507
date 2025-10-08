# blueprints/camera.py
from flask import Blueprint, Response, render_template, jsonify
import cv2
import numpy as np
import threading
import time
from config import CAMERA_URLS, CAMERA_CONFIG

camera_bp = Blueprint('camera', __name__)

class CameraStream:
    def __init__(self, cam_id, resolution=None):
        self.cam_id = cam_id
        self.url = CAMERA_URLS.get(cam_id)
        if not self.url:
            raise ValueError(f"Camera ID '{cam_id}' not found in config")
            
        # 使用 config 設定或預設值
        self.resolution = resolution or (CAMERA_CONFIG['FRAME_WIDTH'], CAMERA_CONFIG['FRAME_HEIGHT'])
        
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
        
        # 在空白畫面上顯示攝影機資訊
        cv2.putText(blank, f'Camera: {self.cam_id}', (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(blank, 'Connecting...', (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        return blank
    
    def _connect_camera(self):
        """連接攝影機"""
        try:
            if self.cap:
                self.cap.release()
            
            self.cap = cv2.VideoCapture(self.url)
            
            # 設定攝影機參數
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.cap.set(cv2.CAP_PROP_FPS, CAMERA_CONFIG['FPS'])
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, CAMERA_CONFIG['BUFFER_SIZE'])
            
            # 測試連接
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
                # 嘗試連接攝影機
                if not self.cap or not self.cap.isOpened():
                    if self.reconnect_attempts < self.max_attempts:
                        print(f"[Camera {self.cam_id}] Attempting to connect... ({self.reconnect_attempts + 1}/{self.max_attempts})")
                        if self._connect_camera():
                            continue
                        else:
                            self.reconnect_attempts += 1
                            time.sleep(CAMERA_CONFIG['RECONNECT_TIMEOUT'])
                            continue
                    else:
                        print(f"[Camera {self.cam_id}] Max reconnect attempts reached")
                        time.sleep(10)  # 等待較長時間再重試
                        self.reconnect_attempts = 0
                        continue
                
                # 讀取畫面
                ret, frame = self.cap.read()
                if ret:
                    # 調整畫面大小
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
            
            # 編碼為 JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ret:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            time.sleep(1.0 / CAMERA_CONFIG['FPS'])
    
    def stop(self):
        """停止串流"""
        self.running = False
        if self.cap:
            self.cap.release()
        self.thread.join()

# 攝影機池管理
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

# 🔧 修正的路由定義 - 移除重複的 /camera 前綴
@camera_bp.route('/test')  # ✅ 會變成 /camera/test
def camera_test():
    """測試 camera blueprint 是否正常運作"""
    return jsonify({
        "status": "ok",
        "message": "Camera blueprint is working",
        "available_cameras": list(CAMERA_URLS.keys()),
        "camera_urls": CAMERA_URLS
    })

@camera_bp.route('/<cam_id>')  # ✅ 會變成 /camera/inside
def camera_view(cam_id):
    """攝影機檢視頁面"""
    if cam_id not in CAMERA_URLS:
        return f"Camera '{cam_id}' not found", 404
    
    return render_template('camera/view.html', 
                         cam_id=cam_id, 
                         camera_name=cam_id.replace('_', ' ').title())

@camera_bp.route('/<cam_id>/stream')  # ✅ 會變成 /camera/inside/stream
def camera_stream(cam_id):
    """攝影機 MJPEG 串流"""
    camera = get_camera(cam_id)
    if not camera:
        return f"Camera '{cam_id}' not available", 404
    
    return Response(camera.generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@camera_bp.route('/<cam_id>/status')  # ✅ 會變成 /camera/inside/status
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

@camera_bp.route('/list')  # ✅ 會變成 /camera/list
def cameras_list():
    """列出所有可用攝影機"""
    return jsonify({
        "cameras": list(CAMERA_URLS.keys()),
        "urls": CAMERA_URLS
    })