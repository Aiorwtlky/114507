# test_vehicle_distance.py

import cv2
import time
from utils.vehicle_distance_detector import VehicleDistanceDetector

def test_vehicle_distance(video_path='project_video.mp4'):
    """
    測試前車距離偵測
    """
    # 初始化偵測器
    print("正在初始化前車距離偵測器...")
    detector = VehicleDistanceDetector(
        focal_length=2450,  # 預設值，實車需校準
        known_width=1.8
    )
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"❌ 無法開啟影片：{video_path}")
        return
    
    print("="*70)
    print("🚗 前車距離偵測測試")
    print("="*70)
    print("⚙️  系統參數：")
    print(f"   焦距：700 像素（預設，需校準）")
    print(f"   車寬：1.8 公尺")
    print(f"   安全距離公式：速度（km/h）÷ 10 × 3")
    print("\n🎮 操作說明：")
    print("   '+' 或 '=' - 增加車速")
    print("   '-' - 減少車速")
    print("   'q' - 退出")
    print("="*70 + "\n")
    
    frame_count = 0
    b02_count = 0
    last_b02_time = 0
    b02_cooldown = 3.0
    
    current_speed = 50  # 模擬車速（km/h）
    
    print("🎬 影片開始播放...\n")
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("\n🔄 影片結束，重新播放")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        
        frame_count += 1
        
        # 前車距離偵測
        result = detector.detect(
            frame, 
            speed_kmh=current_speed, 
            draw_visualization=True
        )
        
        # 每 30 幀輸出狀態
        if frame_count % 30 == 0:
            if result['vehicle_detected']:
                print(f"[{frame_count:4d}] "
                      f"車輛數: {result['vehicle_count']} | "
                      f"最近距離: {result['distance']:.1f}m | "
                      f"安全距離: {result['safe_distance']:.1f}m | "
                      f"車速: {current_speed}km/h | "
                      f"過近: {'是' if result['too_close'] else '否'}")
            else:
                print(f"[{frame_count:4d}] 未偵測到前車")
        
        # B02 事件觸發
        if result['too_close']:
            current_time = time.time()
            
            if current_time - last_b02_time >= b02_cooldown:
                b02_count += 1
                last_b02_time = current_time
                
                print("\n" + "="*70)
                print(f"🚨 [B02] 前車過近事件 #{b02_count}")
                print(f"├─ 當前距離：{result['distance']:.1f}m")
                print(f"├─ 安全距離：{result['safe_distance']:.1f}m")
                print(f"├─ 車速：{current_speed}km/h")
                print(f"└─ 信心度：{result['confidence']:.2f}")
                print("="*70 + "\n")
        
        # 視覺化顯示
        if result['visualization'] is not None:
            vis = result['visualization']
            
            # 顯示車速
            cv2.putText(vis, f"Speed: {current_speed}km/h", (50, 180), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            
            # B02 計數
            cv2.putText(vis, f"B02 Events: {b02_count}", (50, 220), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            
            # 偵測統計
            cv2.putText(vis, f"Vehicles: {result['vehicle_count']}", (50, 260), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
            
            cv2.imshow('Vehicle Distance Detection', vis)
        
        # 鍵盤控制
        key = cv2.waitKey(30) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('+') or key == ord('='):
            current_speed = min(current_speed + 10, 120)
            print(f"\n🚗 車速增加：{current_speed}km/h "
                  f"（安全距離：{detector.calculate_safe_distance(current_speed):.1f}m）\n")
        elif key == ord('-'):
            current_speed = max(current_speed - 10, 30)
            print(f"\n🚗 車速減少：{current_speed}km/h "
                  f"（安全距離：{detector.calculate_safe_distance(current_speed):.1f}m）\n")
    
    # 測試結果統計
    print("\n" + "="*70)
    print("📊 測試結果統計")
    print("="*70)
    print(f"總幀數：{frame_count}")
    print(f"偵測到車輛的幀數：{detector.detection_count}")
    print(f"偵測成功率：{detector.detection_count / frame_count * 100:.1f}%")
    print(f"B02 事件總數：{b02_count}")
    print("="*70)
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    test_vehicle_distance('project_video.mp4')