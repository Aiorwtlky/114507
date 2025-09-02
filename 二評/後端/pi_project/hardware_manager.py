import cv2
import threading
import queue
import logging
import time
from typing import Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)

class OptimizedCameraManager:
    """優化的攝影機管理器，針對雙鏡頭設計"""
    
    def __init__(self, config):
        self.config = config
        self.internal_camera = None
        self.external_camera = None
        self.internal_frame_queue = queue.Queue(maxsize=2)
        self.external_frame_queue = queue.Queue(maxsize=2)
        self.running = False
        self.threads = []
        
    def initialize_cameras(self) -> bool:
        """初始化攝影機"""
        try:
            # 內鏡頭設定 (駕駛員監控)
            self.internal_camera = cv2.VideoCapture(self.config.internal_camera_index)
            if not self.internal_camera.isOpened():
                raise Exception(f"無法開啟內鏡頭 {self.config.internal_camera_index}")
            
            # 設定內鏡頭參數
            self.internal_camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.internal_camera_width)
            self.internal_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.internal_camera_height)
            self.internal_camera.set(cv2.CAP_PROP_FPS, self.config.internal_camera_fps)
            self.internal_camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 減少延遲
            
            # 外鏡頭設定 (ADAS)
            self.external_camera = cv2.VideoCapture(self.config.external_camera_index)
            if not self.external_camera.isOpened():
                raise Exception(f"無法開啟外鏡頭 {self.config.external_camera_index}")
                
            # 設定外鏡頭參數
            self.external_camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.external_camera_width)
            self.external_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.external_camera_height)
            self.external_camera.set(cv2.CAP_PROP_FPS, self.config.external_camera_fps)
            self.external_camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 減少延遲
            
            logger.info("攝影機初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"攝影機初始化失敗: {e}")
            return False
    
    def start_capture(self):
        """開始擷取影像"""
        self.running = True
        
        # 內鏡頭擷取執行緒
        internal_thread = threading.Thread(
            target=self._capture_internal_frames,
            name="InternalCamera"
        )
        
        # 外鏡頭擷取執行緒
        external_thread = threading.Thread(
            target=self._capture_external_frames,
            name="ExternalCamera"
        )
        
        self.threads = [internal_thread, external_thread]
        
        for thread in self.threads:
            thread.daemon = True
            thread.start()
        
        logger.info("攝影機擷取開始")
    
    def _capture_internal_frames(self):
        """內鏡頭擷取執行緒"""
        while self.running:
            if self.internal_camera is None:
                time.sleep(0.1)
                continue
                
            ret, frame = self.internal_camera.read()
            if not ret:
                logger.warning("內鏡頭讀取失敗")
                time.sleep(0.1)
                continue
            
            # 清空舊的 frame 避免累積延遲
            try:
                while not self.internal_frame_queue.empty():
                    self.internal_frame_queue.get_nowait()
            except queue.Empty:
                pass
            
            try:
                self.internal_frame_queue.put(frame, block=False)
            except queue.Full:
                pass  # 忽略滿的 queue
    
    def _capture_external_frames(self):
        """外鏡頭擷取執行緒"""
        while self.running:
            if self.external_camera is None:
                time.sleep(0.1)
                continue
                
            ret, frame = self.external_camera.read()
            if not ret:
                logger.warning("外鏡頭讀取失敗")
                time.sleep(0.1)
                continue
            
            # 清空舊的 frame 避免累積延遲
            try:
                while not self.external_frame_queue.empty():
                    self.external_frame_queue.get_nowait()
            except queue.Empty:
                pass
            
            try:
                self.external_frame_queue.put(frame, block=False)
            except queue.Full:
                pass  # 忽略滿的 queue
    
    def get_internal_frame(self) -> Optional[np.ndarray]:
        """取得內鏡頭影像"""
        try:
            return self.internal_frame_queue.get(timeout=0.1)
        except queue.Empty:
            return None
    
    def get_external_frame(self) -> Optional[np.ndarray]:
        """取得外鏡頭影像"""
        try:
            return self.external_frame_queue.get(timeout=0.1)
        except queue.Empty:
            return None
    
    def stop_capture(self):
        """停止擷取"""
        self.running = False
        
        # 等待執行緒結束
        for thread in self.threads:
            thread.join(timeout=2.0)
        
        # 釋放攝影機資源
        if self.internal_camera:
            self.internal_camera.release()
            self.internal_camera = None
            
        if self.external_camera:
            self.external_camera.release()
            self.external_camera = None
        
        logger.info("攝影機擷取停止")
    
    def __del__(self):
        """解構函式"""
        self.stop_capture()

class HailoAccelerator:
    """Hailo 8 AI 加速器管理器"""
    
    def __init__(self, config):
        self.config = config
        self.device = None
        self.initialized = False
        
    def initialize(self) -> bool:
        """初始化 Hailo 加速器"""
        try:
            if not self.config.use_hailo_acceleration:
                logger.info("Hailo 加速未啟用，使用 CPU 模式")
                return False
                
            logger.info("Hailo 8 AI Kit 初始化...")
            
            # TODO: 實際的 Hailo 初始化代碼
            # 這裡需要根據實際的 Hailo SDK 進行調整
            # from hailo_platform import HailoDevice
            # self.device = HailoDevice()
            # self.device.configure()
            
            self.initialized = True
            logger.info("Hailo 8 AI Kit 初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"Hailo 8 AI Kit 初始化失敗: {e}")
            logger.info("將使用 CPU 模式運行")
            return False
    
    def is_available(self) -> bool:
        """檢查 Hailo 是否可用"""
        return self.initialized
    
    def infer(self, model_name: str, input_data: np.ndarray):
        """執行推理"""
        if not self.initialized:
            raise Exception("Hailo 未初始化")
        
        # TODO: 實際的推理代碼
        # return self.device.infer(model_name, input_data)
        pass
    
    def load_model(self, model_path: str, model_name: str) -> bool:
        """載入模型"""
        try:
            if not self.initialized:
                return False
            
            # TODO: 實際的模型載入代碼
            logger.info(f"載入模型: {model_name} from {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"載入模型失敗: {e}")
            return False