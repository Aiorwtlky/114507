# utils/unified_ai_detector.py
"""
統一 AI 偵測系統
整合所有偵測器，提供單一接口
"""

import cv2
import numpy as np
from datetime import datetime
from typing import Dict, Optional, List

from utils.drowsiness_detector import get_drowsiness_detector
from utils.lane_departure_detector import get_lane_detector
from utils.vehicle_traffic_detector import get_vehicle_traffic_detector


class UnifiedAIDetector:
    """統一 AI 偵測系統"""
    
    def __init__(self, driver_id=None):
        """
        初始化統一偵測系統
        
        Args:
            driver_id: 駕駛員 ID（用於個體化校準）
        """
        self.driver_id = driver_id
        
        # 初始化各偵測器（懶加載）
        self.drowsiness_detector = None
        self.lane_detector = None
        self.vehicle_detector = None
        
        # 事件定義映射（與你的資料庫標準一致）
        self.event_mapping = {
            # 疲勞駕駛
            'drowsy_severe': {
                'code': 'A01',
                'description': '重度疲勞駕駛 (閉眼超過3秒)',
                'points': 25
            },
            'drowsy_moderate': {
                'code': 'A02',
                'description': '中度疲勞駕駛 (閉眼1-3秒)',
                'points': 15
            },
            'drowsy_mild': {
                'code': 'A02',  # 使用 A02
                'description': '中度疲勞駕駛 (閉眼1-3秒)',
                'points': 15
            },
            
            # 分心（頭部低垂視為分心）
            'drowsy_head_drop': {
                'code': 'A03',
                'description': '長時間分心 (低頭/轉頭超過5秒)',
                'points': 20
            },
            
            # 車道偏離
            'lane_departure_left': {
                'code': 'B01',
                'description': '車道偏離 (未打方向燈)',
                'points': 5
            },
            'lane_departure_right': {
                'code': 'B01',
                'description': '車道偏離 (未打方向燈)',
                'points': 5
            },
            
            # 前車過近
            'tailgating': {
                'code': 'B02',
                'description': '前車過近',
                'points': 15
            },
            
            # 闖紅燈
            'red_light_violation': {
                'code': 'B03',
                'description': '闖紅燈',
                'points': 30
            }
        }
    
    def _init_drowsiness_detector(self):
        """初始化疲勞偵測器"""
        if self.drowsiness_detector is None:
            self.drowsiness_detector = get_drowsiness_detector(self.driver_id)
    
    def _init_lane_detector(self):
        """初始化車道偵測器"""
        if self.lane_detector is None:
            self.lane_detector = get_lane_detector()
    
    def _init_vehicle_detector(self):
        """初始化車輛偵測器"""
        if self.vehicle_detector is None:
            self.vehicle_detector = get_vehicle_traffic_detector()
    
    def detect_inside_camera(self, frame: np.ndarray) -> Optional[Dict]:
        """
        內鏡頭偵測（駕駛行為）
        
        Args:
            frame: OpenCV 影像幀
            
        Returns:
            dict: 偵測到的事件（如果有）
        """
        self._init_drowsiness_detector()
        
        # 執行疲勞偵測
        result = self.drowsiness_detector.detect(frame)
        
        # 校準中
        if result.get('status') == 'calibrating':
            return None
        
        # 未偵測到臉部
        if result.get('status') == 'no_face':
            return None
        
        # 檢查是否有事件
        if result.get('drowsiness_level', 0) > 0:
            event_type = result.get('event_type')
            
            if event_type and event_type in self.event_mapping:
                event_def = self.event_mapping[event_type]
                
                return {
                    'camera_type': 'inside',
                    'event_number': event_def['code'],
                    'event_description': event_def['description'],
                    'timestamp': datetime.now().isoformat(),
                    'confidence_score': result.get('confidence', 0.7),
                    'deduction_points': event_def['points'],
                    'event_details': {
                        'drowsiness_level': result['drowsiness_level'],
                        'metrics': result.get('metrics', {})
                    },
                    'local_image_path': None
                }
        
        return None
    
    def detect_outside_camera(
        self, 
        frame: np.ndarray,
        left_turn_signal: bool = False,
        right_turn_signal: bool = False,
        vehicle_speed: float = 0.0
    ) -> Optional[List[Dict]]:
        """
        外鏡頭偵測（道路狀況）
        
        Args:
            frame: OpenCV 影像幀
            left_turn_signal: 左方向燈狀態（從 GPIO）
            right_turn_signal: 右方向燈狀態（從 GPIO）
            vehicle_speed: 車速（km/h，從 GPS）
            
        Returns:
            list: 偵測到的事件列表
        """
        events = []
        
        # 1. 車道偏離偵測
        self._init_lane_detector()
        lane_result = self.lane_detector.detect(
            frame, 
            left_turn_signal, 
            right_turn_signal
        )
        
        if lane_result.get('event_triggered'):
            event_type = lane_result['event_type']
            
            if event_type in self.event_mapping:
                event_def = self.event_mapping[event_type]
                
                events.append({
                    'camera_type': 'outside',
                    'event_number': event_def['code'],
                    'event_description': event_def['description'],
                    'timestamp': datetime.now().isoformat(),
                    'confidence_score': lane_result.get('confidence', 0.7),
                    'deduction_points': event_def['points'],
                    'event_details': {
                        'metrics': lane_result.get('metrics', {}),
                        'turn_signals': lane_result.get('turn_signals', {})
                    },
                    'local_image_path': None
                })
        
        # 2. 前車與交通號誌偵測
        self._init_vehicle_detector()
        vehicle_result = self.vehicle_detector.detect(frame)
        
        if vehicle_result.get('status') == 'detected':
            for event in vehicle_result.get('events', []):
                event_type = event['event_type']
                
                # 前車過近
                if event_type == 'tailgating':
                    event_def = self.event_mapping['tailgating']
                    
                    events.append({
                        'camera_type': 'outside',
                        'event_number': event_def['code'],
                        'event_description': event_def['description'],
                        'timestamp': datetime.now().isoformat(),
                        'confidence_score': event.get('confidence', 0.75),
                        'deduction_points': event_def['points'],
                        'event_details': {
                            'distance': event.get('distance'),
                            'safe_distance': event.get('safe_distance'),
                            'vehicle_info': event.get('vehicle_info')
                        },
                        'local_image_path': None
                    })
                
                # 紅燈偵測（需結合車速判斷闖紅燈）
                elif event_type == 'red_light_detected':
                    # 只有在移動中（車速 > 5 km/h）才算闖紅燈
                    if vehicle_speed > 5:
                        event_def = self.event_mapping['red_light_violation']
                        
                        events.append({
                            'camera_type': 'outside',
                            'event_number': event_def['code'],
                            'event_description': event_def['description'],
                            'timestamp': datetime.now().isoformat(),
                            'confidence_score': event.get('confidence', 0.80),
                            'deduction_points': event_def['points'],
                            'event_details': {
                                'vehicle_speed': vehicle_speed,
                                'red_lights': event.get('red_lights')
                            },
                            'local_image_path': None
                        })
        
        return events if events else None
    
    def calibrate_driver(self, frame: np.ndarray) -> Dict:
        """
        駕駛員校準程序
        
        在行程開始時進行，建立個體化基準
        
        Args:
            frame: 內鏡頭影像幀
            
        Returns:
            dict: 校準狀態
        """
        self._init_drowsiness_detector()
        
        result = self.drowsiness_detector.detect(frame)
        
        if result.get('status') == 'calibrating':
            return {
                'status': 'calibrating',
                'progress': result['progress'],
                'required': result['required'],
                'message': f"正在校準... {result['progress']}/{result['required']}"
            }
        else:
            return {
                'status': 'completed',
                'message': '校準完成',
                'baseline_ear': self.drowsiness_detector.baseline_ear
            }
    
    def reset_all(self):
        """重置所有偵測器狀態"""
        if self.drowsiness_detector:
            self.drowsiness_detector.ear_history.clear()
            self.drowsiness_detector.blink_history.clear()
            self.drowsiness_detector.consecutive_closed_frames = 0
        
        if self.lane_detector:
            self.lane_detector.left_lane_history.clear()
            self.lane_detector.right_lane_history.clear()
            self.lane_detector.vehicle_position_history.clear()
        
        if self.vehicle_detector:
            self.vehicle_detector.tracked_vehicles.clear()
            self.vehicle_detector.traffic_light_history.clear()


# 全域單例
_unified_detector = None

def get_unified_detector(driver_id=None):
    """取得統一偵測系統的單例"""
    global _unified_detector
    if _unified_detector is None or (driver_id and _unified_detector.driver_id != driver_id):
        _unified_detector = UnifiedAIDetector(driver_id)
    return _unified_detector