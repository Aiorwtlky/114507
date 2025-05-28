import sys
import os

# 設置工作目錄為專案根目錄
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 取得專案根目錄
os.chdir(project_root)  # 確保工作目錄是專案根目錄

# 確保將專案根目錄加入到 sys.path，這樣 Python 會正確匯入專案內的模組
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 確認當前工作目錄
print("Current working directory:", os.getcwd())

# 現在可以正確匯入 shared 模組
try:
    from shared import utils
    from shared.utils import get_current_timestamp
    print("成功匯入 shared 模組")
except ImportError as e:
    print(f"匯入 shared 模組時發生錯誤: {e}")
    # 如果匯入失敗，繼續執行但不使用 shared 模組的功能
    utils = None
    get_current_timestamp = None

import cv2
import time
from camera_input import get_camera, read_frame, release_camera
from yolo_detector import detect_objects
from roi_checker import InnerWheelDiffROI
from event_manager import EventManager

def main():
    # 參數設定
    axle_length = 3.5  # 公尺
    turn_angle_deg = 30
    pixels_per_meter = 50
    frame_width = 640
    frame_height = 480
    center_x = frame_width // 2
    center_y = frame_height - 50

    # 計算內輪差ROI
    roi = InnerWheelDiffROI(axle_length, turn_angle_deg, pixels_per_meter, center_x, center_y)
    
    # 事件管理
    event_manager = EventManager()

    # 開啟攝影機
    cap = get_camera(1)

    try:
        while True:
            # 讀取影像
            frame = read_frame(cap)

            # 偵測物件
            detections = detect_objects(frame)

            # 繪製ROI區域
            roi.draw_roi(frame)

            triggered = False
            detected_objects = []

            # 遍歷所有偵測到的物件
            for det in detections:
                x1, y1, x2, y2 = det['bbox']
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                if det['class'] in ['person', 'bicycle', 'motorcycle']:
                    if roi.is_point_in_roi(cx, cy):  # 判斷是否進入內輪差區域
                        triggered = True
                        detected_objects.append(det)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    else:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"{det['class']} {det['confidence']:.2f}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # 當觸發警示時，開始錄影與截圖
            if triggered and not event_manager.recording:
                # 優先使用 shared 模組的時間格式化函數
                if get_current_timestamp:
                    timestamp = get_current_timestamp()
                else:
                    # 備用：使用內建的時間格式化
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    
                video_path = event_manager.start_recording(frame.shape, timestamp)
                image_path = event_manager.save_screenshot(frame, timestamp)
                print(f"警示觸發：錄影 {video_path}，截圖 {image_path}")
                print("偵測物件：", detected_objects)

            # 若正在錄影，持續寫入錄影檔
            if event_manager.recording:
                event_manager.record_frame(frame)
                if event_manager.check_recording_timeout():
                    print("錄影結束")

            # 顯示影像
            cv2.imshow("內輪差警示系統", frame)
            if cv2.waitKey(1) == 27:  # 按下ESC退出
                break

    finally:
        # 釋放攝影機
        release_camera(cap)

if __name__ == "__main__":
    main()