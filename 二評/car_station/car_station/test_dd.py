# test_drowsiness.py - 完整測試腳本
import cv2
import sys
from utils.drowsiness_detector import PersonalizedDrowsinessDetector

def main():
    # 初始化
    detector = PersonalizedDrowsinessDetector('TEST001')
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ 錯誤：無法開啟攝影機")
        print("   請檢查：")
        print("   1. 攝影機是否正確連接")
        print("   2. 是否有其他程式正在使用攝影機")
        print("   3. 攝影機驅動是否正常")
        return
    
    print("=" * 60)
    print("疲勞駕駛偵測系統測試")
    print("=" * 60)
    print("\n測試說明：")
    print("  1. 前 1-2 秒會進行校準，請保持正常睜眼狀態")
    print("  2. 校準完成後，可以測試以下動作：")
    print("     - 閉眼 1-2 秒 → 應觸發 A02（中度疲勞）")
    print("     - 閉眼 3+ 秒  → 應觸發 A01（重度疲勞）")
    print("\n按 'q' 退出測試\n")
    print("=" * 60)
    
    frame_count = 0
    calibration_complete = False
    last_event_type = None
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("⚠️ 警告：無法讀取攝影機畫面")
                break
            
            frame_count += 1
            
            # 執行偵測
            result = detector.detect(frame)
            
            # 處理結果
            if result.get('status') == 'calibrating':
                if frame_count % 30 == 0:
                    progress = result.get('progress', 0)
                    required = result.get('required', 30)
                    print(f"🔧 校準中... {progress}/{required} 樣本")
                
            elif result.get('status') == 'calibrating' and not calibration_complete:
                calibration_complete = True
                print("\n✅ 校準完成！開始偵測...\n")
                
            elif result.get('status') == 'detected':
                metrics = result.get('metrics', {})
                
                # 每 30 幀輸出一次狀態
                if frame_count % 30 == 0:
                    print(f"\r幀 {frame_count}: EAR={metrics.get('ear', 0):.3f} | "
                          f"閉眼幀數={metrics.get('closed_frames', 0)} | "
                          f"眨眼次數={metrics.get('total_blinks', 0)}", end='')
                
                # 偵測到事件
                event_type = result.get('event_type')
                if event_type and event_type != last_event_type:
                    last_event_type = event_type
                    
                    event_map = {
                        'drowsy_severe': 'A01 - 重度疲勞 (閉眼超過3秒)',
                        'drowsy_moderate': 'A02 - 中度疲勞 (閉眼1-3秒)',
                        'drowsy_mild': 'A02 - 中度疲勞 (閉眼1-3秒)'
                    }
                    
                    desc = event_map.get(event_type, event_type)
                    confidence = result.get('confidence', 0)
                    
                    print(f"\n\n{'='*60}")
                    print(f"🚨 偵測到事件: {desc}")
                    print(f"   信心分數: {confidence:.2f}")
                    print(f"   EAR: {metrics.get('ear', 0):.3f}")
                    print(f"   閉眼幀數: {metrics.get('closed_frames', 0)}")
                    print(f"   閉眼時長: {metrics.get('closed_duration', 0):.2f} 秒")
                    print(f"{'='*60}\n")
                
                # 事件結束
                elif not event_type and last_event_type:
                    last_event_type = None
                    
            elif result.get('status') == 'no_face':
                if frame_count % 30 == 0:
                    print(f"\r幀 {frame_count}: ⚠️ 未偵測到臉部", end='')
                    
            elif result.get('status') == 'error':
                print(f"\n❌ 錯誤: {result.get('message')}")
            
            # 顯示畫面（可選）
            cv2.imshow('Drowsiness Detection', frame)
            
            # 按 'q' 退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\n\n測試被中斷")
    except Exception as e:
        print(f"\n❌ 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cap.release()
        cv2.destroyAllWindows()
        
        print("\n" + "=" * 60)
        print("測試結束")
        print(f"總處理幀數: {frame_count}")
        print(f"總眨眼次數: {detector.total_blinks}")
        if detector.baseline_ear:
            print(f"基準 EAR: {detector.baseline_ear:.3f}")
        print("=" * 60)

if __name__ == "__main__":
    main()
