# test_lane_realistic.py

import cv2
import time
from utils.lane_departure_detector import LaneDepartureDetector

def test_lane_realistic(video_path='project_video.mp4'):
    """
    车道偏离测试 - 实际道路版本
    减少误报，只在真的变道时触发
    """
    detector = LaneDepartureDetector(
        skip_undistort=False, 
        departure_threshold=0.45  # 提高阈值
    )
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"无法开启影片：{video_path}")
        return
    
    print("="*70)
    print("车道偏离预警系统 - 实际道路版")
    print("="*70)
    print("系统参数：")
    print(f"   偏离阈值：0.45m（接近压线）")
    print(f"   持续时间：2.0 秒（避免过弯误报）")
    print(f"   冷却时间：5.0 秒")
    print("\n操作：'s' 方向灯 | 'o' 关灯 | 'q' 退出")
    print("="*70 + "\n")
    
    frame_count = 0
    b01_count = 0
    last_b01_time = 0
    b01_cooldown = 5.0
    
    # 新增：持续偏离计数
    consecutive_departed_frames = 0
    departure_duration_threshold = 60  # 2 秒 @ 30fps
    
    turn_signal_on = False
    
    print("影片开始播放...\n")
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("\n影片结束，重新播放")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            consecutive_departed_frames = 0
            continue
        
        frame_count += 1
        result = detector.detect(frame, draw_visualization=True)
        
        # 每 30 帧输出状态
        if frame_count % 30 == 0:
            print(f"[{frame_count:4d}] "
                  f"Offset: {result['offset']:+.3f}m | "
                  f"偏离: {'是' if result['departed'] else '否'} | "
                  f"持续: {consecutive_departed_frames} 帧 | "
                  f"方向灯: {'ON' if turn_signal_on else 'OFF'}")
        
        # 持续偏离判断
        if result['departed'] and result['confidence'] > 0.5:
            consecutive_departed_frames += 1
        else:
            consecutive_departed_frames = 0
        
        # B01 触发（新逻辑）
        if consecutive_departed_frames >= departure_duration_threshold:
            
            if not turn_signal_on:
                current_time = time.time()
                
                if current_time - last_b01_time >= b01_cooldown:
                    b01_count += 1
                    last_b01_time = current_time
                    
                    print("\n" + "="*70)
                    print(f"[B01] 车道偏离事件 #{b01_count}")
                    print(f"偏移量：{result['offset']:+.3f}m")
                    print(f"持续时间：{consecutive_departed_frames / 30:.1f} 秒")
                    print(f"方向灯：OFF")
                    print(f"违规原因：持续偏离且未打方向灯")
                    print("="*70 + "\n")
                    
                    # 重置计数（避免重复触发）
                    consecutive_departed_frames = 0
            
            else:
                if frame_count % 30 == 0:
                    print(f"   ✓ 持续偏离但有打方向灯（合法变道）")
                consecutive_departed_frames = 0
        
        # 视觉化
        if result['visualization'] is not None:
            vis = result['visualization'].copy()
            
            if turn_signal_on:
                cv2.putText(vis, "TURN SIGNAL ON", (50, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
            else:
                cv2.putText(vis, "NO SIGNAL", (50, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2)
            
            offset_color = (0, 0, 255) if result['departed'] else (0, 255, 0)
            cv2.putText(vis, f"Offset: {result['offset']:+.3f}m", (50, 200), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, offset_color, 2)
            
            cv2.putText(vis, f"B01: {b01_count}", (50, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)
            
            # 显示持续偏离时间
            if consecutive_departed_frames > 0:
                duration = consecutive_departed_frames / 30
                cv2.putText(vis, f"Duration: {duration:.1f}s", (50, 280), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            
            cv2.imshow('Lane Departure Warning', vis)
        
        # 键盘
        key = cv2.waitKey(30) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('s'):
            turn_signal_on = not turn_signal_on
            print(f"\n方向灯：{'ON' if turn_signal_on else 'OFF'}\n")
        elif key == ord('o'):
            turn_signal_on = False
            print("\n方向灯关闭\n")
    
    print("\n" + "="*70)
    print("测试结果")
    print("="*70)
    print(f"总帧数：{frame_count}")
    print(f"B01 事件：{b01_count}")
    print("="*70)
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    test_lane_realistic('project_video.mp4')