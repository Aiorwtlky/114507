import cv2
import threading
import time
import os
import logging
from typing import Optional, Dict, List
import queue
from utils import create_video_writer, cleanup_old_files

logger = logging.getLogger(__name__)

class DashcamRecorder:
    """行車記錄器 - 針對樹莓派優化"""
    
    def __init__(self, config):
        self.config = config
        self.recording = False
        self.current_segment = None
        self.segment_start_time = None
        self.frame_queue = queue.Queue(maxsize=30)  # 限制隊列大小
        self.alert_buffer = []
        
        # 錄影參數 (樹莓派優化)
        self.fps = 15  # 降低FPS以減少資源消耗
        self.width = 640
        self.height = 480
        self.codec = 'mp4v'  # 使用較快的編碼
        
        # 執行緒
        self.recording_thread = None
        self.is_running = False
        
        # 確保目錄存在
        os.makedirs(self.config.temp_videos_dir, exist_ok=True)
        
    def start_recording(self):
        """開始錄影"""
        if self.recording:
            logger.warning("錄影已在進行中")
            return
            
        self.recording = True
        self.is_running = True
        self.recording_thread = threading.Thread(target=self._recording_loop, daemon=True)
        self.recording_thread.start()
        logger.info("行車記錄器開始錄影")
    
    def stop_recording(self):
        """停止錄影"""
        self.recording = False
        self.is_running = False
        
        if self.recording_thread:
            self.recording_thread.join(timeout=5.0)
        
        # 完成當前片段
        if self.current_segment:
            self._finish_current_segment()
        
        logger.info("行車記錄器停止錄影")
    
    def add_frame(self, frame, alerts: List[Dict] = None):
        """添加影像幀"""
        if not self.recording:
            return
            
        try:
            # 調整幀大小以節省資源
            if frame.shape[:2] != (self.height, self.width):
                frame = cv2.resize(frame, (self.width, self.height))
            
            # 非阻塞式添加
            if not self.frame_queue.full():
                timestamp = time.time()
                self.frame_queue.put((frame.copy(), timestamp, alerts or []))
            else:
                # 隊列滿時丟棄最舊的幀
                try:
                    self.frame_queue.get_nowait()
                    self.frame_queue.put((frame.copy(), timestamp, alerts or []))
                except queue.Empty:
                    pass
                    
        except Exception as e:
            logger.error(f"添加幀錯誤: {e}")
    
    def _recording_loop(self):
        """錄影主循環"""
        while self.is_running:
            try:
                # 檢查是否需要開始新片段
                if self._should_start_new_segment():
                    self._start_new_segment()
                
                # 處理幀隊列
                try:
                    frame, timestamp, alerts = self.frame_queue.get(timeout=1.0)
                    self._process_frame(frame, timestamp, alerts)
                except queue.Empty:
                    continue
                    
            except Exception as e:
                logger.error(f"錄影循環錯誤: {e}")
                time.sleep(0.1)
        
        # 完成當前片段
        if self.current_segment:
            self._finish_current_segment()
    
    def _should_start_new_segment(self) -> bool:
        """檢查是否應該開始新片段"""
        if self.current_segment is None:
            return True
            
        # 檢查時間是否超過設定的片段長度
        if self.segment_start_time:
            elapsed = time.time() - self.segment_start_time
            return elapsed >= self.config.video_duration
            
        return False
    
    def _start_new_segment(self):
        """開始新的錄影片段"""
        try:
            # 完成當前片段
            if self.current_segment:
                self._finish_current_segment()
            
            # 建立新片段檔案
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"dashcam_{timestamp}.mp4"
            filepath = os.path.join(self.config.temp_videos_dir, filename)
            
            # 建立影片寫入器
            fourcc = cv2.VideoWriter_fourcc(*self.codec)
            self.current_segment = cv2.VideoWriter(
                filepath, fourcc, self.fps, (self.width, self.height)
            )
            
            if not self.current_segment.isOpened():
                logger.error(f"無法建立影片檔案: {filepath}")
                self.current_segment = None
                return
            
            self.segment_start_time = time.time()
            self.alert_buffer = []
            
            logger.info(f"開始新片段: {filename}")
            
        except Exception as e:
            logger.error(f"開始新片段錯誤: {e}")
            self.current_segment = None
    
    def _process_frame(self, frame, timestamp, alerts):
        """處理單一幀"""
        try:
            if self.current_segment and self.current_segment.isOpened():
                # 添加時間戳記
                frame_with_overlay = self._add_overlay(frame, timestamp, alerts)
                
                # 寫入影片
                self.current_segment.write(frame_with_overlay)
                
                # 收集警報
                if alerts:
                    self.alert_buffer.extend(alerts)
                    
        except Exception as e:
            logger.error(f"處理幀錯誤: {e}")
    
    def _add_overlay(self, frame, timestamp, alerts) -> cv2.typing.MatLike:
        """添加覆蓋層資訊"""
        overlay_frame = frame.copy()
        
        try:
            # 添加時間戳記
            time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
            cv2.putText(overlay_frame, time_str, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # 添加警報資訊
            if alerts:
                y_offset = 60
                for alert in alerts[-3:]:  # 只顯示最新的3個警報
                    alert_text = f"{alert.get('code', '')}: {alert.get('name', '')}"
                    cv2.putText(overlay_frame, alert_text, (10, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                    y_offset += 25
            
            # 添加系統狀態
            status_text = "REC"
            cv2.putText(overlay_frame, status_text, (overlay_frame.shape[1] - 80, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # 添加紅色錄影指示點
            cv2.circle(overlay_frame, (overlay_frame.shape[1] - 120, 25), 8, (0, 0, 255), -1)
            
        except Exception as e:
            logger.error(f"添加覆蓋層錯誤: {e}")
        
        return overlay_frame
    
    def _finish_current_segment(self):
        """完成當前片段"""
        try:
            if self.current_segment:
                self.current_segment.release()
                
                # 取得檔案資訊
                segment_info = self._get_segment_info()
                
                logger.info(f"完成片段: {segment_info['filename']}")
                logger.info(f"警報數量: {len(self.alert_buffer)}")
                
                # 通知上傳服務
                self._notify_upload_service(segment_info)
                
                self.current_segment = None
                self.segment_start_time = None
                
                # 清理舊檔案
                cleanup_old_files(self.config.temp_videos_dir, self.config.max_local_files)
                
        except Exception as e:
            logger.error(f"完成片段錯誤: {e}")
    
    def _get_segment_info(self) -> Dict:
        """取得片段資訊"""
        try:
            # 取得最新的影片檔案
            video_files = [f for f in os.listdir(self.config.temp_videos_dir) if f.endswith('.mp4')]
            if video_files:
                latest_file = max(video_files, key=lambda f: os.path.getctime(
                    os.path.join(self.config.temp_videos_dir, f)
                ))
                
                filepath = os.path.join(self.config.temp_videos_dir, latest_file)
                file_size = os.path.getsize(filepath)
                
                return {
                    'filename': latest_file,
                    'filepath': filepath,
                    'file_size': file_size,
                    'alerts': self.alert_buffer.copy(),
                    'duration': self.config.video_duration,
                    'timestamp': self.segment_start_time
                }
        except Exception as e:
            logger.error(f"取得片段資訊錯誤: {e}")
        
        return {}
    
    def _notify_upload_service(self, segment_info: Dict):
        """通知上傳服務"""
        try:
            # 這裡可以實作通知機制，例如寫入檔案或使用訊息隊列
            upload_queue_file = os.path.join(self.config.data_dir, 'upload_queue.txt')
            
            with open(upload_queue_file, 'a', encoding='utf-8') as f:
                import json
                f.write(json.dumps(segment_info, ensure_ascii=False) + '\n')
                
        except Exception as e:
            logger.error(f"通知上傳服務錯誤: {e}")
    
    def get_recording_status(self) -> Dict:
        """取得錄影狀態"""
        return {
            'recording': self.recording,
            'current_segment_duration': time.time() - self.segment_start_time if self.segment_start_time else 0,
            'queue_size': self.frame_queue.qsize(),
            'alerts_in_buffer': len(self.alert_buffer),
            'temp_files_count': len([f for f in os.listdir(self.config.temp_videos_dir) if f.endswith('.mp4')])
        }