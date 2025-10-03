# utils/vehicle_distance_detector.py

import cv2
import numpy as np
from collections import deque

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("警告：未安裝 ultralytics，前車偵測將無法使用")

class VehicleDistanceDetector:
    """
    前車距離偵測器（YOLOv8）
    """
    
    def __init__(self, focal_length=700, known_width=1.8):
        """
        Args:
            focal_length: 相機焦距（像素），需要校準
            known_width: 車輛實際寬度（公尺）
        """
        if not YOLO_AVAILABLE:
            raise ImportError("請先安裝：pip install ultralytics")
        
        # 載入 YOLOv8n 模型（輕量版）
        print("正在載入 YOLOv8 模型...")
        self.model = YOLO('yolov8n.pt')
        print("模型載入完成")
        
        # 相機參數
        self.focal_length = focal_length
        self.known_width = known_width
        
        # 安全距離參數
        self.safe_distance_multiplier = 3.0  # 速度倍數
        self.min_safe_distance = 10.0  # 最小安全距離（公尺）
        
        # 滑動平均
        self.distance_history = deque(maxlen=5)
        
        # 偵測統計
        self.frame_count = 0
        self.detection_count = 0
    
    def calculate_safe_distance(self, speed_kmh=50):
        """
        計算安全距離（符合台灣道路規則）
        
        公式：速度（km/h）÷ 10 × 3
        例如：50 km/h → 15m，100 km/h → 30m
        
        Args:
            speed_kmh: 當前車速（公里/小時）
        
        Returns:
            safe_distance: 安全距離（公尺）
        """
        safe_distance = (speed_kmh / 10) * self.safe_distance_multiplier
        return max(safe_distance, self.min_safe_distance)
    
    def estimate_distance(self, bbox_width):
        """
        估算距離（三角測量）
        
        公式：距離 = (焦距 × 實際寬度) / 像素寬度
        
        Args:
            bbox_width: Bounding Box 的像素寬度
        
        Returns:
            distance: 估算距離（公尺）
        """
        if bbox_width <= 0:
            return float('inf')
        
        distance = (self.focal_length * self.known_width) / bbox_width
        return distance
    
    def detect(self, frame, speed_kmh=50, draw_visualization=False):
        """
        主偵測函數
        
        Args:
            frame: 輸入影像（BGR）
            speed_kmh: 當前車速（用於計算安全距離）
            draw_visualization: 是否繪製視覺化
        
        Returns:
            result: {
                'too_close': bool,           # 是否過近
                'distance': float,           # 距離（公尺）
                'safe_distance': float,      # 安全距離（公尺）
                'vehicle_detected': bool,    # 是否偵測到車輛
                'confidence': float,         # 信心度
                'vehicle_count': int,        # 偵測到的車輛數
                'visualization': np.array    # 視覺化影像
            }
        """
        try:
            self.frame_count += 1
            
            # YOLOv8 偵測（只偵測車輛 class=2, 3, 5, 7）
            # class 2: car, 3: motorcycle, 5: bus, 7: truck
            results = self.model(
                frame, 
                classes=[2, 3, 5, 7], 
                verbose=False,
                conf=0.5  # 信心度閾值
            )
            
            # 計算安全距離
            safe_distance = self.calculate_safe_distance(speed_kmh)
            
            # 找到最近的車輛
            closest_vehicle = None
            min_distance = float('inf')
            all_vehicles = []
            
            if len(results[0].boxes) > 0:
                self.detection_count += 1
                
                for box in results[0].boxes:
                    # 取得 Bounding Box
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    bbox_width = x2 - x1
                    bbox_height = y2 - y1
                    confidence = float(box.conf[0])
                    
                    # 過濾太小的偵測（可能是遠方車輛）
                    if bbox_width < 30 or bbox_height < 30:
                        continue
                    
                    # 估算距離
                    distance = self.estimate_distance(bbox_width)
                    
                    vehicle_info = {
                        'bbox': (int(x1), int(y1), int(x2), int(y2)),
                        'distance': distance,
                        'confidence': confidence,
                        'width': bbox_width
                    }
                    
                    all_vehicles.append(vehicle_info)
                    
                    # 記錄最近的車輛
                    if distance < min_distance:
                        min_distance = distance
                        closest_vehicle = vehicle_info
            
            # 滑動平均（只針對最近車輛）
            if closest_vehicle:
                self.distance_history.append(closest_vehicle['distance'])
                avg_distance = np.mean(self.distance_history)
            else:
                self.distance_history.clear()
                avg_distance = float('inf')
            
            # 判斷是否過近
            too_close = (
                closest_vehicle is not None and 
                avg_distance < safe_distance and
                len(self.distance_history) >= 3  # 需要穩定偵測
            )
            
            result = {
                'too_close': too_close,
                'distance': avg_distance if closest_vehicle else None,
                'safe_distance': safe_distance,
                'vehicle_detected': closest_vehicle is not None,
                'confidence': closest_vehicle['confidence'] if closest_vehicle else 0.0,
                'vehicle_count': len(all_vehicles),
                'visualization': None
            }
            
            # 視覺化
            if draw_visualization:
                result['visualization'] = self._draw_detection(
                    frame, all_vehicles, closest_vehicle, 
                    avg_distance, safe_distance, too_close
                )
            else:
                result['visualization'] = frame
            
            return result
            
        except Exception as e:
            print(f"[Vehicle Detection Error] {e}")
            return {
                'too_close': False,
                'distance': None,
                'safe_distance': safe_distance,
                'vehicle_detected': False,
                'confidence': 0.0,
                'vehicle_count': 0,
                'visualization': frame
            }
    
    def _draw_detection(self, frame, all_vehicles, closest_vehicle, 
                       distance, safe_distance, too_close):
        """繪製偵測結果"""
        vis = frame.copy()
        
        # 繪製所有車輛的 Bounding Box
        for vehicle in all_vehicles:
            x1, y1, x2, y2 = vehicle['bbox']
            
            # 判斷是否為最近車輛
            is_closest = (closest_vehicle and 
                         vehicle['bbox'] == closest_vehicle['bbox'])
            
            if is_closest:
                # 最近車輛用特殊顏色
                color = (0, 0, 255) if too_close else (0, 255, 0)
                thickness = 3
            else:
                # 其他車輛用灰色
                color = (128, 128, 128)
                thickness = 2
            
            cv2.rectangle(vis, (x1, y1), (x2, y2), color, thickness)
            
            # 距離標示
            dist_text = f"{vehicle['distance']:.1f}m"
            cv2.putText(vis, dist_text, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # 狀態資訊
        if closest_vehicle:
            status = "TOO CLOSE!" if too_close else "SAFE"
            status_color = (0, 0, 255) if too_close else (0, 255, 0)
            
            cv2.putText(vis, status, (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, status_color, 3)
            
            cv2.putText(vis, f"Distance: {distance:.1f}m", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            cv2.putText(vis, f"Safe: {safe_distance:.1f}m", (50, 140), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        else:
            cv2.putText(vis, "No Vehicle", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (100, 100, 100), 2)
        
        return vis