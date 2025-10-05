# services/detection_service.py
"""
偵測服務管理
管理所有行程的 AI 服務實例
"""

from services.ai_service import AIService

class DetectionService:
    """偵測服務管理器（單例）"""
    
    _instance = None
    _services = {}  # {trip_id: AIService}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def start_trip_detection(cls, trip_id):
        """
        啟動行程偵測
        
        Args:
            trip_id: 行程 ID
        
        Returns:
            bool: 是否成功啟動
        """
        if trip_id in cls._services:
            print(f"[DetectionService] Trip {trip_id} 服務已存在")
            return False
        
        service = AIService(trip_id)
        if service.start():
            cls._services[trip_id] = service
            print(f"[DetectionService] Trip {trip_id} 偵測服務已啟動")
            return True
        else:
            return False
    
    @classmethod
    def stop_trip_detection(cls, trip_id):
        """
        停止行程偵測
        
        Args:
            trip_id: 行程 ID
        """
        if trip_id not in cls._services:
            print(f"[DetectionService] Trip {trip_id} 服務不存在")
            return
        
        service = cls._services[trip_id]
        service.stop()
        del cls._services[trip_id]
        print(f"[DetectionService] Trip {trip_id} 偵測服務已停止")
    
    @classmethod
    def get_trip_service(cls, trip_id):
        """取得行程服務實例"""
        return cls._services.get(trip_id)
    
    @classmethod
    def update_trip_gpio(cls, trip_id, left_turn, right_turn, speed):
        """更新行程的 GPIO 狀態"""
        service = cls._services.get(trip_id)
        if service:
            service.update_gpio_status(left_turn, right_turn, speed)
    
    @classmethod
    def get_all_services(cls):
        """取得所有運行中的服務"""
        return list(cls._services.keys())