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
    UserRegisterAPIView
)

urlpatterns = [
    # --- GET (Read) APIs for Frontend ---
    path('personnel/', PersonnelListAPIView.as_view(), name='personnel-list'),
    path('groups/', GroupListAPIView.as_view(), name='group-list'),
    path('devices/', DeviceListAPIView.as_view(), name='device-list'),
    path('trips/', TripListAPIView.as_view(), name='trip-list'),
    path('trips/<int:pk>/', TripDetailAPIView.as_view(), name='trip-detail'),

    # --- POST/PUT (Write) APIs for Raspberry Pi ---
    path('trips/start/', TripStartAPIView.as_view(), name='trip-start'),
    path('events/', AiVisionLogCreateAPIView.as_view(), name='event-create'),
    path('videos/', VideoRecordCreateAPIView.as_view(), name='video-create'),
    path('trips/<int:pk>/end/', TripEndAPIView.as_view(), name='trip-end'),
    path('register/', UserRegisterAPIView.as_view(), name='user-register'), 
]