# ai_core/frame_processor.py
"""
影像幀處理器
管理 AI 偵測器的執行，控制處理頻率
"""

import threading
import time
from queue import Queue
from datetime import datetime

class FrameProcessor:
    """影像幀處理器 - 控制 AI 偵測頻率"""
    
    def __init__(self, detector, process_fps=10):
        """
        初始化處理器
        
        Args:
            detector: AI 偵測器實例
            process_fps: 處理頻率（每秒處理幾幀）
        """
        self.detector = detector
        self.process_fps = process_fps
        self.process_interval = 1.0 / process_fps
        
        # 處理執行緒
        self.is_running = False
        self.process_thread = None
        
        # 統計
        self.processed_count = 0
        self.last_process_time = None
        self.actual_fps = 0
        
        # 結果佇列
        self.result_queue = Queue(maxsize=100)
    
    def start(self, camera_manager):
        """
        啟動處理執行緒
        
        Args:
            camera_manager: CameraManager 實例
        """
        if self.is_running:
            return
        
        self.camera_manager = camera_manager
        self.is_running = True
        self.process_thread = threading.Thread(
            target=self._process_loop, 
            daemon=True
        )
        self.process_thread.start()
        print(f"[{self.detector.__class__.__name__}] 處理執行緒已啟動 ({self.process_fps} FPS)")
    
    def stop(self):
        """停止處理執行緒"""
        self.is_running = False
        
        if self.process_thread:
            self.process_thread.join(timeout=2)
        
        print(f"[{self.detector.__class__.__name__}] 處理執行緒已停止")

    def _process_loop(self):
        """處理迴圈（在獨立執行緒中執行）"""
        while self.is_running:
            start_time = time.time()
            
            try:
                frame_data = self.camera_manager.get_frame(timeout=0.5)
                
                if frame_data is None:
                    time.sleep(0.1)
                    continue
                
                # 改回用 detect
                result = self.detector.detect(
                    frame=frame_data['frame'],
                    timestamp=frame_data['timestamp']
                )
                
                if result and result.get('event_detected'):
                    try:
                        self.result_queue.put(result, block=False)
                    except:
                        pass
                
                self.processed_count += 1
                current_time = time.time()
                if self.last_process_time:
                    self.actual_fps = 1.0 / (current_time - self.last_process_time)
                self.last_process_time = current_time
                
                elapsed = time.time() - start_time
                sleep_time = max(0, self.process_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
            except Exception as e:
                print(f"[{self.detector.__class__.__name__}] 處理錯誤: {e}")
                time.sleep(0.5)
    
    def get_result(self, timeout=0.1):
        """取得偵測結果"""
        try:
            return self.result_queue.get(timeout=timeout)
        except:
            return None
    
    def get_status(self):
        """取得處理器狀態"""
        return {
            'detector': self.detector.__class__.__name__,
            'is_running': self.is_running,
            'processed_count': self.processed_count,
            'target_fps': self.process_fps,
            'actual_fps': round(self.actual_fps, 2),
            'result_queue_size': self.result_queue.qsize()
        }