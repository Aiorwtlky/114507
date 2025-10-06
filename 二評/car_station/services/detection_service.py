# services/detection_service.py（完整修正版）
"""
偵測服務管理器
管理所有行程的 AI 偵測服務
"""

from services.ai_service import AIService

class DetectionService:
    """偵測服務管理器"""
    
    # 類別變數：儲存所有執行中的服務
    active_services = {}
    
    @classmethod
    def start_trip_detection(cls, trip_id):
        """啟動行程偵測"""
        if trip_id in cls.active_services:
            print(f"[DetectionService] Trip {trip_id} 已有執行中的服務")
            return False
        
        try:
            from flask import current_app
            ai_service = AIService(trip_id, current_app._get_current_object())
            success = ai_service.start()
            
            if success:
                cls.active_services[trip_id] = ai_service
                print(f"[DetectionService] Trip {trip_id} 偵測服務已啟動")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"[DetectionService] 啟動失敗: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @classmethod
    def stop_trip_detection(cls, trip_id):
        """停止行程偵測"""
        if trip_id not in cls.active_services:
            print(f"[DetectionService] Trip {trip_id} 沒有執行中的服務")
            return False
        
        try:
            ai_service = cls.active_services[trip_id]
            ai_service.stop()
            del cls.active_services[trip_id]
            print(f"[DetectionService] Trip {trip_id} 偵測服務已停止")
            return True
        except Exception as e:
            print(f"[DetectionService] 停止失敗: {e}")
            return False
    
    @classmethod
    def get_trip_service(cls, trip_id):
        """取得行程的 AI 服務"""
        return cls.active_services.get(trip_id)
    
    @classmethod
    def get_all_active_trips(cls):
        """取得所有執行中的行程 ID"""
        return list(cls.active_services.keys())