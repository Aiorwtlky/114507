# api/urls.py

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    # User
    UserRegisterAPIView,
    UserProfileAPIView,
    PersonnelListAPIView,
    # Group
    MyGroupsListAPIView,
    GroupCreateAPIView,
    GroupDetailAPIView,
    GroupMembersListAPIView,
    GroupListAPIView,
    # Announcement
    GroupAnnouncementListCreateAPIView,
    GroupAnnouncementDetailAPIView,
    # Device
    DeviceListAPIView,
    # Trip, Video & Report
    TripListAPIView,
    TripDetailAPIView,
    VideoListAPIView,
    generate_trip_report_pdf,
    # Data Upload
    TripStartAPIView,
    TripEndAPIView,
    AiVisionLogCreateAPIView,
    VideoRecordCreateAPIView,
    # AI, System & Stats
    ChatbotAPIView,
    health_check,
    system_stats,
    UserTrendsAPIView,
    InvitationCodeCreateAPIView, 
    GroupMemberRoleAPIView,
    GroupMemberDeleteAPIView,
    ChatbotFeedbackAPIView,
)

urlpatterns = [
    # 認證 API
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', UserRegisterAPIView.as_view(), name='user-register'),
    path('auth/profile/', UserProfileAPIView.as_view(), name='user-profile'),

    # 群組與成員管理 API
    path('me/groups/', MyGroupsListAPIView.as_view(), name='my-group-list'),
    path('groups/', GroupCreateAPIView.as_view(), name='group-create'),
    path('groups/all/', GroupListAPIView.as_view(), name='group-list-all'),
    path('groups/<int:pk>/', GroupDetailAPIView.as_view(), name='group-detail'),
    path('groups/<int:pk>/members/', GroupMembersListAPIView.as_view(), name='group-members-list'),
    path('groups/<int:group_pk>/members/<int:user_pk>/role/', GroupMemberRoleAPIView.as_view(), name='group-member-role-update'),
    path('groups/<int:group_pk>/members/<int:user_pk>/', GroupMemberDeleteAPIView.as_view(), name='group-member-delete'),

    
    # 公告管理 API
    path('groups/<int:group_pk>/announcements/', GroupAnnouncementListCreateAPIView.as_view(), name='group-announcement-list-create'),
    path('announcements/<int:pk>/', GroupAnnouncementDetailAPIView.as_view(), name='announcement-detail'),
    path('groups/<int:group_pk>/invitations/', InvitationCodeCreateAPIView.as_view(), name='group-invitation-create'),

    # 數據讀取與報表 API
    path('personnel/', PersonnelListAPIView.as_view(), name='personnel-list'),
    path('devices/', DeviceListAPIView.as_view(), name='device-list'),
    path('trips/', TripListAPIView.as_view(), name='trip-list'),
    path('trips/<int:pk>/', TripDetailAPIView.as_view(), name='trip-detail'),
    path('videos/', VideoListAPIView.as_view(), name='video-list'),
    path('trips/<int:trip_pk>/report/', generate_trip_report_pdf, name='trip-report-pdf'), 
    
    # 統計 API
    path('statistics/trends/', UserTrendsAPIView.as_view(), name='user-trends'),
    
    # 樹莓派資料上傳 API
    path('trips/start/', TripStartAPIView.as_view(), name='trip-start'),
    path('trips/<int:pk>/end/', TripEndAPIView.as_view(), name='trip-end'),
    path('events/', AiVisionLogCreateAPIView.as_view(), name='event-create'),
    path('videos/', VideoRecordCreateAPIView.as_view(), name='video-create'),
    
    # AI 與系統狀態 API
    path('chatbot/', ChatbotAPIView.as_view(), name='chatbot'),
    path('chatbot/feedback/', ChatbotFeedbackAPIView.as_view(), name='chatbot-feedback'),
    path('health/', health_check, name='health-check'),
    path('system/stats/', system_stats, name='system-stats'),
]