# api/urls.py

from django.urls import path
from .views import (
    PersonnelListAPIView,
    GroupListAPIView,
    DeviceListAPIView,
    TripListAPIView,
    TripDetailAPIView,
)

urlpatterns = [
    # GET /api/personnel/
    path('personnel/', PersonnelListAPIView.as_view(), name='personnel-list'),
    
    # GET /api/groups/
    path('groups/', GroupListAPIView.as_view(), name='group-list'),
    
    # GET /api/devices/
    path('devices/', DeviceListAPIView.as_view(), name='device-list'),

    # GET /api/trips/
    path('trips/', TripListAPIView.as_view(), name='trip-list'),
    
    # GET /api/trips/<int:pk>/
    # <int:pk> 是一個路徑轉換器，它會捕獲 URL 中的整數，並將其作為主鍵 (pk) 傳遞給視圖
    path('trips/<int:pk>/', TripDetailAPIView.as_view(), name='trip-detail'),
]