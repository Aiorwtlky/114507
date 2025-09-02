import cv2
import time
import json
import os
import logging
import numpy as np
from typing import Dict, Optional
from adaptive_driver_monitor import EyeSizeAdaptiveMonitor

logger = logging.getLogger(__name__)

class DriverCalibrationSystem:
    """駕駛員校準系統"""
    
    def __init__(self, config):
        self.config = config
        self.monitor = EyeSizeAdaptiveMonitor(config)
        self.camera = None
        
        # 校準階段
        self.calibration_phases = [
            {
                'name': 'normal_state',
                'display_name': '正常駕駛狀態校準',
                'instruction': '請保持正常駕駛姿勢，眼睛自然張開，直視前方',
                'duration': 30,
                'min_frames': 100
            },
            {
                'name': 'blink_pattern',
                'display_name': '眨眼模式校準',
                'instruction': '請進行正常眨眼，每次眨眼後稍作停頓',
                'duration': 20,
                'min_frames': 50
            },
            {
                'name': 'head_movement',
                'display_name': '頭部姿態校準',
                'instruction': '請保持正常駕駛姿勢，可輕微轉動頭部',
                'duration': 15,
                'min_frames': 40
            }
        ]
        
    def initialize_camera(self) -> bool:
        """初始化攝影機"""
        try:
            self.camera = cv2.VideoCapture(self.config.internal_camera_index)
            if not self.camera.isOpened():
                logger.error("無法開啟攝影機")
                return False
                
            # 設定攝影機參數
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.internal_camera_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.internal_camera_height)
            self.camera.set(cv2.CAP_PROP_FPS, self.config.internal_camera_fps)
            
            logger.info("攝影機初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"攝影機初始化失敗: {e}")
            return False
    
    def start_calibration(self, driver_name: str) -> bool:
        """開始完整校準流程"""
        try:
            print(f"\n=== 駕駛員校準系統 ===")
            print(f"駕駛員: {driver_name}")
            print(f"日期: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*50)
            
            if not self.initialize_camera():
                return False
            
            print("\n校準說明:")
            print("1. 請確保光線充足")
            print("2. 坐在正常駕駛位置")
            print("3. 攝影機應對準您的臉部")
            print("4. 按照指示完成各階段校準")
            print("\n按 Enter 開始校準...")
            input()
            
            # 開始校準
            self.monitor.start_calibration(driver_name)
            
            # 執行各階段校準
            for phase in self.calibration_phases:
                if not self._run_calibration_phase(phase):
                    print("校準失敗！")
                    return False
            
            # 完成校準
            success = self.monitor.finish_calibration()
            
            if success:
                print("\n🎉 校準完成！")
                print("個人化設定已儲存，系統將根據您的眼型特徵進行精確檢測。")
                
                # 顯示校準結果
                self._display_calibration_results()
                
            else:
                print("\n❌ 校準失敗！請重新校準。")
            
            return success
            
        except Exception as e:
            logger.error(f"校準過程錯誤: {e}")
            print(f"校準錯誤: {e}")
            return False
        finally:
            if self.camera:
                self.camera.release()
            cv2.destroyAllWindows()
    
    def _run_calibration_phase(self, phase: Dict) -> bool:
        """執行單一校準階段"""
        try:
            print(f"\n--- {phase['display_name']} ---")
            print(f"指示: {phase['instruction']}")
            print(f"持續時間: {phase['duration']} 秒")
            print("\n準備就緒後按 Enter 開始...")
            input()
            
            start_time = time.time()
            frame_count = 0
            valid_frames = 0
            
            print("校準進行中...")
            print("進度: ", end="", flush=True)
            
            while time.time() - start_time < phase['duration']:
                ret, frame = self.camera.read()
                if not ret:
                    continue
                
                frame_count += 1
                
                # 分析幀
                result = self.monitor.analyze_frame(frame)
                
                if result['face_detected']:
                    # 添加校準幀
                    self.monitor.add_calibration_frame(frame, phase['name'])
                    valid_frames += 1
                    
                    # 顯示即時結果
                    display_frame = self._draw_calibration_overlay(frame, result, phase)
                    cv2.imshow('Driver Calibration', display_frame)
                
                # 更新進度
                progress = int((time.time() - start_time) / phase['duration'] * 20)
                print(f"\r進度: {'█' * progress}{'░' * (20 - progress)} {progress * 5}%", end="", flush=True)
                
                # 檢查退出
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\n用戶取消校準")
                    return False
            
            print(f"\n✓ 階段完成！有效幀數: {valid_frames}/{frame_count}")
            
            # 檢查最小幀數要求
            if valid_frames < phase['min_frames']:
                print(f"❌ 有效幀數不足！需要至少 {phase['min_frames']} 幀，實際 {valid_frames} 幀")
                print("請重新校準此階段...")
                return self._run_calibration_phase(phase)  # 重試
            
            time.sleep(1)  # 短暫休息
            return True
            
        except Exception as e:
            logger.error(f"校準階段錯誤: {e}")
            return False
    
    def _draw_calibration_overlay(self, frame, result, phase) -> np.ndarray:
        """繪製校準覆蓋層"""
        overlay_frame = frame.copy()
        
        try:
            # 繪製臉部檢測狀態
            if result['face_detected']:
                # 綠色邊框表示檢測到臉部
                h, w = frame.shape[:2]
                cv2.rectangle(overlay_frame, (10, 10), (w-10, h-10), (0, 255, 0), 3)
                
                # 顯示EAR值
                ear_text = f"EAR: {result['avg_ear']:.3f}"
                cv2.putText(overlay_frame, ear_text, (20, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # 顯示眼睛狀態
                eye_state = result['eye_state']
                state_color = (0, 255, 0) if eye_state == 'open' else (0, 255, 255)
                cv2.putText(overlay_frame, f"狀態: {eye_state}", (20, 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, state_color, 2)
                
            else:
                # 紅色邊框表示未檢測到臉部
                h, w = frame.shape[:2]
                cv2.rectangle(overlay_frame, (10, 10), (w-10, h-10), (0, 0, 255), 3)
                cv2.putText(overlay_frame, "未檢測到臉部", (20, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # 顯示當前階段資訊
            cv2.putText(overlay_frame, phase['display_name'], (20, overlay_frame.shape[0] - 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # 顯示指示
            instruction_lines = self._wrap_text(phase['instruction'], 50)
            for i, line in enumerate(instruction_lines):
                cv2.putText(overlay_frame, line, (20, overlay_frame.shape[0] - 30 + i * 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
        except Exception as e:
            logger.error(f"繪製覆蓋層錯誤: {e}")
        
        return overlay_frame
    
    def _wrap_text(self, text: str, width: int) -> list:
        """文字換行"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + word) <= width:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines
    
    def _display_calibration_results(self):
        """顯示校準結果"""
        try:
            if self.monitor.driver_profile:
                profile = self.monitor.driver_profile
                
                print("\n--- 校準結果 ---")
                print(f"駕駛員: {profile.get('driver_name', 'Unknown')}")
                print(f"眼睛類型: {profile.get('eye_size_category', 'Unknown')}")
                print(f"正常EAR值: {profile.get('normal_ear_mean', 0):.3f}")
                print(f"閉眼閾值: {profile.get('closed_threshold', 0):.3f}")
                print(f"疲勞閾值: {profile.get('drowsy_threshold', 0):.3f}")
                print(f"校準品質: {profile.get('calibration_quality', 0):.2f}")
                print(f"校準幀數: {profile.get('calibration_frames', 0)}")
                
                # 評估校準品質
                quality = profile.get('calibration_quality', 0)
                if quality >= 0.8:
                    print("🌟 校準品質: 優秀")
                elif quality >= 0.6:
                    print("👍 校準品質: 良好")
                elif quality >= 0.4:
                    print("⚠️  校準品質: 一般，建議重新校準")
                else:
                    print("❌ 校準品質: 不佳，請重新校準")
                
                print("="*30)
                
        except Exception as e:
            logger.error(f"顯示校準結果錯誤: {e}")
    
    def list_existing_profiles(self):
        """列出現有的駕駛員檔案"""
        try:
            profiles = self.monitor.list_driver_profiles()
            
            if not profiles:
                print("目前沒有駕駛員檔案")
                return
            
            print("\n=== 現有駕駛員檔案 ===")
            for driver_id, profile in profiles.items():
                print(f"\nID: {driver_id}")
                print(f"姓名: {profile.get('driver_name', 'Unknown')}")
                print(f"校準日期: {profile.get('calibration_date', 'Unknown')}")
                print(f"眼睛類型: {profile.get('eye_size_category', 'Unknown')}")
                print(f"校準品質: {profile.get('calibration_quality', 0):.2f}")
            
            print("="*30)
            
        except Exception as e:
            logger.error(f"列出檔案錯誤: {e}")

def main():
    """主函式"""
    import argparse
    from config import config
    
    parser = argparse.ArgumentParser(description='駕駛員校準系統')
    parser.add_argument('--name', type=str, help='駕駛員姓名')
    parser.add_argument('--list', action='store_true', help='列出現有檔案')
    
    args = parser.parse_args()
    
    calibration_system = DriverCalibrationSystem(config)
    
    if args.list:
        calibration_system.list_existing_profiles()
        return
    
    if args.name:
        driver_name = args.name
    else:
        print("=== 駕駛員校準系統 ===")
        calibration_system.list_existing_profiles()
        driver_name = input("\n請輸入駕駛員姓名: ").strip()
        
        if not driver_name:
            print("請提供有效的駕駛員姓名")
            return
    
    # 開始校準
    success = calibration_system.start_calibration(driver_name)
    
    if success:
        print("\n校準完成！您現在可以啟動主系統了。")
    else:
        print("\n校準失敗，請重試。")

if __name__ == "__main__":
    main()