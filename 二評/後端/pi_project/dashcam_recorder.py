import cv2
import os
import time
import threading
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from utils import (
    setup_logging,
    get_performance_monitor,
    generate_video_filename,
    ensure_directory_exists,
    format_file_size,
    cleanup_old_files
)
from config import config

class DashcamRecorder:
    """行車記錄器影像錄製系統"""
    
    def __init__(self, config_obj=None):
        self.config = config_obj or config
        self.logger = setup_logging()
        self.performance_monitor = get_performance_monitor('dashcam_recorder')
        
        # 錄影參數
        self.recording_duration = self.config.recording.duration_seconds
        self.video_quality = self.config.recording.video_quality
        self.codec = cv2.VideoWriter_fourcc(*'mp4v')
        
        # 錄影狀態
        self.is_recording = False
        self.current_writer = None
        self.current_filename = None
        self.recording_start_time = None
        
        # 攝影機
        self.external_camera = None
        self.internal_camera = None
        
        # 執行緒控制
        self.recording_thread = None
        self.stop_event = threading.Event()
        
        # 回調函數（錄影完成時調用）
        self.on_video_completed_callback = None
        
        # 統計資料
        self.recording_stats = {
            'total_videos': 0,
            'total_recording_time': 0,
            'total_file_size': 0,
            'start_time': time.time(),
            'current_session_videos': 0
        }
        
        # 執行緒安全
        self._lock = threading.Lock()
        
        # 確保輸出目錄存在
        ensure_directory_exists(self.config.temp_videos_dir)
        
        self.logger.info("行車記錄器已初始化")
    
    def start_recording(self, use_external_camera: bool = True, use_internal_camera: bool = False) -> bool:
        """
        開始錄影
        
        Args:
            use_external_camera: 是否使用外部攝影機
            use_internal_camera: 是否使用內部攝影機
            
        Returns:
            bool: 是否成功開始錄影
        """
        try:
            if self.is_recording:
                self.logger.warning("錄影已在進行中")
                return True
            
            # 初始化攝影機
            if use_external_camera:
                if not self._init_external_camera():
                    self.logger.error("初始化外部攝影機失敗")
                    return False
            
            if use_internal_camera:
                if not self._init_internal_camera():
                    self.logger.error("初始化內部攝影機失敗")
                    # 繼續，因為外部攝影機可能仍可用
            
            if not self.external_camera and not self.internal_camera:
                self.logger.error("沒有可用的攝影機")
                return False
            
            # 啟動錄影執行緒
            self.is_recording = True
            self.stop_event.clear()
            self.recording_thread = threading.Thread(target=self._recording_worker, daemon=True)
            self.recording_thread.start()
            
            self.logger.info("行車記錄開始")
            return True
            
        except Exception as e:
            self.logger.error(f"開始錄影時發生錯誤: {e}")
            return False
    
    def stop_recording(self):
        """停止錄影"""
        try:
            if not self.is_recording:
                self.logger.warning("錄影尚未開始")
                return
            
            self.logger.info("正在停止錄影...")
            
            # 設定停止事件
            self.stop_event.set()
            self.is_recording = False
            
            # 等待錄影執行緒結束
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=5.0)
            
            # 關閉當前錄影
            self._finish_current_recording()
            
            # 釋放攝影機資源
            self._release_cameras()
            
            self.logger.info("錄影已停止")
            
        except Exception as e:
            self.logger.error(f"停止錄影時發生錯誤: {e}")
    
    def _init_external_camera(self) -> bool:
        """初始化外部攝影機"""
        try:
            self.external_camera = cv2.VideoCapture(self.config.camera.external_camera_index)
            
            if not self.external_camera.isOpened():
                self.logger.error("無法開啟外部攝影機")
                return False
            
            # 設定解析度和幀率
            self.external_camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.camera.external_camera_width)
            self.external_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.camera.external_camera_height)
            self.external_camera.set(cv2.CAP_PROP_FPS, self.config.camera.external_camera_fps)
            
            # 驗證設定
            actual_width = int(self.external_camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.external_camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.external_camera.get(cv2.CAP_PROP_FPS)
            
            self.logger.info(f"外部攝影機已初始化: {actual_width}x{actual_height} @ {actual_fps} FPS")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化外部攝影機失敗: {e}")
            return False
    
    def _init_internal_camera(self) -> bool:
        """初始化內部攝影機"""
        try:
            self.internal_camera = cv2.VideoCapture(self.config.camera.internal_camera_index)
            
            if not self.internal_camera.isOpened():
                self.logger.error("無法開啟內部攝影機")
                return False
            
            # 設定解析度和幀率
            self.internal_camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.camera.internal_camera_width)
            self.internal_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.camera.internal_camera_height)
            self.internal_camera.set(cv2.CAP_PROP_FPS, self.config.camera.internal_camera_fps)
            
            actual_width = int(self.internal_camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.internal_camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.internal_camera.get(cv2.CAP_PROP_FPS)
            
            self.logger.info(f"內部攝影機已初始化: {actual_width}x{actual_height} @ {actual_fps} FPS")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化內部攝影機失敗: {e}")
            return False
    
    def _recording_worker(self):
        """錄影工作執行緒"""
        self.logger.info("錄影工作執行緒已啟動")
        
        while not self.stop_event.is_set() and self.is_recording:
            try:
                # 開始新的錄影片段
                if not self._start_new_recording_segment():
                    self.logger.error("無法開始新的錄影片段")
                    break
                
                # 錄影指定時間
                segment_start_time = time.time()
                frame_count = 0
                
                while (time.time() - segment_start_time < self.recording_duration and 
                       not self.stop_event.is_set()):
                    
                    self.performance_monitor.start_frame()
                    
                    # 從攝影機讀取幀
                    frame_recorded = False
                    
                    if self.external_camera:
                        ret, frame = self.external_camera.read()
                        if ret and self.current_writer:
                            self.current_writer.write(frame)
                            frame_recorded = True
                            frame_count += 1
                    
                    if not frame_recorded:
                        # 如果外部攝影機失敗，嘗試使用內部攝影機
                        if self.internal_camera:
                            ret, frame = self.internal_camera.read()
                            if ret and self.current_writer:
                                self.current_writer.write(frame)
                                frame_count += 1
                    
                    self.performance_monitor.end_frame()
                    
                    # 控制幀率
                    time.sleep(1.0 / self.config.camera.external_camera_fps)
                
                # 完成當前錄影片段
                video_info = self._finish_current_recording()
                
                if video_info:
                    # 呼叫完成回調
                    if self.on_video_completed_callback:
                        try:
                            self.on_video_completed_callback(video_info)
                        except Exception as e:
                            self.logger.error(f"錄影完成回調執行錯誤: {e}")
                    
                    # 更新統計
                    with self._lock:
                        self.recording_stats['total_videos'] += 1
                        self.recording_stats['current_session_videos'] += 1
                        self.recording_stats['total_recording_time'] += self.recording_duration
                        if 'file_size' in video_info:
                            self.recording_stats['total_file_size'] += video_info['file_size']
                    
                    self.logger.info(f"錄影片段完成: {video_info['filename']} ({frame_count} 幀)")
            
            except Exception as e:
                self.logger.error(f"錄影工作執行緒錯誤: {e}")
                time.sleep(1.0)
        
        # 清理
        self._finish_current_recording()
        self.logger.info("錄影工作執行緒已結束")
    
    def _start_new_recording_segment(self) -> bool:
        """開始新的錄影片段"""
        try:
            # 生成檔案名稱
            self.current_filename = generate_video_filename('external')
            video_path = os.path.join(self.config.temp_videos_dir, self.current_filename)
            
            # 決定錄影解析度
            if self.external_camera:
                width = int(self.external_camera.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(self.external_camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = self.external_camera.get(cv2.CAP_PROP_FPS)
            elif self.internal_camera:
                width = int(self.internal_camera.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(self.internal_camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = self.internal_camera.get(cv2.CAP_PROP_FPS)
            else:
                return False
            
            # 建立 VideoWriter
            self.current_writer = cv2.VideoWriter(
                video_path,
                self.codec,
                fps,
                (width, height)
            )
            
            if not self.current_writer.isOpened():
                self.logger.error(f"無法建立影片寫入器: {video_path}")
                return False
            
            self.recording_start_time = time.time()
            self.logger.debug(f"開始錄影片段: {self.current_filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"開始新錄影片段失敗: {e}")
            return False
    
    def _finish_current_recording(self) -> Optional[Dict[str, Any]]:
        """完成當前錄影"""
        try:
            if not self.current_writer or not self.current_filename:
                return None
            
            # 釋放 VideoWriter
            self.current_writer.release()
            self.current_writer = None
            
            # 獲取檔案資訊
            video_path = os.path.join(self.config.temp_videos_dir, self.current_filename)
            
            if not os.path.exists(video_path):
                self.logger.warning(f"錄影檔案不存在: {video_path}")
                return None
            
            file_size = os.path.getsize(video_path)
            recording_duration = time.time() - self.recording_start_time if self.recording_start_time else 0
            
            video_info = {
                'filename': self.current_filename,
                'file_path': video_path,
                'file_size': file_size,
                'recording_duration': recording_duration,
                'start_time': self.recording_start_time,
                'end_time': time.time(),
                'camera_type': 'external' if self.external_camera else 'internal'
            }
            
            # 重置狀態
            self.current_filename = None
            self.recording_start_time = None
            
            return video_info
            
        except Exception as e:
            self.logger.error(f"完成錄影時發生錯誤: {e}")
            return None
    
    def _release_cameras(self):
        """釋放攝影機資源"""
        try:
            if self.external_camera:
                self.external_camera.release()
                self.external_camera = None
                self.logger.debug("外部攝影機已釋放")
            
            if self.internal_camera:
                self.internal_camera.release()
                self.internal_camera = None
                self.logger.debug("內部攝影機已釋放")
            
        except Exception as e:
            self.logger.error(f"釋放攝影機時發生錯誤: {e}")
    
    def set_video_completed_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """設定錄影完成回調函數"""
        self.on_video_completed_callback = callback
        self.logger.info("錄影完成回調函數已設定")
    
    def get_recording_stats(self) -> Dict[str, Any]:
        """獲取錄影統計資料"""
        try:
            with self._lock:
                stats = self.recording_stats.copy()
            
            # 計算運行時間
            uptime = time.time() - stats['start_time']
            stats['uptime_seconds'] = uptime
            stats['uptime_formatted'] = f"{uptime / 3600:.1f} 小時"
            
            # 計算平均檔案大小
            if stats['total_videos'] > 0:
                stats['average_file_size'] = stats['total_file_size'] / stats['total_videos']
                stats['average_file_size_formatted'] = format_file_size(stats['average_file_size'])
            else:
                stats['average_file_size'] = 0
                stats['average_file_size_formatted'] = "0 B"
            
            # 當前狀態
            stats['is_recording'] = self.is_recording
            stats['current_filename'] = self.current_filename
            
            # 格式化總大小
            stats['total_file_size_formatted'] = format_file_size(stats['total_file_size'])
            
            # 錄影效率（實際錄影時間 / 運行時間）
            if uptime > 0:
                stats['recording_efficiency'] = stats['total_recording_time'] / uptime
            else:
                stats['recording_efficiency'] = 0.0
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_video_files(self) -> List[Dict[str, Any]]:
        """獲取影片檔案列表"""
        try:
            video_files = []
            
            if not os.path.exists(self.config.temp_videos_dir):
                return video_files
            
            for filename in os.listdir(self.config.temp_videos_dir):
                if filename.lower().endswith(('.mp4', '.avi', '.mov')):
                    file_path = os.path.join(self.config.temp_videos_dir, filename)
                    
                    if os.path.isfile(file_path):
                        stat = os.stat(file_path)
                        video_files.append({
                            'filename': filename,
                            'file_path': file_path,
                            'file_size': stat.st_size,
                            'file_size_formatted': format_file_size(stat.st_size),
                            'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                            'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
            
            # 按建立時間排序
            video_files.sort(key=lambda x: x['created_time'], reverse=True)
            return video_files
            
        except Exception as e:
            self.logger.error(f"獲取影片檔案列表時發生錯誤: {e}")
            return []
    
    def cleanup_old_videos(self):
        """清理舊影片檔案"""
        try:
            deleted_count = cleanup_old_files(
                self.config.temp_videos_dir,
                self.config.recording.max_local_files,
                "*.mp4"
            )
            
            if deleted_count > 0:
                self.logger.info(f"已清理 {deleted_count} 個舊影片檔案")
                
                # 更新統計（減少檔案計數，但保留其他統計）
                with self._lock:
                    self.recording_stats['current_session_videos'] = max(
                        0, self.recording_stats['current_session_videos'] - deleted_count
                    )
            
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"清理舊影片時發生錯誤: {e}")
            return 0
    
    def test_cameras(self) -> Dict[str, bool]:
        """測試攝影機功能"""
        results = {}
        
        # 測試外部攝影機
        try:
            test_cap = cv2.VideoCapture(self.config.camera.external_camera_index)
            if test_cap.isOpened():
                ret, frame = test_cap.read()
                results['external_camera'] = ret
            else:
                results['external_camera'] = False
            test_cap.release()
        except Exception as e:
            self.logger.error(f"測試外部攝影機時發生錯誤: {e}")
            results['external_camera'] = False
        
        # 測試內部攝影機
        try:
            test_cap = cv2.VideoCapture(self.config.camera.internal_camera_index)
            if test_cap.isOpened():
                ret, frame = test_cap.read()
                results['internal_camera'] = ret
            else:
                results['internal_camera'] = False
            test_cap.release()
        except Exception as e:
            self.logger.error(f"測試內部攝影機時發生錯誤: {e}")
            results['internal_camera'] = False
        
        return results
    
    def __del__(self):
        """清理資源"""
        try:
            self.stop_recording()
        except Exception:
            pass

# 如果直接執行此檔案，則進入測試模式
if __name__ == "__main__":
    import sys
    
    print("行車記錄器測試模式")
    
    recorder = DashcamRecorder()
    
    # 測試攝影機
    print("測試攝影機...")
    camera_results = recorder.test_cameras()
    print(f"攝影機測試結果: {camera_results}")
    
    if not any(camera_results.values()):
        print("沒有可用的攝影機")
        sys.exit(1)
    
    # 設定錄影完成回調
    def on_video_completed(video_info):
        print(f"錄影完成: {video_info['filename']} ({format_file_size(video_info['file_size'])})")
    
    recorder.set_video_completed_callback(on_video_completed)
    
    # 開始錄影
    print("開始錄影測試...")
    if recorder.start_recording():
        print("錄影已開始，按 Ctrl+C 停止")
        
        try:
            while True:
                time.sleep(5)
                
                # 顯示統計
                stats = recorder.get_recording_stats()
                print(f"錄影統計: 已錄製 {stats['current_session_videos']} 個影片")
                
        except KeyboardInterrupt:
            print("用戶中斷錄影")
    
    else:
        print("無法開始錄影")
    
    # 停止錄影
    recorder.stop_recording()
    
    # 顯示最終統計
    final_stats = recorder.get_recording_stats()
    print(f"最終統計: {final_stats}")
    
    # 顯示影片檔案
    video_files = recorder.get_video_files()
    print(f"影片檔案: {len(video_files)} 個")
    for video in video_files[:5]:  # 顯示前5個
        print(f"  {video['filename']} - {video['file_size_formatted']}")
    
    print("測試結束")