# core/video_recorder.py
"""
影片錄製管理
根據設定決定要錄製哪些鏡頭
"""

import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
import configparser


class VideoRecorder:
    def __init__(self, config_path: str = "config.ini"):
        """
        初始化影片錄製器
        
        Args:
            config_path: 設定檔路徑
        """
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        # 讀取錄影設定
        self.record_inner = self.config.getboolean('recording', 'record_inner_camera', fallback=False)
        self.record_outer = self.config.getboolean('recording', 'record_outer_camera', fallback=True)
        self.fps = self.config.getint('recording', 'fps', fallback=30)
        self.resolution = (
            self.config.getint('recording', 'resolution_width', fallback=1920),
            self.config.getint('recording', 'resolution_height', fallback=1080)
        )
        self.codec = self.config.get('recording', 'codec', fallback='h264')
        
        # VideoWriter 物件
        self.inner_writer: Optional[cv2.VideoWriter] = None
        self.outer_writer: Optional[cv2.VideoWriter] = None
        
        # 錄影狀態
        self.is_recording = False
        self.inner_video_path: Optional[Path] = None
        self.outer_video_path: Optional[Path] = None
        self.start_time: Optional[datetime] = None
        
        print(f"[VideoRecorder] Initialized")
        print(f"  - Record Inner: {self.record_inner}")
        print(f"  - Record Outer: {self.record_outer}")
        print(f"  - FPS: {self.fps}, Resolution: {self.resolution}")
    
    def start_recording(self, inner_path: Optional[Path] = None, outer_path: Optional[Path] = None):
        """
        開始錄影
        
        Args:
            inner_path: 內鏡頭影片儲存路徑
            outer_path: 外鏡頭影片儲存路徑
        """
        if self.is_recording:
            print("[VideoRecorder] Already recording!")
            return
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 或使用 'avc1' (H.264)
        
        # 建立內鏡頭 Writer
        if self.record_inner and inner_path:
            self.inner_video_path = inner_path
            self.inner_writer = cv2.VideoWriter(
                str(inner_path),
                fourcc,
                self.fps,
                self.resolution
            )
            if not self.inner_writer.isOpened():
                print(f"[VideoRecorder] ERROR: Failed to open inner video writer: {inner_path}")
                self.inner_writer = None
            else:
                print(f"[VideoRecorder] Started recording inner camera: {inner_path}")
        
        # 建立外鏡頭 Writer
        if self.record_outer and outer_path:
            self.outer_video_path = outer_path
            self.outer_writer = cv2.VideoWriter(
                str(outer_path),
                fourcc,
                self.fps,
                self.resolution
            )
            if not self.outer_writer.isOpened():
                print(f"[VideoRecorder] ERROR: Failed to open outer video writer: {outer_path}")
                self.outer_writer = None
            else:
                print(f"[VideoRecorder] Started recording outer camera: {outer_path}")
        
        self.is_recording = True
        self.start_time = datetime.now()
    
    def write_frame(self, inner_frame: Optional[np.ndarray] = None, outer_frame: Optional[np.ndarray] = None):
        """
        寫入一幀影像
        
        Args:
            inner_frame: 內鏡頭影像
            outer_frame: 外鏡頭影像
        """
        if not self.is_recording:
            return
        
        # 寫入內鏡頭
        if self.inner_writer and inner_frame is not None:
            # 確保尺寸正確
            if inner_frame.shape[1] != self.resolution[0] or inner_frame.shape[0] != self.resolution[1]:
                inner_frame = cv2.resize(inner_frame, self.resolution)
            self.inner_writer.write(inner_frame)
        
        # 寫入外鏡頭
        if self.outer_writer and outer_frame is not None:
            # 確保尺寸正確
            if outer_frame.shape[1] != self.resolution[0] or outer_frame.shape[0] != self.resolution[1]:
                outer_frame = cv2.resize(outer_frame, self.resolution)
            self.outer_writer.write(outer_frame)
    
    def stop_recording(self) -> Tuple[Optional[Path], Optional[Path]]:
        """
        停止錄影
        
        Returns:
            (inner_video_path, outer_video_path)
        """
        if not self.is_recording:
            print("[VideoRecorder] Not recording!")
            return None, None
        
        # 釋放 Writer
        if self.inner_writer:
            self.inner_writer.release()
            print(f"[VideoRecorder] Stopped recording inner camera: {self.inner_video_path}")
        
        if self.outer_writer:
            self.outer_writer.release()
            print(f"[VideoRecorder] Stopped recording outer camera: {self.outer_video_path}")
        
        self.is_recording = False
        
        inner_path = self.inner_video_path
        outer_path = self.outer_video_path
        
        # 重置狀態
        self.inner_writer = None
        self.outer_writer = None
        self.inner_video_path = None
        self.outer_video_path = None
        self.start_time = None
        
        return inner_path, outer_path
    
    def get_recording_duration(self) -> float:
        """
        取得目前錄影時長（秒）
        
        Returns:
            錄影時長（秒）
        """
        if not self.is_recording or not self.start_time:
            return 0.0
        
        return (datetime.now() - self.start_time).total_seconds()
    
    def is_recording_active(self) -> bool:
        """檢查是否正在錄影"""
        return self.is_recording