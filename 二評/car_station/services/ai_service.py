# services/ai_service.py
"""
統一 AI 服務
整合所有 AI 偵測器和評分系統
"""

import threading
import time
from datetime import datetime

from ai_core.camera_manager import CameraManager
from ai_core.frame_processor import FrameProcessor
from ai_core.event_dispatcher import EventDispatcher

from detectors.inside.drowsiness_detector import DrowsinessDetector
from detectors.inside.phone_detector import PhoneDetector
from detectors.inside.attention_detector import AttentionDetector
from detectors.outside.lane_detector import LaneDetector
from detectors.outside.distance_detector import DistanceDetector

from scoring.interval_manager import IntervalManager
from scoring.score_calculator import ScoreCalculator

class AIService:
    """統一 AI 服務"""
    
    def __init__(self, trip_id):
        """
        初始化 AI 服務
        
        Args:
            trip_id: 行程 ID
        """
        self.trip_id = trip_id
        
        # 攝影機管理器
        self.inside_camera = None
        self.outside_camera = None
        
        # 偵測器
        self.drowsiness_detector = None
        self.phone_detector = None
        self.attention_detector = None
        self.lane_detector = None
        self.distance_detector = None
        
        # 幀處理器
        self.processors = []
        
        # 事件分發器
        self.event_dispatcher = None
        
        # 區間管理器
        self.interval_manager = None
        
        # 狀態
        self.is_running = False
        
        # GPIO 狀態快取（從外部更新）
        self.gpio_status = {
            'left_turn_signal': False,
            'right_turn_signal': False,
            'vehicle_speed': 50
        }
    
    def start(self):
        """啟動 AI 服務"""
        if self.is_running:
            print("[AIService] 服務已在運行中")
            return False
        
        print(f"[AIService] 啟動 AI 服務 (Trip {self.trip_id})...")
        
        try:
            # 1. 啟動攝影機
            self.inside_camera = CameraManager('inside')
            self.outside_camera = CameraManager('outside')
            
            if not self.inside_camera.start():
                raise Exception("內鏡頭啟動失敗")
            if not self.outside_camera.start():
                raise Exception("外鏡頭啟動失敗")
            
            # 2. 初始化偵測器
            self.drowsiness_detector = DrowsinessDetector()
            self.phone_detector = PhoneDetector()
            self.attention_detector = AttentionDetector()
            self.lane_detector = LaneDetector()
            self.distance_detector = DistanceDetector()
            
            # 3. 啟動事件分發器
            self.event_dispatcher = EventDispatcher(self.trip_id)
            self.event_dispatcher.start()
            
            # 4. 建立並啟動幀處理器
            # 內鏡頭處理器
            drowsiness_processor = FrameProcessor(self.drowsiness_detector, process_fps=10)
            drowsiness_processor.start(self.inside_camera)
            self.processors.append(drowsiness_processor)
            
            phone_processor = FrameProcessor(self.phone_detector, process_fps=5)
            phone_processor.start(self.inside_camera)
            self.processors.append(phone_processor)
            
            attention_processor = FrameProcessor(self.attention_detector, process_fps=10)
            attention_processor.start(self.inside_camera)
            self.processors.append(attention_processor)
            
            # 外鏡頭處理器（需要傳入 GPIO 狀態）
            lane_processor = FrameProcessor(self._create_lane_wrapper(), process_fps=5)
            lane_processor.start(self.outside_camera)
            self.processors.append(lane_processor)
            
            distance_processor = FrameProcessor(self._create_distance_wrapper(), process_fps=3)
            distance_processor.start(self.outside_camera)
            self.processors.append(distance_processor)
            
            # 5. 啟動結果收集執行緒
            self.is_running = True
            self.collector_thread = threading.Thread(target=self._collect_results, daemon=True)
            self.collector_thread.start()
            
            # 6. 啟動區間管理器
            self.interval_manager = IntervalManager(self.trip_id, interval_minutes=15)
            self.interval_manager.start()
            
            print("[AIService] AI 服務啟動成功 ✅")
            return True
            
        except Exception as e:
            print(f"[AIService] 啟動失敗: {e}")
            self.stop()
            return False
    
    def stop(self):
        """停止 AI 服務"""
        print("[AIService] 停止 AI 服務...")
        
        self.is_running = False
        
        # 停止區間管理器
        if self.interval_manager:
            self.interval_manager.stop()
        
        # 停止幀處理器
        for processor in self.processors:
            processor.stop()
        
        # 停止事件分發器
        if self.event_dispatcher:
            self.event_dispatcher.stop()
        
        # 停止攝影機
        if self.inside_camera:
            self.inside_camera.stop()
        if self.outside_camera:
            self.outside_camera.stop()
        
        # 計算最終評分
        ScoreCalculator.update_trip_score(self.trip_id)
        
        print("[AIService] AI 服務已停止")
    
    def _create_lane_wrapper(self):
        """建立車道偵測器包裝器（注入 GPIO 狀態）"""
        class LaneDetectorWrapper:
            def __init__(self, detector, gpio_getter):
                self.detector = detector
                self.gpio_getter = gpio_getter
                self.__class__.__name__ = 'LaneDetector'
            
            def initialize(self):
                return self.detector.initialize()
            
            def detect(self, frame, timestamp=None):
                gpio = self.gpio_getter()
                return self.detector.detect(
                    frame=frame,
                    timestamp=timestamp,
                    left_turn_signal=gpio['left_turn_signal'],
                    right_turn_signal=gpio['right_turn_signal']
                )
        
        return LaneDetectorWrapper(self.lane_detector, lambda: self.gpio_status)
    
    def _create_distance_wrapper(self):
        """建立距離偵測器包裝器（注入車速）"""
        class DistanceDetectorWrapper:
            def __init__(self, detector, gpio_getter):
                self.detector = detector
                self.gpio_getter = gpio_getter
                self.__class__.__name__ = 'DistanceDetector'
            
            def initialize(self):
                return self.detector.initialize()
            
            def detect(self, frame, timestamp=None):
                gpio = self.gpio_getter()
                return self.detector.detect(
                    frame=frame,
                    timestamp=timestamp,
                    vehicle_speed=gpio['vehicle_speed']
                )
        
        return DistanceDetectorWrapper(self.distance_detector, lambda: self.gpio_status)
    
    def _collect_results(self):
        """收集所有偵測器的結果並分發事件"""
        while self.is_running:
            try:
                for processor in self.processors:
                    result = processor.get_result(timeout=0.01)
                    
                    if result and result.get('event_detected'):
                        # 分發事件到資料庫
                        self.event_dispatcher.dispatch_event({
                            'rule_id': result['rule_id'],
                            'timestamp': result['timestamp'],
                            'confidence': result['confidence'],
                            'detection_data': result['detection_data']
                        })
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"[AIService] 收集結果錯誤: {e}")
                time.sleep(0.5)
    
    def update_gpio_status(self, left_turn, right_turn, speed):
        """
        更新 GPIO 狀態（從外部呼叫）
        
        Args:
            left_turn: 左轉燈狀態
            right_turn: 右轉燈狀態
            speed: 車速 (km/h)
        """
        self.gpio_status = {
            'left_turn_signal': left_turn,
            'right_turn_signal': right_turn,
            'vehicle_speed': speed
        }
    
    def get_status(self):
        """取得 AI 服務狀態"""
        status = {
            'is_running': self.is_running,
            'trip_id': self.trip_id,
            'cameras': {},
            'detectors': {},
            'event_dispatcher': {},
            'interval': {}
        }
        
        if self.inside_camera:
            status['cameras']['inside'] = self.inside_camera.get_status()
        if self.outside_camera:
            status['cameras']['outside'] = self.outside_camera.get_status()
        
        for processor in self.processors:
            detector_name = processor.detector.__class__.__name__
            status['detectors'][detector_name] = processor.get_status()
        
        if self.event_dispatcher:
            status['event_dispatcher'] = self.event_dispatcher.get_status()
        
        if self.interval_manager:
            status['interval'] = self.interval_manager.get_current_interval_info()
        
        return status