# api/urls.py

from django.urls import path
from .views import (
    PersonnelListAPIView,
    GroupListAPIView,
    DeviceListAPIView,
    TripListAPIView,
    TripDetailAPIView,
    TripStartAPIView,
    AiVisionLogCreateAPIView,
    VideoRecordCreateAPIView,
    TripEndAPIView,
    UserRegisterAPIView,
    ChatbotAPIView,
    CustomAuthToken,
    UserProfileAPIView,
    health_check,
    system_stats,
)

urlpatterns = [
    # =============================================================================
    # 認證相關 API
    # =============================================================================
    path('auth/login/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('auth/register/', UserRegisterAPIView.as_view(), name='user-register'),
    path('auth/profile/', UserProfileAPIView.as_view(), name='user-profile'),
    
    # =============================================================================
    # 系統狀態 API
    # =============================================================================
    path('health/', health_check, name='health-check'),
    path('system/stats/', system_stats, name='system-stats'),
    
    # =============================================================================
    # 前端資料查詢 API
    # =============================================================================
    path('personnel/', PersonnelListAPIView.as_view(), name='personnel-list'),
    path('groups/', GroupListAPIView.as_view(), name='group-list'),
    path('devices/', DeviceListAPIView.as_view(), name='device-list'),
    path('trips/', TripListAPIView.as_view(), name='trip-list'),
    path('trips/<int:pk>/', TripDetailAPIView.as_view(), name='trip-detail'),
    
    # =============================================================================
    # AI 功能 API
    # =============================================================================
    path('chatbot/', ChatbotAPIView.as_view(), name='chatbot'),
    
    # =============================================================================
    # 樹莓派與設備管理 API
    # =============================================================================
    path('trips/start/', TripStartAPIView.as_view(), name='trip-start'),
    path('trips/<int:pk>/end/', TripEndAPIView.as_view(), name='trip-end'),
    path('events/', AiVisionLogCreateAPIView.as_view(), name='event-create'),
    path('videos/', VideoRecordCreateAPIView.as_view(), name='video-create'),
]