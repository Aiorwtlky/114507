# ai_core/camera_manager.py
"""
雙鏡頭管理器
負責從 RTSP 串流讀取影像，使用多執行緒避免阻塞
"""

import cv2
import threading
import time
from queue import Queue, Full
from datetime import datetime
from config import CAMERA_URLS, CAMERA_CONFIG

class CameraManager:
    """攝影機管理器 - 處理雙鏡頭串流"""
    
    # 在 camera_manager.py 的 __init__ 中加入：

    def __init__(self, camera_type='inside', source=None):
        self.camera_type = camera_type
    
        # Demo 模式：支援本地攝影機或影片檔
        if source is not None:
            self.source = source
        else:
            from config import DEMO_MODE, CAMERA_SOURCES, CAMERA_URLS
            if DEMO_MODE:
                self.source = CAMERA_SOURCES.get(camera_type)
            else:
                self.source = CAMERA_URLS.get(camera_type)
    
    # ... 其他初始化代碼
        
        # 影像佇列（最多保留 30 幀，約 1 秒）
        self.frame_queue = Queue(maxsize=30)
        
        # 狀態控制
        self.is_running = False
        self.capture_thread = None
        self.cap = None
        
        # 統計資訊
        self.frame_count = 0
        self.dropped_frames = 0
        self.last_frame_time = None
        self.fps = 0
        
        # 重連設定
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = CAMERA_CONFIG['MAX_RECONNECT_ATTEMPTS']
        
    def connect(self):
        """連接到 RTSP 串流"""
        try:
            self.cap = cv2.VideoCapture(self.rtsp_url)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, CAMERA_CONFIG['BUFFER_SIZE'])
            
            if not self.cap.isOpened():
                raise ConnectionError(f"無法連接到 {self.camera_type} 攝影機")
            
            print(f"[{self.camera_type}] 攝影機連接成功: {self.rtsp_url}")
            self.reconnect_attempts = 0
            return True
            
        except Exception as e:
            print(f"[{self.camera_type}] 攝影機連接失敗: {e}")
            return False
    
    def start(self):
        """啟動攝影機擷取執行緒"""
        if self.is_running:
            print(f"[{self.camera_type}] 攝影機已在運行中")
            return
        
        if not self.connect():
            return False
        
        self.is_running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        print(f"[{self.camera_type}] 攝影機擷取執行緒已啟動")
        return True
    
    def stop(self):
        """停止攝影機擷取"""
        self.is_running = False
        
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        # 清空佇列
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except:
                break
        
        print(f"[{self.camera_type}] 攝影機已停止")
    
    def _capture_loop(self):
        """持續擷取影像的迴圈（在獨立執行緒中執行）"""
        consecutive_failures = 0
        
        while self.is_running:
            try:
                ret, frame = self.cap.read()
                
                if not ret or frame is None:
                    consecutive_failures += 1
                    print(f"[{self.camera_type}] 讀取失敗 ({consecutive_failures})")
                    
                    if consecutive_failures >= 10:
                        print(f"[{self.camera_type}] 連續失敗，嘗試重連...")
                        self._reconnect()
                        consecutive_failures = 0
                    
                    time.sleep(0.1)
                    continue
                
                # 重設失敗計數
                consecutive_failures = 0
                
                # 計算 FPS
                current_time = time.time()
                if self.last_frame_time:
                    self.fps = 1.0 / (current_time - self.last_frame_time)
                self.last_frame_time = current_time
                
                # 嘗試放入佇列
                try:
                    self.frame_queue.put({
                        'frame': frame,
                        'timestamp': datetime.now(),
                        'frame_number': self.frame_count
                    }, block=False)
                    self.frame_count += 1
                except Full:
                    # 佇列已滿，丟棄最舊的幀
                    try:
                        self.frame_queue.get_nowait()
                        self.frame_queue.put({
                            'frame': frame,
                            'timestamp': datetime.now(),
                            'frame_number': self.frame_count
                        }, block=False)
                        self.dropped_frames += 1
                    except:
                        pass
                
            except Exception as e:
                print(f"[{self.camera_type}] 擷取錯誤: {e}")
                time.sleep(0.5)
    
    def _reconnect(self):
        """重新連接攝影機"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            print(f"[{self.camera_type}] 超過最大重連次數，放棄重連")
            self.is_running = False
            return
        
        self.reconnect_attempts += 1
        print(f"[{self.camera_type}] 重連嘗試 {self.reconnect_attempts}/{self.max_reconnect_attempts}")
        
        if self.cap:
            self.cap.release()
        
        time.sleep(CAMERA_CONFIG['RECONNECT_TIMEOUT'])
        self.connect()
    
    def get_frame(self, timeout=1.0):
        """
        從佇列取得影像幀
        
        Args:
            timeout: 等待超時時間（秒）
        
        Returns:
            dict: {'frame': np.array, 'timestamp': datetime, 'frame_number': int}
            None: 如果超時或無影像
        """
        try:
            return self.frame_queue.get(timeout=timeout)
        except:
            return None
    
    def get_status(self):
        """取得攝影機狀態"""
        return {
            'camera_type': self.camera_type,
            'is_running': self.is_running,
            'frame_count': self.frame_count,
            'dropped_frames': self.dropped_frames,
            'fps': round(self.fps, 2),
            'queue_size': self.frame_queue.qsize(),
            'reconnect_attempts': self.reconnect_attempts
        }