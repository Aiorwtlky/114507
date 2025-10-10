# api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    ApiRootView,
    # 認證與使用者
    UserRegisterAPIView, UserProfileAPIView, UserSelfBindNFCAPIView,
    # NFC 相關
    FindUserByNFCAPIView, BindNFCAPIView,
    # 群組與成員
    MyGroupsListAPIView, GroupCreateAPIView, GroupDetailAPIView,
    GroupMembersListAPIView, GroupMemberRoleAPIView, GroupMemberDeleteAPIView,
    # 公告與邀請碼
    GroupAnnouncementListCreateAPIView, GroupAnnouncementDetailAPIView,
    InvitationCodeCreateAPIView, RecentAnnouncementsAPIView,
    # 數據讀取與報表
    TripListAPIView, TripDetailAPIView, VideoListAPIView, generate_trip_report_pdf,
    # 車機上傳
    TripStartAPIView, TripEndAPIView, AiVisionLogCreateAPIView, VideoRegisterAPIView,
    # AI、統計與系統
    ChatbotAPIView, TripSuggestionFeedbackAPIView, UserTrendsAPIView,
    health_check, system_stats,
    # (管理員專用)
    PersonnelListAPIView, GroupListAPIView, DeviceListAPIView,
)

urlpatterns = [
    path('',ApiRootView.as_view(), name='api-root'),
    # 1. 認證 API
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', UserRegisterAPIView.as_view(), name='user-register'),
    path('auth/profile/', UserProfileAPIView.as_view(), name='user-profile'),
    path('auth/profile/bind-nfc/', UserSelfBindNFCAPIView.as_view(), name='user-self-bind-nfc'),

    # 2. NFC 相關 API
    path('users/by-nfc/', FindUserByNFCAPIView.as_view(), name='find-user-by-nfc'),
    path('personnel/<int:user_id>/bind-nfc/', BindNFCAPIView.as_view(), name='admin-bind-nfc'),

    # 3. 群組與成員管理 API
    path('me/groups/', MyGroupsListAPIView.as_view(), name='my-group-list'),
    path('groups/', GroupCreateAPIView.as_view(), name='group-create'),
    path('groups/<int:pk>/', GroupDetailAPIView.as_view(), name='group-detail'),
    path('groups/<int:pk>/members/', GroupMembersListAPIView.as_view(), name='group-members-list'),
    path('groups/<int:group_pk>/members/<int:user_pk>/', GroupMemberDeleteAPIView.as_view(), name='group-member-delete'),
    path('groups/<int:group_pk>/members/<int:user_pk>/role/', GroupMemberRoleAPIView.as_view(), name='group-member-role-update'),
    
    # 4. 公告與邀請碼 API
    path('groups/<int:group_pk>/announcements/', GroupAnnouncementListCreateAPIView.as_view(), name='group-announcement-list-create'),
    path('groups/<int:group_pk>/invitations/', InvitationCodeCreateAPIView.as_view(), name='group-invitation-create'),
    path('announcements/<int:pk>/', GroupAnnouncementDetailAPIView.as_view(), name='announcement-detail'),
    path('announcements/recent/', RecentAnnouncementsAPIView.as_view(), name='recent-announcements'),
    
    # 5. 數據讀取與報表 API
    path('trips/', TripListAPIView.as_view(), name='trip-list'),
    path('trips/<int:pk>/', TripDetailAPIView.as_view(), name='trip-detail'),
    path('trips/<int:trip_pk>/report/', generate_trip_report_pdf, name='trip-report-pdf'),
    path('videos/', VideoListAPIView.as_view(), name='video-list'), # 這是讀取列表的 API
    
    # 6. 車機上傳 API
    path('trips/start/', TripStartAPIView.as_view(), name='trip-start'),
    path('trips/<int:pk>/end/', TripEndAPIView.as_view(), name='trip-end'),
    path('events/', AiVisionLogCreateAPIView.as_view(), name='event-create'),
    path('videos/register/', VideoRegisterAPIView.as_view(), name='video-register'), # 這是註冊影片 URL 的 API

    # 7. AI、統計與回饋 API
    path('chatbot/', ChatbotAPIView.as_view(), name='chatbot'),
    path('statistics/trends/', UserTrendsAPIView.as_view(), name='user-trends'),
    path('trips/feedback/', TripSuggestionFeedbackAPIView.as_view(), name='trip-suggestion-feedback'),

    # 8. 系統狀態 API
    path('health/', health_check, name='health-check'),
    path('system/stats/', system_stats, name='system-stats'),

    # 9. (管理員專用) 列表 API
    path('personnel/', PersonnelListAPIView.as_view(), name='personnel-list'),
    path('devices/', DeviceListAPIView.as_view(), name='device-list'),
    path('groups/all/', GroupListAPIView.as_view(), name='group-list-all'),
]