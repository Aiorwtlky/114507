import math
import cv2
import numpy as np
from shared import constants
from shared.constants import *  

class InnerWheelDiffROI:
    def __init__(self, axle_length, turn_angle_deg, pixels_per_meter, 
                 rear_axle_x, rear_axle_y, vehicle_length=12.0, vehicle_width=2.5, 
                 turning_direction='right'):
        """
        內輪差ROI計算器 - 側面攝影機視角
        
        Args:
            axle_length: 車軸距 (公尺)
            turn_angle_deg: 轉向角度 (度)
            pixels_per_meter: 像素/公尺比例
            rear_axle_x, rear_axle_y: 車輛後軸位置在畫面中的座標
            vehicle_length: 車身長度 (公尺) - 大型車輛約12公尺
            vehicle_width: 車身寬度 (公尺)
            turning_direction: 轉向方向 ('left' 或 'right')
        """
        self.a = axle_length  # 車軸距
        self.theta_deg = turn_angle_deg
        self.theta_rad = math.radians(turn_angle_deg)
        self.pixels_per_meter = pixels_per_meter
        self.rear_axle_x = rear_axle_x
        self.rear_axle_y = rear_axle_y
        self.vehicle_length = vehicle_length
        self.vehicle_width = vehicle_width
        self.turning_direction = turning_direction
        
        # 計算車輛關鍵點位置（像素）
        self.vehicle_length_px = int(vehicle_length * pixels_per_meter)
        self.vehicle_width_px = int(vehicle_width * pixels_per_meter)
        self.axle_length_px = int(axle_length * pixels_per_meter)
        
        # 前軸位置（假設車輛朝右，前軸在後軸右側）
        self.front_axle_x = rear_axle_x + self.axle_length_px
        self.front_axle_y = rear_axle_y
        
        # 計算轉向參數
        self.calc_turning_parameters()
        
        # 計算ROI區域
        self.roi_points = []
        self.danger_zone_points = []
        self.safe_zone_points = []
        self.calc_roi_zones()

    def calc_turning_parameters(self):
        """計算轉向參數"""
        if abs(self.theta_rad) < 0.001:  # 直行時避免除零錯誤
            self.r = float('inf')
            self.R = float('inf')
            self.r_px = 10000  # 設定一個很大的值代表直行
            self.R_px = 10000
            return
            
        # 內輪轉彎半徑 (後軸內側輪到轉向中心的距離)
        self.r = abs(self.a / math.tan(self.theta_rad))
        
        # 外輪轉彎半徑 (前軸外側輪到轉向中心的距離)
        self.R = math.sqrt(self.r**2 + self.a**2)
        
        # 轉換為像素單位
        self.r_px = int(self.r * self.pixels_per_meter)
        self.R_px = int(self.R * self.pixels_per_meter)
        
        # 車身寬度的一半（像素）
        self.half_width_px = int((self.vehicle_width / 2) * self.pixels_per_meter)

    def calc_roi_zones(self):
        """計算ROI危險區域和安全區域 - 側面視角"""
        if abs(self.theta_rad) < 0.001:  # 直行時不需要內輪差檢測
            return
            
        # 轉向中心位置計算
        if self.turning_direction == 'right':
            # 右轉：轉向中心在車輛下方
            turning_center_x = self.rear_axle_x
            turning_center_y = self.rear_axle_y + self.r_px
        else:
            # 左轉：轉向中心在車輛上方
            turning_center_x = self.rear_axle_x  
            turning_center_y = self.rear_axle_y - self.r_px
        
        # 計算轉向的角度範圍
        # 從車輛當前位置開始，到轉向角度結束
        if self.turning_direction == 'right':
            start_angle = -math.pi/2  # 從正上方開始（車輛初始方向）
            end_angle = start_angle + self.theta_rad
        else:
            start_angle = math.pi/2   # 從正下方開始
            end_angle = start_angle - self.theta_rad
        
        # 危險區域：內輪差掃過的區域
        self.danger_zone_points = self._calculate_inner_wheel_danger_zone(
            turning_center_x, turning_center_y, start_angle, end_angle
        )
        
        # 安全區域：車輛正常轉向區域
        self.safe_zone_points = self._calculate_vehicle_safe_zone(
            turning_center_x, turning_center_y, start_angle, end_angle
        )

    def _calculate_inner_wheel_danger_zone(self, center_x, center_y, start_angle, end_angle):
        """計算內輪差危險區域（車輛內側掃過但車身不會經過的區域）"""
        points = []
        num_points = 20
        
        # 內輪轉彎半徑（考慮車身寬度）
        inner_radius = max(0, self.r_px - self.half_width_px)
        # 車身內側邊緣的轉彎半徑
        vehicle_inner_radius = self.r_px
        
        # 外弧線點（車身內側邊緣）
        for i in range(num_points + 1):
            angle = start_angle + (end_angle - start_angle) * i / num_points
            x = center_x + vehicle_inner_radius * math.cos(angle)
            y = center_y + vehicle_inner_radius * math.sin(angle)
            points.append([int(x), int(y)])
        
        # 內弧線點（內輪軌跡）- 反向連接
        for i in range(num_points, -1, -1):
            angle = start_angle + (end_angle - start_angle) * i / num_points
            x = center_x + inner_radius * math.cos(angle)
            y = center_y + inner_radius * math.sin(angle)
            points.append([int(x), int(y)])
            
        return np.array(points, np.int32) if len(points) > 0 else np.array([], np.int32)

    def _calculate_vehicle_safe_zone(self, center_x, center_y, start_angle, end_angle):
        """計算車輛安全轉向區域"""
        points = []
        num_points = 20
        
        # 車身內側和外側的轉彎半徑
        inner_radius = self.r_px
        outer_radius = self.r_px + self.vehicle_width_px
        
        # 外弧線點
        for i in range(num_points + 1):
            angle = start_angle + (end_angle - start_angle) * i / num_points
            x = center_x + outer_radius * math.cos(angle)
            y = center_y + outer_radius * math.sin(angle)
            points.append([int(x), int(y)])
        
        # 內弧線點 - 反向連接
        for i in range(num_points, -1, -1):
            angle = start_angle + (end_angle - start_angle) * i / num_points
            x = center_x + inner_radius * math.cos(angle)
            y = center_y + inner_radius * math.sin(angle)
            points.append([int(x), int(y)])
            
        return np.array(points, np.int32) if len(points) > 0 else np.array([], np.int32)

    def update_parameters(self, turn_angle_deg=None, turning_direction=None, rear_axle_pos=None):
        """更新轉向參數並重新計算ROI"""
        if turn_angle_deg is not None:
            self.theta_deg = turn_angle_deg
            self.theta_rad = math.radians(turn_angle_deg)
        
        if turning_direction is not None:
            self.turning_direction = turning_direction
            
        if rear_axle_pos is not None:
            self.rear_axle_x, self.rear_axle_y = rear_axle_pos
            self.front_axle_x = self.rear_axle_x + self.axle_length_px
            self.front_axle_y = self.rear_axle_y
        
        self.calc_turning_parameters()
        self.calc_roi_zones()

    def is_point_in_danger_zone(self, x, y):
        """判斷點是否在危險區域內（內輪差區域）"""
        if len(self.danger_zone_points) == 0:
            return False
        
        result = cv2.pointPolygonTest(self.danger_zone_points, (float(x), float(y)), False)
        return result >= 0

    def is_point_in_safe_zone(self, x, y):
        """判斷點是否在安全區域內"""
        if len(self.safe_zone_points) == 0:
            return False
            
        result = cv2.pointPolygonTest(self.safe_zone_points, (float(x), float(y)), False)
        return result >= 0

    def is_point_in_roi(self, x, y):
        """判斷點是否在ROI區域內（包含危險和安全區域）"""
        return self.is_point_in_danger_zone(x, y) or self.is_point_in_safe_zone(x, y)

    def get_zone_type(self, x, y):
        """取得點所在的區域類型"""
        if self.is_point_in_danger_zone(x, y):
            return "danger"
        elif self.is_point_in_safe_zone(x, y):
            return "safe"
        else:
            return "outside"

    def draw_roi(self, frame):
        """繪製ROI區域"""
        # 繪製危險區域（紅色）
        if len(self.danger_zone_points) > 0:
            # 創建半透明覆蓋層
            overlay = frame.copy()
            cv2.fillPoly(overlay, [self.danger_zone_points], (0, 0, 255))
            cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
            cv2.polylines(frame, [self.danger_zone_points], True, (0, 0, 255), 2)
        
        # 繪製安全區域（綠色）
        if len(self.safe_zone_points) > 0:
            overlay = frame.copy()
            cv2.fillPoly(overlay, [self.safe_zone_points], (0, 255, 0))
            cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)
            cv2.polylines(frame, [self.safe_zone_points], True, (0, 255, 0), 2)
        
        # 繪製車輛關鍵點
        cv2.circle(frame, (self.rear_axle_x, self.rear_axle_y), 8, (255, 255, 0), -1)  # 後軸
        cv2.circle(frame, (self.front_axle_x, self.front_axle_y), 8, (0, 255, 255), -1)  # 前軸
        
        # 標記
        cv2.putText(frame, "Rear Axle", (self.rear_axle_x + 10, self.rear_axle_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
        cv2.putText(frame, "Front Axle", (self.front_axle_x + 10, self.front_axle_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        
        # 顯示轉向資訊
        direction_text = "右轉" if self.turning_direction == 'right' else "左轉"
        cv2.putText(frame, f"{direction_text}: {self.theta_deg}°", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        # 顯示圖例
        cv2.putText(frame, "紅色: 內輪差危險區域", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, "綠色: 車輛安全區域", (10, 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    def draw_vehicle_outline(self, frame):
        """繪製車輛輪廓 - 側面視角"""
        # 車輛矩形的四個角點（側面視角，車頭朝右）
        vehicle_corners = np.array([
            [self.rear_axle_x - self.vehicle_length_px//4, self.rear_axle_y - self.half_width_px],  # 車尾上
            [self.rear_axle_x - self.vehicle_length_px//4, self.rear_axle_y + self.half_width_px],  # 車尾下
            [self.rear_axle_x + self.vehicle_length_px*3//4, self.rear_axle_y + self.half_width_px], # 車頭下
            [self.rear_axle_x + self.vehicle_length_px*3//4, self.rear_axle_y - self.half_width_px]  # 車頭上
        ], np.int32)
        
        cv2.polylines(frame, [vehicle_corners], True, (255, 255, 255), 3)
        
        # 標示車輛方向
        arrow_start = (self.front_axle_x, self.front_axle_y)
        arrow_end = (self.front_axle_x + 30, self.front_axle_y)
        cv2.arrowedLine(frame, arrow_start, arrow_end, (255, 255, 255), 3)

    def get_roi_info(self):
        """取得ROI資訊"""
        return {
            "axle_length": self.a,
            "turn_angle": self.theta_deg,
            "turning_direction": self.turning_direction,
            "inner_radius": self.r if hasattr(self, 'r') else 0,
            "outer_radius": self.R if hasattr(self, 'R') else 0,
            "vehicle_length": self.vehicle_length,
            "vehicle_width": self.vehicle_width,
            "rear_axle_position": (self.rear_axle_x, self.rear_axle_y),
            "front_axle_position": (self.front_axle_x, self.front_axle_y)
        }