# api/views.py

from rest_framework import generics, status, permissions, views
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Q
from django.db.models.functions import TruncMonth
from django.template.loader import render_to_string
from weasyprint import HTML
import logging

from .models import (
    Group, Trip, VehicleDevice, AiVisionLog, VideoRecord, PersonnelProfile,
    GroupAnnouncement, InvitationCode, GroupMember
)
from .serializers import (
    UserSerializer, GroupSerializer, TripListSerializer,
    TripDetailSerializer, VehicleDeviceSerializer, TripStartSerializer,
    AiVisionLogCreateSerializer, VideoRecordCreateSerializer, TripEndSerializer,
    UserRegisterSerializer, PersonnelProfileSerializer, GroupMemberSerializer,
    GroupAnnouncementSerializer, VideoRecordSerializer, InvitationCodeSerializer
)
from .services import calculate_trip_score, is_driver_on_active_trip, get_chatbot_response
from .permissions import IsOwnerOrAdmin, IsGroupOwnerOrAdmin, IsAnnouncementPublisherOrAdmin

logger = logging.getLogger(__name__)

# --- Helper Function for Permission Check ---
def is_leader_of(leader, member):
    """檢查 'leader' 是否為 'member' 的組長 (群組建立者) 或管理員"""
    if not leader or not member:
        return False
    if leader.is_staff:
        return True
    # 檢查是否存在一個群組，其成員包含 member 且建立者是 leader
    return Group.objects.filter(members=member, created_by=leader).exists()

# =============================================================================
# 認證與使用者 Views
# =============================================================================

class UserRegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """讓用戶查看和更新自己的個人資料 (User + PersonnelProfile)"""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PersonnelProfileSerializer
        return UserSerializer

    def get_object(self):
        if self.request.method in ['PUT', 'PATCH']:
            profile, created = PersonnelProfile.objects.get_or_create(user=self.request.user)
            return profile
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = request.user
        profile = self.get_object()
        data = request.data
        user_fields = ['username', 'email', 'first_name', 'last_name']
        user_data_to_update = {key: data[key] for key in user_fields if key in data}

        if 'password' in data and data['password']:
            user.set_password(data['password'])

        for key, value in user_data_to_update.items():
            setattr(user, key, value)
        user.save()

        profile_serializer = self.get_serializer(profile, data=data, partial=True)
        profile_serializer.is_valid(raise_exception=True)
        profile_serializer.save()

        final_user_serializer = UserSerializer(user, context=self.get_serializer_context())
        return Response(final_user_serializer.data, status=status.HTTP_200_OK)

# =============================================================================
# 群組與成員管理 API
# =============================================================================

class MyGroupsListAPIView(generics.ListAPIView):
    """獲取當前登入使用者所管理的所有群組列表"""
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # --- ▼▼▼【第二步】將 get_queryset 方法替換為以下內容 ▼▼▼ ---
        # 查詢條件：群組的成員包含我，或者，群組的建立者是我
        return Group.objects.filter(
            Q(members=user) | Q(created_by=user)
        ).distinct().order_by('-created_at')
        # --- ▲▲▲ 請將 get_queryset 方法替換為以上內容 ▲▲▲ ---

class GroupCreateAPIView(generics.CreateAPIView):
    """建立新群組"""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        group = serializer.instance
        GroupMember.objects.create(group=group, user=self.request.user)


class GroupDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """讀取、更新、刪除單一群組"""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated, IsGroupOwnerOrAdmin]

class GroupMembersListAPIView(generics.ListAPIView):
    """獲取特定群組的成員列表 (包含計算後的平均分數)"""
    serializer_class = GroupMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs['pk']
        return User.objects.filter(
            joined_groups__id=group_id
        ).annotate(
            average_score=Avg('trip__score')
        ).order_by('username')

# =============================================================================
# 公告管理 API
# =============================================================================

class GroupAnnouncementListCreateAPIView(generics.ListCreateAPIView):
    """讀取特定群組的公告列表 (GET) 或在該群組下建立新公告 (POST)"""
    serializer_class = GroupAnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 從 URL 中獲取 group_pk 參數，並篩選出對應的公告
        group_pk = self.kwargs['group_pk']
        return GroupAnnouncement.objects.filter(group__id=group_pk).order_by('-publish_date')

    def perform_create(self, serializer):
            group = get_object_or_404(Group, pk=self.kwargs['group_pk'])
            
            # --- ▼▼▼ 修改權限檢查邏輯 ▼▼▼ ---
            is_owner = (group.created_by == self.request.user)
            is_staff = self.request.user.is_staff
            is_group_admin = GroupMember.objects.filter(group=group, user=self.request.user, role='ADMIN').exists()

            if not (is_owner or is_staff or is_group_admin):
                raise PermissionDenied("您沒有權限在此群組中發布公告。")
            # --- ▲▲▲ 修改結束 ▲▲▲ ---
            serializer.save(publisher=self.request.user, group=group)

class GroupAnnouncementDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """讀取、更新、刪除單則公告"""
    queryset = GroupAnnouncement.objects.all()
    serializer_class = GroupAnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated, IsAnnouncementPublisherOrAdmin]

class InvitationCodeCreateAPIView(generics.CreateAPIView):
    """為特定群組建立一個新的邀請碼"""
    serializer_class = InvitationCodeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        group = get_object_or_404(Group, pk=self.kwargs['group_pk'])

        # --- ▼▼▼ 修改權限檢查邏輯 ▼▼▼ ---
        is_owner = (group.created_by == self.request.user)
        is_staff = self.request.user.is_staff
        is_group_admin = GroupMember.objects.filter(group=group, user=self.request.user, role='ADMIN').exists()

        if not (is_owner or is_staff or is_group_admin):
            raise PermissionDenied("您沒有權限為此群組生成邀請碼。")
        # --- ▲▲▲ 修改結束 ▲▲▲ ---

        serializer.save(created_by=self.request.user, group=group)

# =============================================================================
# 數據讀取 API (含查詢擴充)
# =============================================================================

class PersonnelListAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        return User.objects.filter(is_active=True).order_by('username')

class GroupListAPIView(generics.ListAPIView):
    """(管理員用) 獲取系統內所有群組"""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAdminUser]

class DeviceListAPIView(generics.ListAPIView):
    queryset = VehicleDevice.objects.filter(is_active=True)
    serializer_class = VehicleDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

class TripListAPIView(generics.ListAPIView):
    """行程列表 API，支援 ?user_id=<id> 查詢"""
    serializer_class = TripListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        target_user_id = self.request.query_params.get('user_id')

        if target_user_id:
            # 如果提供了 user_id，表示組長想查詢特定成員
            target_user = get_object_or_404(User, pk=target_user_id)
            # 權限檢查：請求者必須是管理員，或是該成員的組長
            if not is_leader_of(user, target_user):
                raise PermissionDenied("You do not have permission to view this user's trips.")
            return Trip.objects.filter(personnel=target_user).order_by('-start_time')
        else:
            # 如果沒提供 user_id，維持原有邏輯
            if user.is_staff:
                return Trip.objects.all().order_by('-start_time')
            return Trip.objects.filter(personnel=user).order_by('-start_time')

