import cloudinary
import cloudinary.uploader
import cloudinary.api
import threading
import time
import json
import os
import logging
import queue
from typing import Dict, List, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class CloudinaryUploader:
    """Cloudinary 雲端上傳服務 - 針對樹莓派優化"""
    
    def __init__(self, config):
        self.config = config
        self.upload_queue = queue.Queue()
        self.upload_thread = None
        self.is_running = False
        
        # 網路優化設定
        self.session = self._create_optimized_session()
        
        # 上傳狀態
        self.upload_stats = {
            'total_uploads': 0,
            'successful_uploads': 0,
            'failed_uploads': 0,
            'total_size_mb': 0
        }
        
        # 初始化 Cloudinary
        self._initialize_cloudinary()
    
    def _create_optimized_session(self):
        """建立優化的HTTP會話"""
        session = requests.Session()
        
        # 重試策略
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 設定超時
        session.timeout = 60
        
        return session
    
    def _initialize_cloudinary(self):
        """初始化 Cloudinary 配置"""
        try:
            if not all([
                self.config.cloudinary_cloud_name,
                self.config.cloudinary_api_key,
                self.config.cloudinary_api_secret
            ]):
                logger.error("Cloudinary 配置不完整")
                return False
            
            cloudinary.config(
                cloud_name=self.config.cloudinary_cloud_name,
                api_key=self.config.cloudinary_api_key,
                api_secret=self.config.cloudinary_api_secret,
                secure=True
            )
            
            # 測試連接
            try:
                cloudinary.api.ping()
                logger.info("Cloudinary 連接成功")
                return True
            except Exception as e:
                logger.error(f"Cloudinary 連接測試失敗: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Cloudinary 初始化失敗: {e}")
            return False
    
    def start(self):
        """啟動上傳服務"""
        if self.is_running:
            logger.warning("上傳服務已在運行")
            return
            
        self.is_running = True
        self.upload_thread = threading.Thread(target=self._upload_loop, daemon=True)
        self.upload_thread.start()
        
        # 載入待上傳隊列
        self._load_upload_queue()
        
        logger.info("雲端上傳服務已啟動")
    
    def stop(self):
        """停止上傳服務"""
        self.is_running = False
        
        if self.upload_thread:
            self.upload_thread.join(timeout=10.0)
        
        logger.info("雲端上傳服務已停止")
    
    def upload_video_segment(self, video_path: str, alerts: List[Dict], 
                           driver_info: Dict = None) -> bool:
        """排隊上傳影片片段"""
        try:
            if not os.path.exists(video_path):
                logger.error(f"影片檔案不存在: {video_path}")
                return False
            
            upload_task = {
                'type': 'video',
                'file_path': video_path,
                'alerts': alerts,
                'driver_info': driver_info or {},
                'timestamp': time.time(),
                'retry_count': 0
            }
            
            self.upload_queue.put(upload_task)
            logger.info(f"影片已加入上傳隊列: {os.path.basename(video_path)}")
            return True
            
        except Exception as e:
            logger.error(f"加入上傳隊列失敗: {e}")
            return False
    
    def _upload_loop(self):
        """上傳主循環"""
        while self.is_running:
            try:
                # 取得上傳任務
                try:
                    task = self.upload_queue.get(timeout=5.0)
                except queue.Empty:
                    continue
                
                # 執行上傳
                success = self._process_upload_task(task)
                
                if not success:
                    # 重試邏輯
                    task['retry_count'] += 1
                    if task['retry_count'] < 3:
                        logger.info(f"重試上傳: {task['file_path']} (第{task['retry_count']}次)")
                        time.sleep(30)  # 等待30秒後重試
                        self.upload_queue.put(task)
                    else:
                        logger.error(f"上傳失敗，已達最大重試次數: {task['file_path']}")
                        self.upload_stats['failed_uploads'] += 1
                
                # 限制上傳頻率以避免過載樹莓派
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"上傳循環錯誤: {e}")
                time.sleep(5)
    
    def _process_upload_task(self, task: Dict) -> bool:
        """處理單一上傳任務"""
        try:
            file_path = task['file_path']
            
            if not os.path.exists(file_path):
                logger.error(f"檔案不存在: {file_path}")
                return False
            
            # 檢查檔案大小
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            
            if file_size_mb > 100:  # Cloudinary 免費版限制
                logger.warning(f"檔案過大，跳過上傳: {file_path} ({file_size_mb:.1f}MB)")
                return False
            
            logger.info(f"開始上傳: {os.path.basename(file_path)} ({file_size_mb:.1f}MB)")
            
            # 準備上傳選項
            upload_options = self._prepare_upload_options(task)
            
            # 執行上傳
            response = cloudinary.uploader.upload_large(
                file_path,
                **upload_options
            )
            
            if response.get('secure_url'):
                logger.info(f"上傳成功: {response['secure_url']}")
                
                # 記錄到資料庫
                self._record_upload(file_path, response, task)
                
                # 刪除本地檔案
                self._cleanup_local_file(file_path)
                
                # 更新統計
                self.upload_stats['successful_uploads'] += 1
                self.upload_stats['total_size_mb'] += file_size_mb
                
                return True
            else:
                logger.error(f"上傳失敗，無回應URL: {file_path}")
                return False
            
        except Exception as e:
            logger.error(f"上傳處理錯誤: {e}")
            return False
    
    def _prepare_upload_options(self, task: Dict) -> Dict:
        """準備上傳選項"""
        filename = os.path.basename(task['file_path'])
        timestamp = time.strftime('%Y%m%d_%H%M%S', time.localtime(task['timestamp']))
        
        # 基本選項
        options = {
            'public_id': f"dashcam/{timestamp}_{filename.split('.')[0]}",
            'folder': "pi_dashcam",
            'resource_type': "video",
            'chunk_size': 6000000,  # 6MB chunks for better stability
            'timeout': 120,
        }
        
        # 添加標籤
        tags = ['dashcam', 'raspberry_pi']
        
        # 根據警報添加標籤
        alerts = task.get('alerts', [])
        if alerts:
            alert_codes = [alert.get('code', '') for alert in alerts]
            tags.extend(alert_codes)
            
            # 高優先級警報
            high_priority_codes = ['A01', 'B03']  # 重度疲勞、闖紅燈
            if any(code in alert_codes for code in high_priority_codes):
                tags.append('high_priority')
        
        options['tags'] = ','.join(tags)
        
        # 添加上下文資訊
        context = {
            'timestamp': str(task['timestamp']),
            'alert_count': str(len(alerts)),
            'driver_id': task.get('driver_info', {}).get('driver_id', 'unknown'),
            'device_id': 'raspberry_pi_001'  # 可以從配置讀取
        }
        
        # 添加警報詳情
        if alerts:
            for i, alert in enumerate(alerts[:5]):  # 最多5個警報
                context[f'alert_{i}_code'] = alert.get('code', '')
                context[f'alert_{i}_score'] = str(alert.get('score', 0))
        
        options['context'] = context
        
        return options
    
    def _record_upload(self, local_path: str, response: Dict, task: Dict):
        """記錄上傳資訊到資料庫"""
        try:
            from database_manager import DatabaseManager
            
            db = DatabaseManager(self.config)
            
            upload_record = {
                'local_path': local_path,
                'cloud_url': response.get('secure_url'),
                'cloud_public_id': response.get('public_id'),
                'file_size': response.get('bytes', 0),
                'upload_timestamp': time.time(),
                'alerts': json.dumps(task.get('alerts', []), ensure_ascii=False),
                'driver_info': json.dumps(task.get('driver_info', {}), ensure_ascii=False)
            }
            
            db.record_upload(upload_record)
            
        except Exception as e:
            logger.error(f"記錄上傳資訊失敗: {e}")
    
    def _cleanup_local_file(self, file_path: str):
        """清理本地檔案"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"已刪除本地檔案: {os.path.basename(file_path)}")
        except Exception as e:
            logger.error(f"刪除本地檔案失敗: {e}")
    
    def _load_upload_queue(self):
        """載入待上傳隊列"""
        try:
            upload_queue_file = os.path.join(self.config.data_dir, 'upload_queue.txt')
            
            if os.path.exists(upload_queue_file):
                with open(upload_queue_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line in lines:
                    try:
                        task = json.loads(line.strip())
                        if os.path.exists(task.get('file_path', '')):
                            self.upload_queue.put(task)
                    except json.JSONDecodeError:
                        continue
                
                # 清空隊列檔案
                open(upload_queue_file, 'w').close()
                
                logger.info(f"載入 {self.upload_queue.qsize()} 個待上傳任務")
                
        except Exception as e:
            logger.error(f"載入上傳隊列失敗: {e}")
    
    def get_upload_stats(self) -> Dict:
        """取得上傳統計"""
        stats = self.upload_stats.copy()
        stats['queue_size'] = self.upload_queue.qsize()
        stats['total_uploads'] = stats['successful_uploads'] + stats['failed_uploads']
        
        if stats['total_uploads'] > 0:
            stats['success_rate'] = stats['successful_uploads'] / stats['total_uploads'] * 100
        else:
            stats['success_rate'] = 0
        
        return stats
    
    def force_upload_all_local_videos(self):
        """強制上傳所有本地影片"""
        try:
            video_files = [f for f in os.listdir(self.config.temp_videos_dir) if f.endswith('.mp4')]
            
            for video_file in video_files:
                video_path = os.path.join(self.config.temp_videos_dir, video_file)
                self.upload_video_segment(video_path, [])
            
            logger.info(f"已將 {len(video_files)} 個影片加入上傳隊列")
            
        except Exception as e:
            logger.error(f"強制上傳失敗: {e}")

# 測試用的獨立執行
if __name__ == "__main__":
    from config import config
    
    uploader = CloudinaryUploader(config)
    uploader.start()
    
    # 測試上傳
    test_video = "test_video.mp4"
    if os.path.exists(test_video):
        uploader.upload_video_segment(test_video, [])
        
    # 等待上傳完成
    time.sleep(10)
    print(uploader.get_upload_stats())
    
    uploader.stop()