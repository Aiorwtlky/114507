import os
import time
import threading
import queue
from typing import Dict, Any, Optional, List
from datetime import datetime
import cloudinary
import cloudinary.uploader
from utils import (
    setup_logging,
    get_performance_monitor,
    cleanup_old_files,
    format_file_size,
    save_json_file,
    load_json_file
)
from config import config

class CloudinaryUploader:
    """Cloudinary 雲端上傳服務"""
    
    def __init__(self, config_obj=None):
        self.config = config_obj or config
        self.logger = setup_logging()
        self.performance_monitor = get_performance_monitor('cloudinary_uploader')
        
        # 配置 Cloudinary
        cloudinary.config(
            cloud_name=self.config.cloudinary.cloud_name,
            api_key=self.config.cloudinary.api_key,
            api_secret=self.config.cloudinary.api_secret
        )
        
        # 上傳佇列
        self.upload_queue = queue.Queue()
        self.upload_results_queue = queue.Queue()
        
        # 執行緒控制
        self.upload_thread = None
        self.is_running = False
        self.upload_stats = {
            'total_uploads': 0,
            'successful_uploads': 0,
            'failed_uploads': 0,
            'total_size_uploaded': 0,
            'start_time': time.time()
        }
        
        # 離線模式和重試機制
        self.offline_mode = False
        self.retry_attempts = {}
        self.pending_uploads_file = os.path.join(self.config.data_dir, 'pending_uploads.json')
        
        # 執行緒安全
        self._lock = threading.Lock()
        
        # 載入待上傳檔案
        self._load_pending_uploads()
        
        self.logger.info("Cloudinary 上傳服務已初始化")
    
    def start(self):
        """啟動上傳服務"""
        try:
            if self.is_running:
                self.logger.warning("上傳服務已在運行中")
                return
            
            self.is_running = True
            self.upload_thread = threading.Thread(target=self._upload_worker, daemon=True)
            self.upload_thread.start()
            
            self.logger.info("雲端上傳服務已啟動")
            
        except Exception as e:
            self.logger.error(f"啟動上傳服務失敗: {e}")
            self.is_running = False
    
    def stop(self):
        """停止上傳服務"""
        try:
            self.is_running = False
            
            if self.upload_thread and self.upload_thread.is_alive():
                self.upload_thread.join(timeout=5.0)
            
            # 儲存待上傳檔案
            self._save_pending_uploads()
            
            self.logger.info("雲端上傳服務已停止")
            
        except Exception as e:
            self.logger.error(f"停止上傳服務時發生錯誤: {e}")
    
    def upload_file(self, file_path: str, metadata: Optional[Dict[str, Any]] = None, 
                   priority: int = 0, delete_after_upload: bool = True) -> bool:
        """
        添加檔案到上傳佇列
        
        Args:
            file_path: 檔案路徑
            metadata: 檔案元資料
            priority: 優先級 (數字越大優先級越高)
            delete_after_upload: 上傳後是否刪除本地檔案
            
        Returns:
            bool: 是否成功添加到佇列
        """
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"檔案不存在: {file_path}")
                return False
            
            file_size = os.path.getsize(file_path)
            upload_task = {
                'file_path': file_path,
                'metadata': metadata or {},
                'priority': priority,
                'delete_after_upload': delete_after_upload,
                'file_size': file_size,
                'added_time': time.time(),
                'retry_count': 0
            }
            
            # 根據優先級插入佇列
            self.upload_queue.put((priority, upload_task))
            
            self.logger.info(f"檔案已添加到上傳佇列: {os.path.basename(file_path)} ({format_file_size(file_size)})")
            return True
            
        except Exception as e:
            self.logger.error(f"添加上傳任務失敗: {e}")
            return False
    
    def upload_video_segment(self, video_path: str, alerts: List[Dict[str, Any]] = None) -> bool:
        """
        上傳影片片段（行車記錄器專用）
        
        Args:
            video_path: 影片檔案路徑
            alerts: 相關警報資料
            
        Returns:
            bool: 是否成功添加到佇列
        """
        try:
            # 準備元資料
            metadata = {
                'type': 'dashcam_video',
                'recorded_time': datetime.now().isoformat(),
                'driver_id': getattr(self, 'current_driver_id', 'unknown'),
                'file_type': 'video'
            }
            
            # 添加警報資訊
            if alerts:
                metadata['alerts'] = alerts
                metadata['alert_count'] = len(alerts)
                metadata['has_alerts'] = True
                
                # 計算總分數
                total_score = sum(alert.get('score', 0) for alert in alerts)
                metadata['total_alert_score'] = total_score
                
                # 設定優先級（有警報的影片優先上傳）
                priority = min(10, total_score // 5)  # 分數越高優先級越高
            else:
                metadata['has_alerts'] = False
                metadata['alert_count'] = 0
                priority = 0
            
            return self.upload_file(video_path, metadata, priority, delete_after_upload=True)
            
        except Exception as e:
            self.logger.error(f"上傳影片片段失敗: {e}")
            return False
    
    def _upload_worker(self):
        """上傳工作執行緒"""
        self.logger.info("上傳工作執行緒已啟動")
        
        while self.is_running:
            try:
                # 從佇列取得任務 (按優先級排序)
                try:
                    priority, task = self.upload_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # 執行上傳
                success = self._perform_upload(task)
                
                # 記錄結果
                self.upload_results_queue.put({
                    'task': task,
                    'success': success,
                    'timestamp': time.time()
                })
                
                # 更新統計
                with self._lock:
                    self.upload_stats['total_uploads'] += 1
                    if success:
                        self.upload_stats['successful_uploads'] += 1
                        self.upload_stats['total_size_uploaded'] += task['file_size']
                    else:
                        self.upload_stats['failed_uploads'] += 1
                
                self.upload_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"上傳工作執行緒錯誤: {e}")
                time.sleep(1.0)
        
        self.logger.info("上傳工作執行緒已結束")
    
    def _perform_upload(self, task: Dict[str, Any]) -> bool:
        """執行單個檔案上傳"""
        file_path = task['file_path']
        metadata = task['metadata']
        delete_after = task['delete_after_upload']
        
        try:
            self.performance_monitor.start_frame()
            
            # 檢查檔案是否仍存在
            if not os.path.exists(file_path):
                self.logger.warning(f"上傳時檔案不存在: {file_path}")
                return False
            
            # 準備上傳參數
            filename = os.path.basename(file_path)
            public_id = self._generate_public_id(filename, metadata)
            
            upload_params = {
                'public_id': public_id,
                'folder': self.config.cloudinary.folder_prefix,
                'resource_type': 'video' if filename.lower().endswith(('.mp4', '.avi', '.mov')) else 'image',
                'context': self._prepare_context(metadata),
                'tags': self._generate_tags(metadata)
            }
            
            # 執行上傳
            self.logger.info(f"開始上傳: {filename}")
            start_time = time.time()
            
            result = cloudinary.uploader.upload(
                file_path,
                **upload_params,
                timeout=self.config.cloudinary.upload_timeout
            )
            
            upload_time = time.time() - start_time
            
            # 上傳成功
            if result.get('public_id'):
                self.logger.info(f"上傳成功: {filename} -> {result['public_id']} ({upload_time:.1f}s)")
                
                # 記錄上傳資訊
                self._record_upload_success(file_path, result, metadata)
                
                # 刪除本地檔案
                if delete_after:
                    try:
                        os.remove(file_path)
                        self.logger.debug(f"本地檔案已刪除: {filename}")
                    except Exception as e:
                        self.logger.warning(f"刪除本地檔案失敗: {e}")
                
                self.performance_monitor.end_frame()
                return True
            
            else:
                self.logger.error(f"上傳失敗，無有效結果: {filename}")
                self.performance_monitor.end_frame()
                return False
        
        except Exception as e:
            self.logger.error(f"上傳檔案時發生錯誤 {file_path}: {e}")
            
            # 重試機制
            task['retry_count'] += 1
            if task['retry_count'] < self.config.cloudinary.max_retries:
                self.logger.info(f"將重試上傳: {filename} (第 {task['retry_count']} 次)")
                # 重新添加到佇列，降低優先級
                self.upload_queue.put((task.get('priority', 0) - 1, task))
            else:
                self.logger.error(f"上傳失敗，已達最大重試次數: {filename}")
                # 保存到待上傳清單
                self._save_failed_upload(task)
            
            self.performance_monitor.end_frame()
            return False
    
    def _generate_public_id(self, filename: str, metadata: Dict[str, Any]) -> str:
        """生成 Cloudinary public_id"""
        try:
            # 移除副檔名
            name_without_ext = os.path.splitext(filename)[0]
            
            # 添加時間戳記和類型資訊
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_type = metadata.get('type', 'unknown')
            
            # 如果有駕駛員 ID，加入其中
            driver_id = metadata.get('driver_id', '')
            if driver_id:
                public_id = f"{file_type}/{driver_id}/{timestamp}_{name_without_ext}"
            else:
                public_id = f"{file_type}/{timestamp}_{name_without_ext}"
            
            return public_id
            
        except Exception:
            # 回退到簡單的命名
            return f"upload_{int(time.time())}_{filename}"
    
    def _prepare_context(self, metadata: Dict[str, Any]) -> Dict[str, str]:
        """準備 Cloudinary context 資料"""
        context = {}
        
        try:
            # 將元資料轉換為字串格式
            for key, value in metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    context[key] = str(value)
                elif isinstance(value, (list, dict)):
                    # 複雜資料類型轉為 JSON 字串
                    import json
                    context[key] = json.dumps(value, ensure_ascii=False)
            
            # 添加上傳時間
            context['upload_time'] = datetime.now().isoformat()
            context['uploader'] = 'pi_project_v1.0'
            
        except Exception as e:
            self.logger.warning(f"準備 context 資料時發生錯誤: {e}")
        
        return context
    
    def _generate_tags(self, metadata: Dict[str, Any]) -> List[str]:
        """生成標籤"""
        tags = ['pi_project', 'dashcam']
        
        try:
            # 根據元資料添加標籤
            if metadata.get('has_alerts'):
                tags.append('has_alerts')
                
                # 添加具體警報類型標籤
                alerts = metadata.get('alerts', [])
                alert_codes = set()
                for alert in alerts:
                    alert_code = alert.get('code', '')
                    if alert_code:
                        alert_codes.add(alert_code)
                
                tags.extend(list(alert_codes))
            
            # 添加檔案類型標籤
            file_type = metadata.get('type', '')
            if file_type:
                tags.append(file_type)
            
            # 添加駕駛員標籤
            driver_id = metadata.get('driver_id', '')
            if driver_id and driver_id != 'unknown':
                tags.append(f"driver_{driver_id}")
            
            # 添加日期標籤
            today = datetime.now().strftime('%Y-%m-%d')
            tags.append(f"date_{today}")
            
        except Exception as e:
            self.logger.warning(f"生成標籤時發生錯誤: {e}")
        
        return tags
    
    def _record_upload_success(self, file_path: str, upload_result: Dict[str, Any], metadata: Dict[str, Any]):
        """記錄上傳成功的資訊"""
        try:
            record = {
                'local_path': file_path,
                'cloudinary_url': upload_result.get('url', ''),
                'public_id': upload_result.get('public_id', ''),
                'upload_time': datetime.now().isoformat(),
                'file_size': upload_result.get('bytes', 0),
                'metadata': metadata
            }
            
            # 保存到上傳記錄檔案
            upload_log_file = os.path.join(self.config.data_dir, 'upload_log.json')
            upload_log = load_json_file(upload_log_file, [])
            upload_log.append(record)
            
            # 只保留最近 1000 筆記錄
            if len(upload_log) > 1000:
                upload_log = upload_log[-1000:]
            
            save_json_file(upload_log, upload_log_file)
            
        except Exception as e:
            self.logger.warning(f"記錄上傳成功資訊時發生錯誤: {e}")
    
    def _save_failed_upload(self, task: Dict[str, Any]):
        """保存上傳失敗的任務"""
        try:
            failed_uploads = load_json_file(self.pending_uploads_file, [])
            
            failed_task = {
                'file_path': task['file_path'],
                'metadata': task['metadata'],
                'retry_count': task['retry_count'],
                'failed_time': datetime.now().isoformat(),
                'file_size': task['file_size']
            }
            
            failed_uploads.append(failed_task)
            save_json_file(failed_uploads, self.pending_uploads_file)
            
        except Exception as e:
            self.logger.error(f"保存失敗上傳任務時發生錯誤: {e}")
    
    def _load_pending_uploads(self):
        """載入待上傳檔案"""
        try:
            pending_uploads = load_json_file(self.pending_uploads_file, [])
            
            loaded_count = 0
            for task_data in pending_uploads:
                file_path = task_data['file_path']
                
                # 檢查檔案是否仍存在
                if os.path.exists(file_path):
                    task = {
                        'file_path': file_path,
                        'metadata': task_data['metadata'],
                        'priority': 0,  # 低優先級
                        'delete_after_upload': True,
                        'file_size': task_data.get('file_size', 0),
                        'added_time': time.time(),
                        'retry_count': task_data.get('retry_count', 0)
                    }
                    
                    self.upload_queue.put((0, task))
                    loaded_count += 1
            
            if loaded_count > 0:
                self.logger.info(f"已載入 {loaded_count} 個待上傳檔案")
                
                # 清空待上傳清單
                save_json_file([], self.pending_uploads_file)
            
        except Exception as e:
            self.logger.error(f"載入待上傳檔案時發生錯誤: {e}")
    
    def _save_pending_uploads(self):
        """保存當前佇列中的待上傳檔案"""
        try:
            pending_tasks = []
            
            # 從佇列中取出所有任務
            while not self.upload_queue.empty():
                try:
                    priority, task = self.upload_queue.get_nowait()
                    pending_tasks.append(task)
                except queue.Empty:
                    break
            
            if pending_tasks:
                existing_pending = load_json_file(self.pending_uploads_file, [])
                
                for task in pending_tasks:
                    pending_data = {
                        'file_path': task['file_path'],
                        'metadata': task['metadata'],
                        'retry_count': task['retry_count'],
                        'saved_time': datetime.now().isoformat(),
                        'file_size': task['file_size']
                    }
                    existing_pending.append(pending_data)
                
                save_json_file(existing_pending, self.pending_uploads_file)
                self.logger.info(f"已保存 {len(pending_tasks)} 個待上傳檔案")
        
        except Exception as e:
            self.logger.error(f"保存待上傳檔案時發生錯誤: {e}")
    
    def get_upload_stats(self) -> Dict[str, Any]:
        """獲取上傳統計資料"""
        try:
            with self._lock:
                stats = self.upload_stats.copy()
            
            # 計算運行時間
            uptime = time.time() - stats['start_time']
            stats['uptime_seconds'] = uptime
            stats['uptime_formatted'] = f"{uptime / 3600:.1f} 小時"
            
            # 計算成功率
            if stats['total_uploads'] > 0:
                stats['success_rate'] = stats['successful_uploads'] / stats['total_uploads']
            else:
                stats['success_rate'] = 0.0
            
            # 佇列狀態
            stats['queue_size'] = self.upload_queue.qsize()
            stats['is_running'] = self.is_running
            
            # 格式化上傳大小
            stats['total_size_formatted'] = format_file_size(stats['total_size_uploaded'])
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_recent_uploads(self, limit: int = 10) -> List[Dict[str, Any]]:
        """獲取最近的上傳記錄"""
        try:
            upload_log_file = os.path.join(self.config.data_dir, 'upload_log.json')
            upload_log = load_json_file(upload_log_file, [])
            
            # 返回最近的記錄
            return upload_log[-limit:]
            
        except Exception as e:
            self.logger.error(f"獲取上傳記錄時發生錯誤: {e}")
            return []
    
    def cleanup_local_files(self):
        """清理本地檔案"""
        try:
            # 清理暫存影片目錄
            deleted_count = cleanup_old_files(
                self.config.temp_videos_dir, 
                self.config.recording.max_local_files,
                "*.mp4"
            )
            
            if deleted_count > 0:
                self.logger.info(f"已清理 {deleted_count} 個舊影片檔案")
            
        except Exception as e:
            self.logger.error(f"清理本地檔案時發生錯誤: {e}")
    
    def set_current_driver(self, driver_id: str):
        """設定當前駕駛員 ID"""
        self.current_driver_id = driver_id
        self.logger.info(f"已設定當前駕駛員: {driver_id}")
    
    def test_connection(self) -> bool:
        """測試 Cloudinary 連接"""
        try:
            # 嘗試獲取帳戶資訊
            result = cloudinary.api.ping()
            
            if result.get('status') == 'ok':
                self.logger.info("Cloudinary 連接測試成功")
                return True
            else:
                self.logger.error("Cloudinary 連接測試失敗")
                return False
                
        except Exception as e:
            self.logger.error(f"Cloudinary 連接測試錯誤: {e}")
            return False