class TripDetailAPIView(generics.RetrieveAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

class VideoListAPIView(generics.ListAPIView):
    """影片列表 API，支援 ?user_id=<id> 查詢"""
    serializer_class = VideoRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        target_user_id = self.request.query_params.get('user_id')

        if target_user_id:
            target_user = get_object_or_404(User, pk=target_user_id)
            if not is_leader_of(user, target_user):
                raise PermissionDenied("You do not have permission to view this user's videos.")
            # 透過 trip__personnel 跨模型查詢
            return VideoRecord.objects.filter(trip__personnel=target_user).order_by('-start_time')
        else:
            return VideoRecord.objects.filter(trip__personnel=user).order_by('-start_time')

# =============================================================================
# 樹莓派資料上傳 API
# =============================================================================

class TripStartAPIView(generics.CreateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripStartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        driver = request.user
        if is_driver_on_active_trip(driver):
            logger.warning(f"User {driver.username} tried to start trip while already on active trip")
            return Response({"error": "Driver is already on an active trip."}, status=status.HTTP_400_BAD_REQUEST)
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            logger.info(f"Trip started successfully by user {driver.username}")
        return response

class TripEndAPIView(generics.UpdateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripEndSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            trip_id = kwargs.get('pk')
            if trip_id:
                calculate_trip_score(trip_id)
        return response

class AiVisionLogCreateAPIView(generics.CreateAPIView):
    queryset = AiVisionLog.objects.all()
    serializer_class = AiVisionLogCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

class VideoRecordCreateAPIView(generics.CreateAPIView):
    queryset = VideoRecord.objects.all()
    serializer_class = VideoRecordCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

# =============================================================================
# AI、系統狀態與統計 API
# =============================================================================

class ChatbotAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        chat_history = request.data.get('messages', [])
        if not isinstance(chat_history, list) or not chat_history:
            return Response({"error": "請求的 'messages' 欄位必須是一個非空的列表。"}, status=status.HTTP_400_BAD_REQUEST)
        logger.info(f"Chatbot request from user {request.user.username}")
        ai_reply = get_chatbot_response(chat_history)
        return Response({"reply": ai_reply}, status=status.HTTP_200_OK)

class UserTrendsAPIView(views.APIView):
    """使用者駕駛分數趨勢 API (月平均)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        target_user_id = request.query_params.get('user_id')

        if target_user_id:
            target_user = get_object_or_404(User, pk=target_user_id)
            if not is_leader_of(user, target_user):
                raise PermissionDenied("You do not have permission to view this user's stats.")
        else:
            target_user = user
        
        trends = Trip.objects.filter(
            personnel=target_user,
            score__isnull=False
        ).annotate(
            month=TruncMonth('start_time')
        ).values(
            'month'
        ).annotate(
            average_score=Avg('score')
        ).values(
            'month', 'average_score'
        ).order_by('month')

        formatted_trends = [
            {
                "month": item['month'].strftime('%Y-%m'),
                "average_score": round(item['average_score'], 1)
            } for item in trends
        ]

        return Response(formatted_trends)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        from .services import client
        ai_status = "available" if client else "unavailable"
        return JsonResponse({'status': 'healthy', 'database': 'connected', 'ai_service': ai_status, 'version': '1.0.0'})
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JsonResponse({'status': 'unhealthy', 'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def system_stats(request):
    stats = {
        'total_users': User.objects.count(),
        'total_trips': Trip.objects.count(),
        'active_trips': Trip.objects.filter(end_time__isnull=True).count(),
        'total_groups': Group.objects.count(),
        'active_devices': VehicleDevice.objects.filter(is_active=True).count(),
    }
    return JsonResponse(stats)

# =============================================================================
# PDF 報表生成 API
# =============================================================================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def generate_trip_report_pdf(request, trip_pk):
    """根據 trip_pk 動態生成一份 PDF 報告並回傳"""
    trip = get_object_or_404(Trip, pk=trip_pk)
    
    # 權限檢查：確保請求者是該行程的擁有者或管理員
    if trip.personnel != request.user and not request.user.is_staff:
        raise PermissionDenied("You do not have permission to generate this report.")

    # 將 trip 物件渲染到 HTML 範本中
    context = {'trip': trip}
    html_string = render_to_string('api/report_template.html', context)

    # 使用 WeasyPrint 將 HTML 字串轉換成 PDF
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()

    # 建立一個 HTTP Response，並設定正確的 Content-Type
    response = HttpResponse(pdf_file, content_type='application/pdf')
    
    # (可選) 設定 Content-Disposition 讓瀏覽器知道檔名
    response['Content-Disposition'] = f'inline; filename="trip_report_{trip.trip_number}.pdf"'

    return response


class GroupMemberRoleAPIView(views.APIView):
    """更新群組成員的角色"""
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, group_pk, user_pk):
            group = get_object_or_404(Group, pk=group_pk)
            target_member_profile = get_object_or_404(GroupMember, group=group, user__id=user_pk)

            # --- ▼▼▼ 修改權限檢查邏輯 ▼▼▼ ---
            # 權限檢查：只有群組建立者或其他管理員才能變更角色
            is_owner = (group.created_by == request.user)
            is_staff = request.user.is_staff
            is_group_admin = GroupMember.objects.filter(group=group, user=request.user, role='ADMIN').exists()

            if not (is_owner or is_staff or is_group_admin):
                raise PermissionDenied("您沒有權限變更成員角色。")
            
            # 【新增】一個小限制：不能移除群組建立者自己的管理員權限
            if group.created_by == target_member_profile.user and request.data.get('role') == 'MEMBER':
                raise PermissionDenied("不能移除群組建立者的管理員權限。")
            # --- ▲▲▲ 修改結束 ▲▲▲ ---

            new_role = request.data.get('role')
            if new_role not in ['MEMBER', 'ADMIN']:
                return Response({"error": "無效的角色"}, status=status.HTTP_400_BAD_REQUEST)

            target_member_profile.role = new_role
            target_member_profile.save()
            return Response({"success": f"使用者 {target_member_profile.user.username} 的角色已更新為 {new_role}"}, status=status.HTTP_200_OK)