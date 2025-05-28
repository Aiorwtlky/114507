import sys
import os

# 設置工作目錄為專案根目錄
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_root)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("Current working directory:", os.getcwd())

# 匯入模組
try:
    from shared import utils
    from shared.utils import get_current_timestamp
    print("成功匯入 shared 模組")
except ImportError as e:
    print(f"匯入 shared 模組時發生錯誤: {e}")
    utils = None
    get_current_timestamp = None

import cv2
import time
import json
from camera_input import get_camera, read_frame, release_camera
from yolo_detector import detect_objects
from roi_checker import InnerWheelDiffROI
from event_manager import EventManager

def load_config():
    """載入設定檔"""
    try:
        with open('edge_device/config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("找不到 config.json，使用預設設定")
        return get_default_config()

def get_default_config():
    """預設設定"""
    return {
        "vehicle": {
            "axle_length": 6.5,      # 大型車軸距（公尺）
            "vehicle_length": 12.0,   # 車身長度（公尺）
            "vehicle_width": 2.5,     # 車身寬度（公尺）
            "turn_angle_deg": 25      # 預設轉向角度
        },
        "camera": {
            "camera_id": 1,
            "frame_width": 1280,      # 較高解析度以便看清側面細節
            "frame_height": 720,
            "pixels_per_meter": 60    # 像素/公尺比例
        },
        "roi": {
            "rear_axle_x": 200,       # 後軸在畫面中的X座標
            "rear_axle_y": 400,       # 後軸在畫面中的Y座標  
            "turning_direction": "right"  # 預設右轉
        },
        "detection": {
            "confidence_threshold": 0.5,
            "target_classes": ["person", "bicycle", "motorcycle", "car"]
        }
    }

def create_config_file():
    """建立設定檔"""
    config = get_default_config()
    os.makedirs('edge_device', exist_ok=True)
    with open('edge_device/config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    print("已建立預設 config.json")

def detect_turn_direction_and_angle(frame, previous_positions=None):
    """
    簡單的轉向偵測（可擴展為更複雜的邏輯）
    這裡先返回預設值，實際應用中可以透過：
    1. 方向盤角度感測器
    2. GPS軌跡分析
    3. 車輛CAN bus資料
    4. 影像分析等方式獲得
    """
    # 暫時返回預設值，實際應用需要接入真實感測器資料
    return "right", 25  # 右轉25度

def main():
    # 載入設定
    config = load_config()
    
    # 如果沒有設定檔，建立一個
    if not os.path.exists('edge_device/config.json'):
        create_config_file()
        config = load_config()
    
    # 從設定中讀取參數
    vehicle_config = config["vehicle"]
    camera_config = config["camera"]
    roi_config = config["roi"]
    detection_config = config["detection"]
    
    # 初始化內輪差ROI計算器
    roi = InnerWheelDiffROI(
        axle_length=vehicle_config["axle_length"],
        turn_angle_deg=vehicle_config["turn_angle_deg"],
        pixels_per_meter=camera_config["pixels_per_meter"],
        rear_axle_x=roi_config["rear_axle_x"],
        rear_axle_y=roi_config["rear_axle_y"],
        vehicle_length=vehicle_config["vehicle_length"],
        vehicle_width=vehicle_config["vehicle_width"],
        turning_direction=roi_config["turning_direction"]
    )
    
    # 事件管理
    event_manager = EventManager()

    # 開啟攝影機
    cap = get_camera(camera_config["camera_id"])
    
    # 設定攝影機解析度
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera_config["frame_width"])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_config["frame_height"])

    print("內輪差警示系統啟動")
    print("按 'ESC' 退出")
    print("按 'r' 切換右轉模式")
    print("按 'l' 切換左轉模式")
    print("按 '+'/'-' 調整轉向角度")
    
    try:
        while True:
            # 讀取影像
            frame = read_frame(cap)
            if frame is None:
                continue

            # 偵測轉向方向和角度（實際應用中應該從車輛感測器取得）
            current_direction, current_angle = detect_turn_direction_and_angle(frame)
            
            # 更新ROI參數
            roi.update_parameters(
                turn_angle_deg=current_angle,
                turning_direction=current_direction
            )

            # 偵測物件
            detections = detect_objects(frame)

            # 繪製ROI區域和車輛輪廓
            roi.draw_roi(frame)
            roi.draw_vehicle_outline(frame)

            triggered = False
            detected_objects = []

            # 遍歷所有偵測到的物件
            for det in detections:
                if det['confidence'] < detection_config["confidence_threshold"]:
                    continue
                    
                x1, y1, x2, y2 = det['bbox']
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                
                # 只檢測特定類別的物件
                if det['class'] in detection_config["target_classes"]:
                    zone_type = roi.get_zone_type(cx, cy)
                    
                    if zone_type == "danger":
                        # 在內輪差危險區域 - 最高警示
                        triggered = True
                        detected_objects.append(det)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 4)
                        cv2.putText(frame, "⚠️ 內輪差危險!", (x1, y1 - 40),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
                        # 添加閃爍效果
                        if int(time.time() * 4) % 2:  # 每0.25秒閃爍
                            cv2.rectangle(frame, (x1-5, y1-5), (x2+5, y2+5), (0, 0, 255), -1)
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 3)
                            
                    elif zone_type == "safe":
                        # 在車輛安全區域 - 中等警示
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 3)
                        cv2.putText(frame, "⚠️ 注意!", (x1, y1 - 30),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                    else:
                        # 在ROI外 - 正常標記
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # 顯示物件資訊
                    class_name = det['class']
                    confidence = det['confidence']
                    cv2.putText(frame, f"{class_name} {confidence:.2f}", 
                               (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # 危險事件處理
            if triggered and not event_manager.recording:
                if get_current_timestamp:
                    timestamp = get_current_timestamp()
                else:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    
                video_path = event_manager.start_recording(frame.shape, timestamp)
                image_path = event_manager.save_screenshot(frame, timestamp)
                
                print(f"🚨 內輪差警示觸發！")
                print(f"📹 錄影：{video_path}")
                print(f"📸 截圖：{image_path}")
                print(f"🎯 偵測物件：{[obj['class'] for obj in detected_objects]}")

            # 錄影處理
            if event_manager.recording:
                event_manager.record_frame(frame)
                if event_manager.check_recording_timeout():
                    print("📹 錄影結束")

            # 顯示系統資訊
            info_y = frame.shape[0] - 100
            cv2.putText(frame, f"轉向：{current_direction} {current_angle}°", 
                       (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"解析度：{frame.shape[1]}x{frame.shape[0]}", 
                       (10, info_y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(frame, f"FPS：{1000/max(1, cv2.getTickCount()):.1f}", 
                       (10, info_y + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # 顯示影像
            cv2.imshow("大型車輛內輪差警示系統 - 側面攝影機", frame)
            
            # 鍵盤控制
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC退出
                break
            elif key == ord('r'):  # 切換右轉
                roi.update_parameters(turning_direction='right')
                print("切換至右轉模式")
            elif key == ord('l'):  # 切換左轉
                roi.update_parameters(turning_direction='left')
                print("切換至左轉模式")
            elif key == ord('+') or key == ord('='):  # 增加角度
                new_angle = min(45, roi.theta_deg + 5)
                roi.update_parameters(turn_angle_deg=new_angle)
                print(f"轉向角度：{new_angle}°")
            elif key == ord('-'):  # 減少角度
                new_angle = max(5, roi.theta_deg - 5)
                roi.update_parameters(turn_angle_deg=new_angle)
                print(f"轉向角度：{new_angle}°")

    except KeyboardInterrupt:
        print("\n收到中斷信號，正在關閉系統...")
    finally:
        # 清理資源
        if event_manager.recording:
            event_manager.stop_recording()
        release_camera(cap)
        cv2.destroyAllWindows()
        print("系統已安全關閉")

if __name__ == "__main__":
    main()