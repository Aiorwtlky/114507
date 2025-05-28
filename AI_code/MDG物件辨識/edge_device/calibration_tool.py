import cv2
import json
import os
import sys
from roi_checker import InnerWheelDiffROI

class ROICalibrationTool:
    def __init__(self, config_path='edge_device/config.json'):
        self.config_path = config_path
        self.load_config()
        
        # 校正狀態
        self.calibration_mode = True
        self.dragging = False
        self.drag_start = None
        self.selected_point = None
        
        # 可調整的關鍵點
        self.adjustment_points = {
            'rear_axle': [self.config['roi']['rear_axle_x'], self.config['roi']['rear_axle_y']],
            'scale_ref': [400, 300]  # 比例參考點
        }
        
        # 初始化ROI
        self.init_roi()
        
    def load_config(self):
        """載入設定檔"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"找不到設定檔：{self.config_path}")
            sys.exit(1)
    
    def save_config(self):
        """儲存設定檔"""
        # 更新設定
        self.config['roi']['rear_axle_x'] = int(self.adjustment_points['rear_axle'][0])
        self.config['roi']['rear_axle_y'] = int(self.adjustment_points['rear_axle'][1])
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
        print("設定已儲存至", self.config_path)
    
    def init_roi(self):
        """初始化ROI計算器"""
        vehicle_config = self.config["vehicle"]
        camera_config = self.config["camera"]
        roi_config = self.config["roi"]
        
        self.roi = InnerWheelDiffROI(
            axle_length=vehicle_config["axle_length"],
            turn_angle_deg=vehicle_config["turn_angle_deg"],
            pixels_per_meter=camera_config["pixels_per_meter"],
            rear_axle_x=self.adjustment_points['rear_axle'][0],
            rear_axle_y=self.adjustment_points['rear_axle'][1],
            vehicle_length=vehicle_config["vehicle_length"],
            vehicle_width=vehicle_config["vehicle_width"],
            turning_direction=roi_config["turning_direction"]
        )
    
    def mouse_callback(self, event, x, y, flags, param):
        """滑鼠事件處理"""
        if event == cv2.EVENT_LBUTTONDOWN:
            # 檢查是否點擊在調整點附近
            for point_name, point_pos in self.adjustment_points.items():
                if abs(x - point_pos[0]) < 15 and abs(y - point_pos[1]) < 15:
                    self.dragging = True
                    self.selected_point = point_name
                    self.drag_start = (x, y)
                    break
        
        elif event == cv2.EVENT_MOUSEMOVE and self.dragging:
            if self.selected_point:
                # 更新選中點的位置
                self.adjustment_points[self.selected_point] = [x, y]
                
                # 如果是後軸位置，更新ROI
                if self.selected_point == 'rear_axle':
                    self.roi.update_parameters(rear_axle_pos=(x, y))
        
        elif event == cv2.EVENT_LBUTTONUP:
            self.dragging = False
            self.selected_point = None
            self.drag_start = None
    
    def draw_calibration_interface(self, frame):
        """繪製校正介面"""
        # 繪製ROI區域
        self.roi.draw_roi(frame)
        self.roi.draw_vehicle_outline(frame)
        
        # 繪製可調整的關鍵點
        for point_name, point_pos in self.adjustment_points.items():
            x, y = int(point_pos[0]), int(point_pos[1])
            
            if point_name == 'rear_axle':
                color = (0, 255, 255)  # 黃色
                label = "後軸位置 (可拖拉)"
            else:
                color = (255, 0, 255)  # 紫色
                label = "比例參考點"
            
            # 繪製十字標記
            cv2.line(frame, (x-10, y), (x+10, y), color, 2)
            cv2.line(frame, (x, y-10), (x, y+10), color, 2)
            cv2.circle(frame, (x, y), 8, color, 2)
            
            # 標籤
            cv2.putText(frame, label, (x + 15, y), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.5, color, 1)
        
        # 繪製校正說明
        instructions = [
            "ROI 校正工具",
            "拖拉黃色十字調整後軸位置",
            "按鍵操作：",
            "  R/L: 切換轉向方向",
            "  +/-: 調整轉向角度",
            "  S: 儲存設定",
            "  ESC: 退出",
            f"當前轉向：{self.roi.turning_direction} {self.roi.theta_deg}°"
        ]
        
        y_offset = 30
        for i, instruction in enumerate(instructions):
            color = (0, 255, 255) if i == 0 else (255, 255, 255)
            thickness = 2 if i == 0 else 1
            cv2.putText(frame, instruction, (10, y_offset + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, thickness)
        
        # 顯示目前座標
        rear_x, rear_y = self.adjustment_points['rear_axle']
        cv2.putText(frame, f"後軸座標: ({int(rear_x)}, {int(rear_y)})", 
                   (10, frame.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.6, (0, 255, 255), 2)
    
    def draw_reference_grid(self, frame):
        """繪製參考網格"""
        height, width = frame.shape[:2]
        
        # 垂直線
        for x in range(0, width, 50):
            cv2.line(frame, (x, 0), (x, height), (100, 100, 100), 1)
            if x % 100 == 0:
                cv2.putText(frame, str(x), (x + 2, 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
        
        # 水平線
        for y in range(0, height, 50):
            cv2.line(frame, (0, y), (width, y), (100, 100, 100), 1)
            if y % 100 == 0:
                cv2.putText(frame, str(y), (5, y - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
    
    def run(self, camera_id=1):
        """執行校正工具"""
        # 開啟攝影機
        cap = cv2.VideoCapture(camera_id)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config['camera']['frame_width'])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config['camera']['frame_height'])
        
        # 設定滑鼠回調
        window_name = "ROI 校正工具"
        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, self.mouse_callback)
        
        print("ROI 校正工具啟動")
        print("請拖拉黃色十字標記來調整後軸位置")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("無法讀取攝影機影像")
                    break
                
                # 繪製參考網格
                self.draw_reference_grid(frame)
                
                # 繪製校正介面
                self.draw_calibration_interface(frame)
                
                # 顯示影像
                cv2.imshow(window_name, frame)
                
                # 鍵盤控制
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC
                    break
                elif key == ord('s') or key == ord('S'):  # 儲存
                    self.save_config()
                elif key == ord('r') or key == ord('R'):  # 右轉
                    self.roi.update_parameters(turning_direction='right')
                    print("切換至右轉模式")
                elif key == ord('l') or key == ord('L'):  # 左轉
                    self.roi.update_parameters(turning_direction='left')
                    print("切換至左轉模式")
                elif key == ord('+') or key == ord('='):  # 增加角度
                    new_angle = min(45, self.roi.theta_deg + 5)
                    self.roi.update_parameters(turn_angle_deg=new_angle)
                    print(f"轉向角度：{new_angle}°")
                elif key == ord('-'):  # 減少角度
                    new_angle = max(5, self.roi.theta_deg - 5)
                    self.roi.update_parameters(turn_angle_deg=new_angle)
                    print(f"轉向角度：{new_angle}°")
                    
        finally:
            cap.release()
            cv2.destroyAllWindows()

def main():
    """校正工具主程式"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ROI 校正工具')
    parser.add_argument('--camera', type=int, default=1, help='攝影機編號')
    parser.add_argument('--config', type=str, default='edge_device/config.json', 
                       help='設定檔路徑')
    
    args = parser.parse_args()
    
    # 確保設定檔存在
    if not os.path.exists(args.config):
        print(f"找不到設定檔：{args.config}")
        print("請先執行 run.py 來建立預設設定檔")
        return
    
    # 啟動校正工具
    calibration_tool = ROICalibrationTool(args.config)
    calibration_tool.run(args.camera)

if __name__ == "__main__":
    main()