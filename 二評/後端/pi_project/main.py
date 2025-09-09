import cv2
import time
import threading
import logging
import signal
import sys
import argparse
import json
from typing import Dict, Optional
from collections import deque

# 導入系統模組
from config import config
from hardware_manager import OptimizedCameraManager, HailoAccelerator
from driver_monitor import EyeSizeAdaptiveMonitor
from adas_analyzer import LightweightAdasAnalyzer
from dashcam_recorder import DashcamRecorder
from cloudinary_uploader import CloudinaryUploader
from database_manager import DatabaseManager
from utils import PerformanceMonitor, get_system_info
from driver_calibration import DriverCalibrationSystem

logger = logging.getLogger(__name__)

class PiDashcamSystem:
    """Pi 車載安全監控系統主類別"""
    
    def __init__(self):
        self.config = config
        self.running = False
        
        # 核心組件
        self.camera_manager = None
        self.driver_monitor = None
        self.adas_analyzer = None
        self.recorder = None
        self.uploader = None
        self.database = None
        self.hailo_accelerator = None
        
        # 效能監控
        self.performance_monitor = PerformanceMonitor()
        
        # 系統狀態
        self.current_driver_id = None
        self.system_stats = {
            'start_time': time.time(),
            'total_alerts': 0,
            'frames_processed': 0,
            'last_activity': time.time()
        }
        
        # 設定信號處理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Pi 車載安全監控系統初始化")
    
    def initialize_system(self) -> bool:
        """初始化系統組件"""
        try:
            logger.info("開始初始化系統組件...")
            
            # 1. 初始化資料庫
            logger.info("初始化資料庫...")
            self.database = DatabaseManager(self.config)
            
            # 2. 初始化硬體加速器
            logger.info("初始化 Hailo 加速器...")
            self.hailo_accelerator = HailoAccelerator(self.config)
            self.hailo_accelerator.initialize()
            
            # 3. 初始化攝影機管理器
            logger.info("初始化攝影機...")
            self.camera_manager = OptimizedCameraManager(self.config)
            if not self.camera_manager.initialize_cameras():
                logger.error("攝影機初始化失敗")
                return False
            
            # 4. 初始化駕駛員監控
            logger.info("初始化駕駛員監控...")
            self.driver_monitor = EyeSizeAdaptiveMonitor(self.config)
            
            # 5. 初始化 ADAS 分析器
            logger.info("初始化 ADAS 分析器...")
            self.adas_analyzer = LightweightAdasAnalyzer(self.config)
            
            # 6. 初始化影片錄製
            logger.info("初始化影片錄製...")
            self.recorder = DashcamRecorder(self.config)
            
            # 7. 初始化雲端上傳
            logger.info("初始化雲端上傳...")
            self.uploader = CloudinaryUploader(self.config)
            self.uploader.start()
            
            logger.info("✅ 系統初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"系統初始化失敗: {e}")
            return False
    
    def load_driver_profile(self, driver_id: str = None) -> bool:
        """載入駕駛員檔案"""
        try:
            if driver_id:
                if self.driver_monitor.load_driver_profile(driver_id):
                    self.current_driver_id = driver_id
                    logger.info(f"已載入駕駛員檔案: {driver_id}")
                    return True
                else:
                    logger.error(f"找不到駕駛員檔案: {driver_id}")
                    return False
            else:
                # 列出可用檔案讓用戶選擇
                profiles = self.driver_monitor.list_driver_profiles()
                
                if not profiles:
                    print("❌ 找不到任何駕駛員檔案")
                    print("請先執行校準: python driver_calibration.py --name 您的姓名")
                    return False
                
                print("\n=== 可用的駕駛員檔案 ===")
                profile_list = list(profiles.items())
                
                for i, (profile_id, profile) in enumerate(profile_list):
                    print(f"{i+1}. {profile.get('driver_name', 'Unknown')} "
                          f"(ID: {profile_id[:12]}...)")
                    print(f"   校準日期: {profile.get('calibration_date', 'Unknown')}")
                    print(f"   眼睛類型: {profile.get('eye_size_category', 'Unknown')}")
                
                try:
                    choice = int(input("\n請選擇駕駛員檔案 (輸入編號): ")) - 1
                    if 0 <= choice < len(profile_list):
                        selected_id = profile_list[choice][0]
                        return self.load_driver_profile(selected_id)
                    else:
                        print("無效的選擇")
                        return False
                except (ValueError, KeyboardInterrupt):
                    print("操作取消")
                    return False
                    
        except Exception as e:
            logger.error(f"載入駕駛員檔案失敗: {e}")
            return False
    
    def start_system(self):
        """啟動系統"""
        try:
            if self.running:
                logger.warning("系統已在運行中")
                return
            
            logger.info("🚗 啟動 Pi 車載安全監控系統")
            
            # 載入駕駛員檔案
            if not self.current_driver_id:
                if not self.load_driver_profile():
                    return
            
            self.running = True
            
            # 啟動攝影機擷取
            self.camera_manager.start_capture()
            
            # 啟動影片錄製
            self.recorder.start_recording()
            
            # 啟動主要處理循環
            self._main_processing_loop()
            
        except Exception as e:
            logger.error(f"系統啟動失敗: {e}")
            self.stop_system()
    
    def _main_processing_loop(self):
        """主要處理循環"""
        logger.info("🔄 主要處理循環開始")
        
        frame_skip_counter = 0
        last_stats_time = time.time()
        
        while self.running:
            try:
                # 更新效能監控
                self.performance_monitor.update()
                
                # 取得影像幀
                internal_frame = self.camera_manager.get_internal_frame()
                external_frame = self.camera_manager.get_external_frame()
                
                # 當前時間戳
                current_time = time.time()
                all_alerts = []
                
                # 處理內鏡頭 (駕駛員監控)
                if internal_frame is not None:
                    driver_result = self.driver_monitor.analyze_frame(internal_frame)
                    
                    if driver_result['alerts']:
                        all_alerts.extend(driver_result['alerts'])
                        self.system_stats['total_alerts'] += len(driver_result['alerts'])
                    
                    # 記錄到資料庫
                    if frame_skip_counter % 5 == 0:  # 每5幀記錄一次
                        self.database.record_driver_monitoring({
                            'timestamp': current_time,
                            'driver_id': self.current_driver_id,
                            'ear_value': driver_result.get('avg_ear', 0),
                            'eye_state': driver_result.get('eye_state', 'unknown'),
                            'head_pose': driver_result.get('head_pose', {}),
                            'alerts': driver_result.get('alerts', [])
                        })
                    
                    # 添加到錄影
                    self.recorder.add_frame(internal_frame, driver_result.get('alerts', []))
                
                # 處理外鏡頭 (ADAS) - 較低頻率
                if external_frame is not None and frame_skip_counter % 3 == 0:
                    # 模擬車輛狀態 (實際使用時應從OBD或其他感測器讀取)
                    speed_kmh = 50  # 假設速度
                    turn_signal_left = False
                    turn_signal_right = False
                    
                    adas_result = self.adas_analyzer.analyze_frame(
                        external_frame, speed_kmh, turn_signal_left, turn_signal_right
                    )
                    
                    if adas_result['alerts']:
                        all_alerts.extend(adas_result['alerts'])
                        self.system_stats['total_alerts'] += len(adas_result['alerts'])
                    
                    # 記錄到資料庫
                    self.database.record_adas_monitoring({
                        'timestamp': current_time,
                        'lane_detected': adas_result.get('lane_detected', False),
                        'vehicles_detected': adas_result.get('vehicles_detected', []),
                        'traffic_lights': adas_result.get('traffic_lights', []),
                        'alerts': adas_result.get('alerts', []),
                        'speed_kmh': speed_kmh
                    })
                
                # 顯示調試資訊
                if self.config.debug_mode and internal_frame is not None:
                    self._display_debug_info(internal_frame, driver_result if 'driver_result' in locals() else {})
                
                # 更新系統統計
                self.system_stats['frames_processed'] += 1
                self.system_stats['last_activity'] = current_time
                
                # 定期記錄系統統計
                if current_time - last_stats_time >= 60:  # 每分鐘記錄一次
                    self._record_system_stats()
                    last_stats_time = current_time
                
                frame_skip_counter += 1
                
                # 控制處理頻率以減少 CPU 負載
                time.sleep(0.05)  # 50ms 延遲
                
            except KeyboardInterrupt:
                logger.info("接收到中斷信號，準備停止系統...")
                break
            except Exception as e:
                logger.error(f"處理循環錯誤: {e}")
                time.sleep(1)  # 錯誤時等待較長時間
        
        logger.info("🛑 主要處理循環結束")
    
    def _record_system_stats(self):
        """記錄系統統計"""
        try:
            system_info = get_system_info()
            performance_stats = self.performance_monitor.get_stats()
            
            stats_data = {
                'timestamp': time.time(),
                'cpu_usage': system_info.get('cpu_percent', 0),
                'memory_usage': system_info.get('memory_percent', 0),
                'temperature': system_info.get('temperature', 0),
                'disk_usage': system_info.get('disk_percent', 0),
                'camera_fps': self.config.internal_camera_fps,
                'processing_fps': performance_stats.get('fps', 0)
            }
            
            self.database.record_system_stats(stats_data)
            
            # 日誌記錄
            if self.config.debug_mode:
                logger.info(f"系統狀態 - CPU: {stats_data['cpu_usage']:.1f}%, "
                           f"記憶體: {stats_data['memory_usage']:.1f}%, "
                           f"溫度: {stats_data['temperature']:.1f}°C, "
                           f"處理FPS: {stats_data['processing_fps']:.1f}")
            
        except Exception as e:
            logger.error(f"記錄系統統計失敗: {e}")
    
    def _display_debug_info(self, frame, driver_result):
        """顯示調試資訊"""
        try:
            debug_frame = frame.copy()
            
            # 添加系統資訊
            info_lines = [
                f"駕駛員: {self.current_driver_id[:12] if self.current_driver_id else 'Unknown'}...",
                f"FPS: {self.performance_monitor.get_fps():.1f}",
                f"EAR: {driver_result.get('avg_ear', 0):.3f}",
                f"狀態: {driver_result.get('eye_state', 'unknown')}",
                f"警報: {len(driver_result.get('alerts', []))}",
                f"運行時間: {int(time.time() - self.system_stats['start_time'])}s"
            ]
            
            for i, line in enumerate(info_lines):
                cv2.putText(debug_frame, line, (10, 30 + i * 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # 顯示警報
            alerts = driver_result.get('alerts', [])
            if alerts:
                y_offset = 200
                for alert in alerts[-3:]:  # 顯示最新3個警報
                    alert_text = f"{alert.get('code', '')}: {alert.get('name', '')}"
                    cv2.putText(debug_frame, alert_text, (10, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                    y_offset += 20
            
            cv2.imshow('Pi Dashcam Debug', debug_frame)
            cv2.waitKey(1)
            
        except Exception as e:
            logger.error(f"顯示調試資訊錯誤: {e}")
    
    def stop_system(self):
        """停止系統"""
        logger.info("🛑 停止 Pi 車載安全監控系統")
        
        self.running = False
        
        try:
            # 停止攝影機
            if self.camera_manager:
                self.camera_manager.stop_capture()
            
            # 停止錄影
            if self.recorder:
                self.recorder.stop_recording()
            
            # 停止上傳服務
            if self.uploader:
                self.uploader.stop()
            
            # 清理資源
            cv2.destroyAllWindows()
            
            # 顯示系統統計
            self._print_system_summary()
            
            logger.info("✅ 系統已安全停止")
            
        except Exception as e:
            logger.error(f"停止系統時發生錯誤: {e}")
    
    def _print_system_summary(self):
        """打印系統摘要"""
        try:
            runtime = time.time() - self.system_stats['start_time']
            
            print("\n" + "="*50)
            print("🏁 系統運行摘要")
            print("="*50)
            print(f"運行時間: {runtime/3600:.1f} 小時")
            print(f"處理幀數: {self.system_stats['frames_processed']}")
            print(f"總警報數: {self.system_stats['total_alerts']}")
            print(f"平均FPS: {self.performance_monitor.get_fps():.1f}")
            
            # 上傳統計
            if self.uploader:
                upload_stats = self.uploader.get_upload_stats()
                print(f"成功上傳: {upload_stats.get('successful_uploads', 0)}")
                print(f"上傳失敗: {upload_stats.get('failed_uploads', 0)}")
                print(f"上傳大小: {upload_stats.get('total_size_mb', 0):.1f} MB")
            
            # 錄影統計
            if self.recorder:
                recording_stats = self.recorder.get_recording_status()
                print(f"暫存檔案: {recording_stats.get('temp_files_count', 0)}")
            
            print("="*50)
            
        except Exception as e:
            logger.error(f"打印系統摘要錯誤: {e}")
    
    def _signal_handler(self, signum, frame):
        """信號處理器"""
        logger.info(f"接收到信號 {signum}，準備關閉系統...")
        self.stop_system()
        sys.exit(0)

def main():
    """主函式"""
    parser = argparse.ArgumentParser(description='Pi 車載安全監控系統')
    parser.add_argument('--driver-id', type=str, help='指定駕駛員ID')
    parser.add_argument('--driver-name', type=str, help='駕駛員姓名 (將自動查找檔案)')
    parser.add_argument('--calibrate', action='store_true', help='進入校準模式')
    parser.add_argument('--test-cameras', action='store_true', help='測試攝影機')
    parser.add_argument('--debug', action='store_true', help='啟用調試模式')
    parser.add_argument('--force-upload', action='store_true', help='強制上傳所有本地影片')
    
    args = parser.parse_args()
    
    # 設定調試模式
    if args.debug:
        config.debug_mode = True
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("""
    ██████╗ ██╗    ██████╗  █████╗ ███████╗██╗  ██╗ ██████╗ █████╗ ███╗   ███╗
    ██╔══██╗██║    ██╔══██╗██╔══██╗██╔════╝██║  ██║██╔════╝██╔══██╗████╗ ████║
    ██████╔╝██║    ██║  ██║███████║███████╗███████║██║     ███████║██╔████╔██║
    ██╔═══╝ ██║    ██║  ██║██╔══██║╚════██║██╔══██║██║     ██╔══██║██║╚██╔╝██║
    ██║     ██║    ██████╔╝██║  ██║███████║██║  ██║╚██████╗██║  ██║██║ ╚═╝ ██║
    ╚═╝     ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝
    
    Pi Project - 車載安全監控系統 v1.0.0
    作者: JoyWuFN | 日期: 2025-09-02
    """)
    
    # 校準模式
    if args.calibrate:
        from driver_calibration import DriverCalibrationSystem
        calibration_system = DriverCalibrationSystem(config)
        
        if args.driver_name:
            calibration_system.start_calibration(args.driver_name)
        else:
            calibration_system.list_existing_profiles()
            driver_name = input("請輸入駕駛員姓名: ").strip()
            if driver_name:
                calibration_system.start_calibration(driver_name)
        return
    
    # 測試攝影機模式
    if args.test_cameras:
        from scripts.test_cameras import test_cameras
        test_cameras()
        return
    
    # 建立系統實例
    system = PiDashcamSystem()
    
    # 初始化系統
    if not system.initialize_system():
        print("❌ 系統初始化失敗")
        return
    
    # 強制上傳模式
    if args.force_upload:
        system.uploader.force_upload_all_local_videos()
        print("✅ 所有本地影片已加入上傳隊列")
        return
    
    # 設定駕駛員
    if args.driver_id:
        system.current_driver_id = args.driver_id
    elif args.driver_name:
        # 根據姓名查找駕駛員ID
        profiles = system.driver_monitor.list_driver_profiles()
        for profile_id, profile in profiles.items():
            if profile.get('driver_name') == args.driver_name:
                system.current_driver_id = profile_id
                break
        
        if not system.current_driver_id:
            print(f"❌ 找不到駕駛員: {args.driver_name}")
            return
    
    try:
        # 啟動系統
        system.start_system()
    except KeyboardInterrupt:
        print("\n用戶中斷系統")
    except Exception as e:
        logger.error(f"系統運行錯誤: {e}")
        print(f"❌ 系統錯誤: {e}")
    finally:
        system.stop_system()

if __name__ == "__main__":
    main()