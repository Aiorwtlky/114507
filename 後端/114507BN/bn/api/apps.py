# api/apps.py

from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    
    def ready(self):
        # 匯入我們剛剛建立的 signals.py 檔案，這樣裡面的接收器就會被註冊
        import api.signals