# 如果直接執行此檔案，則進入測試模式
if __name__ == "__main__":
    import sys
    import tempfile
    
    print("Cloudinary 上傳服務測試模式")
    
    # 檢查配置
    if not all([config.cloudinary.cloud_name, config.cloudinary.api_key, config.cloudinary.api_secret]):
        print("錯誤: Cloudinary 配置不完整，請檢查 .env 檔案")
        sys.exit(1)
    
    uploader = CloudinaryUploader()
    
    # 測試連接
    print("測試 Cloudinary 連接...")
    if not uploader.test_connection():
        print("連接失敗，請檢查配置")
        sys.exit(1)
    
    print("連接成功！")
    
    # 啟動上傳服務
    uploader.start()
    
    try:
        # 建立測試檔案
        test_content = f"Pi Project 測試檔案\n時間: {datetime.now()}\n作者: {config.author}"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            test_file = f.name
        
        print(f"建立測試檔案: {test_file}")
        
        # 上傳測試檔案
        metadata = {
            'type': 'test_file',
            'description': 'Pi Project 上傳服務測試',
            'test_mode': True
        }
        
        print("開始上傳測試...")
        success = uploader.upload_file(test_file, metadata, priority=5, delete_after_upload=True)
        
        if success:
            print("測試檔案已添加到上傳佇列")
            
            # 等待上傳完成
            print("等待上傳完成...")
            time.sleep(5)
            
            # 顯示統計資料
            stats = uploader.get_upload_stats()
            print(f"上傳統計: {stats}")
            
            # 顯示最近上傳
            recent = uploader.get_recent_uploads(5)
            print(f"最近上傳: {recent}")
        
        else:
            print("添加測試檔案到佇列失敗")
    
    except KeyboardInterrupt:
        print("用戶中斷測試")
    
    except Exception as e:
        print(f"測試過程發生錯誤: {e}")
    
    finally:
        # 清理測試檔案
        try:
            if os.path.exists(test_file):
                os.remove(test_file)
        except:
            pass
        
        # 停止服務
        uploader.stop()
        print("測試結束")