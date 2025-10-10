# api/views.py

from rest_framework import generics, status, permissions, views
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Q
from django.db.models.functions import TruncMonth
from django.template.loader import render_to_string
from weasyprint import HTML
import logging

# 專案內部模組匯入
from .models import (
    Group, Trip, VehicleDevice, AiVisionLog, VideoRecord, PersonnelProfile,
    GroupAnnouncement, InvitationCode, GroupMember, TripSuggestionFeedback
)
from .serializers import (
    UserSerializer, GroupSerializer, TripListSerializer,
    TripDetailSerializer, VehicleDeviceSerializer, TripStartSerializer,
    AiVisionLogCreateSerializer, TripEndSerializer,
    UserRegisterSerializer, GroupMemberSerializer,
    GroupAnnouncementSerializer, InvitationCodeSerializer,
    TripSuggestionFeedbackSerializer, VideoRegisterSerializer, VideoRecordSerializer,
    InvitationCodeCreateSerializer
)
from .services import calculate_trip_score, is_driver_on_active_trip, get_chatbot_response
from .permissions import IsOwnerOrAdmin, IsGroupOwnerOrAdmin, IsAnnouncementPublisherOrAdmin

logger = logging.getLogger(__name__)

class ApiRootView(APIView):
    """API 根路由視圖，提供 API 入口點的概覽。"""
    permission_classes = [AllowAny] # 允許任何人訪問

    def get(self, request, *args, **kwargs):
        api_info = {
            "message": "歡迎使用 MDG Pro API 系統",
            "endpoints": {
                "authentication": {
                    "token_obtain": "/token/",
                    "token_refresh": "/token/refresh/",
                    "register": "/auth/register/",
                    "profile": "/auth/profile/",
                },
                "groups": "/me/groups/",
                "trips": "/trips/",
                "chatbot": "/chatbot/",
            }
        }
        return Response(api_info)

# =============================================================================
# 輔助函式 (Helper Functions)
# =============================================================================

def is_leader_of(leader: User, member: User) -> bool:
    """檢查 'leader' 是否為 'member' 的管理者。"""
    if not leader or not member or not leader.is_authenticated:
        return False
    # 網站管理員 (Superuser/Staff) 擁有最高權限
    if leader.is_staff:
        return True
    # 檢查 leader 是否為 member 所在任何群組的建立者或管理員
    return GroupMember.objects.filter(
        user=member,
        group__in=GroupMember.objects.filter(user=leader, role='ADMIN').values('group')
    ).exists()

# =============================================================================
# 1. 認證與使用者 API (Authentication & User APIs)
# =============================================================================

class UserRegisterAPIView(generics.CreateAPIView):
    """(公開) 註冊新使用者。"""
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny] # 任何人都可註冊

# ▼▼▼【核心修改】簡化 UserProfileAPIView ▼▼▼
class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """
    (需登入) 讓使用者讀取與更新自己的個人資料。
    - GET: 獲取當前登入者的完整個人資料 (包含 Profile)。
    - PATCH/PUT: 更新當前登入者的個人資料 (支援巢狀更新 Profile)。
    【已簡化】更新邏輯已完全移至 UserSerializer，此處無需自訂方法。
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        # 此 API 的操作對象永遠是發出請求的當前使用者
        return self.request.user
# ▲▲▲【核心修改】▲▲▲

# =============================================================================
# 2. 群組與成員管理 API (Group & Member APIs)
# (此區塊維持原樣，結構良好)
# =============================================================================

class MyGroupsListAPIView(generics.ListAPIView):
    """(需登入) 獲取當前使用者所屬或建立的所有群組。"""
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # 使用 Q 物件組合查詢：是成員(members)或是建立者(created_by)
        return Group.objects.filter(Q(members=user) | Q(created_by=user)).distinct().order_by('-created_at')

class GroupCreateAPIView(generics.CreateAPIView):
    """(需登入) 建立新群組，並自動將建立者設為管理員。"""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        group = serializer.save(created_by=self.request.user)
        # 建立群組的同時，在 GroupMember 中介表中新增一筆紀錄，並設定角色為 ADMIN
        GroupMember.objects.create(group=group, user=self.request.user, role='ADMIN')

class GroupDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """(需權限) 讀取、更新、刪除單一群組。"""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsGroupOwnerOrAdmin]

class GroupMembersListAPIView(generics.ListAPIView):
    """(需登入) 獲取特定群組的成員列表 (含平均分數)。"""
    serializer_class = GroupMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs['pk']
        # 透過 annotate 計算每個成員的平均分數
        return User.objects.filter(joined_groups__id=group_id).annotate(average_score=Avg('trip__score')).order_by('username')
    
    def get_serializer_context(self):
        # 將 group_id 傳入 serializer context，以便 GroupMemberSerializer 能查詢對應的角色
        context = super().get_serializer_context()
        context['group_id'] = self.kwargs['pk']
        return context

class GroupMemberRoleAPIView(views.APIView):
    """(需權限) 更新群組成員的角色 (ADMIN/MEMBER)。"""
    permission_classes = [IsAuthenticated]

    def patch(self, request, group_pk, user_pk):
        group = get_object_or_404(Group, pk=group_pk)
        target_member_profile = get_object_or_404(GroupMember, group=group, user__id=user_pk)
        
        # 權限檢查：操作者必須是群組建立者、群組管理員或網站管理員
        is_owner = (group.created_by == request.user)
        is_group_admin = GroupMember.objects.filter(group=group, user=request.user, role='ADMIN').exists()
        if not (is_owner or request.user.is_staff or is_group_admin):
            raise PermissionDenied("您沒有權限變更成員角色。")
        
        # 規則檢查：不能移除群組建立者的管理員權限
        if group.created_by == target_member_profile.user and request.data.get('role') == 'MEMBER':
            raise PermissionDenied("不能移除群組建立者的管理員權限。")
            
        new_role = request.data.get('role')
        if new_role not in ['MEMBER', 'ADMIN']:
            return Response({"error": "無效的角色，只能是 'MEMBER' 或 'ADMIN'。"}, status=status.HTTP_400_BAD_REQUEST)
            
        target_member_profile.role = new_role
        target_member_profile.save()
        return Response({"success": f"使用者 {target_member_profile.user.username} 的角色已更新為 {new_role}"}, status=status.HTTP_200_OK)

class GroupMemberDeleteAPIView(views.APIView):
    """(需權限) 從群組中移除一名成員。"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, group_pk, user_pk):
        group = get_object_or_404(Group, pk=group_pk)
        target_user = get_object_or_404(User, pk=user_pk)
        membership = get_object_or_404(GroupMember, group=group, user=target_user)
        
        is_owner = (group.created_by == request.user)
        is_group_admin = GroupMember.objects.filter(group=group, user=request.user, role='ADMIN').exists()
        
        # 權限與規則檢查
        if not (is_owner or is_group_admin or request.user.is_staff):
            raise PermissionDenied("您沒有權限移除成員。")
        if group.created_by == target_user:
            return Response({"error": "不能移除群組的建立者。"}, status=status.HTTP_403_FORBIDDEN)
        if membership.role == 'ADMIN' and not is_owner:
             return Response({"error": "只有群組建立者可以移除其他管理員。"}, status=status.HTTP_403_FORBIDDEN)
             
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# =============================================================================
# 3. 公告與邀請碼 API (Announcement & Invitation APIs)
# =============================================================================

class GroupAnnouncementListCreateAPIView(generics.ListCreateAPIView):
    """(需權限) 獲取或建立特定群組的公告。"""
    serializer_class = GroupAnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        group_pk = self.kwargs['group_pk']
        return GroupAnnouncement.objects.filter(group__id=group_pk).order_by('-publish_date')

    def perform_create(self, serializer):
        group = get_object_or_404(Group, pk=self.kwargs['group_pk'])
        is_owner = (group.created_by == self.request.user)
        is_group_admin = GroupMember.objects.filter(group=group, user=self.request.user, role='ADMIN').exists()
        if not (is_owner or self.request.user.is_staff or is_group_admin):
            raise PermissionDenied("您沒有權限在此群組中發布公告。")
        serializer.save(publisher=self.request.user, group=group)

class GroupAnnouncementDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """(需權限) 讀取、更新、刪除單則公告。"""
    queryset = GroupAnnouncement.objects.all()
    serializer_class = GroupAnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated, IsAnnouncementPublisherOrAdmin]

class RecentAnnouncementsAPIView(generics.ListAPIView):
    """
    (公開) 獲取最新的 5 則公告，用於網站首頁等公開場合。
    """
    # 查詢所有公告，按發布日期倒序排列，只取前 5 筆
    queryset = GroupAnnouncement.objects.all().order_by('-publish_date')[:5]
    serializer_class = GroupAnnouncementSerializer
    # 允許任何人訪問
    permission_classes = [AllowAny]

class InvitationCodeCreateAPIView(generics.CreateAPIView):
    """(需權限) 為特定群組建立一個新的邀請碼。"""
    serializer_class = InvitationCodeCreateSerializer 
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # 覆寫 create 方法，以便在成功後回傳完整的邀請碼物件
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # 使用 InvitationCodeSerializer 來序列化新建立的物件並回傳
        instance = serializer.instance
        response_serializer = InvitationCodeSerializer(instance, context=self.get_serializer_context())
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        group = get_object_or_404(Group, pk=self.kwargs['group_pk'])
        # 權限檢查：必須是群組管理員或建立者
        is_owner = (group.created_by == self.request.user)
        is_group_admin = GroupMember.objects.filter(group=group, user=self.request.user, role='ADMIN').exists()
        if not (is_owner or self.request.user.is_staff or is_group_admin):
            raise PermissionDenied("您沒有權限為此群組生成邀請碼。")
        # 自動填入建立者和所屬群組
        serializer.save(created_by=self.request.user, group=group)

class InvitationCodeListAPIView(generics.ListAPIView):
    """【新增】獲取特定群組的所有邀請碼列表。"""
    serializer_class = InvitationCodeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        group_pk = self.kwargs['group_pk']
        group = get_object_or_404(Group, pk=group_pk)
        # 權限檢查：必須是群組成員
        if not group.members.filter(id=self.request.user.id).exists() and group.created_by != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("您沒有權限查看此群組的邀請碼。")
        return InvitationCode.objects.filter(group=group).order_by('-created_at')

class InvitationCodeManageAPIView(generics.DestroyAPIView):
    """【新增】管理（目前只有刪除/撤銷）單一邀請碼。"""
    queryset = InvitationCode.objects.all()
    serializer_class = InvitationCodeSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        # 權限檢查：必須是邀請碼的建立者，或是群組的管理員/建立者
        user = self.request.user
        is_creator = instance.created_by == user
        is_group_owner = instance.group.created_by == user
        is_group_admin = GroupMember.objects.filter(group=instance.group, user=user, role='ADMIN').exists()
        if not (is_creator or is_group_owner or is_group_admin or user.is_staff):
            raise PermissionDenied("您沒有權限撤銷此邀請碼。")
        instance.delete()

# =============================================================================
# 4. 數據讀取與報表 API (Data & Report APIs)
# =============================================================================

class TripListAPIView(generics.ListAPIView):
    """(需登入) 行程列表 API，管理者可使用 ?user_id=<id> 查詢特定成員。"""
    serializer_class = TripListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if target_user_id := self.request.query_params.get('user_id'):
            target_user = get_object_or_404(User, pk=target_user_id)
            if not is_leader_of(user, target_user):
                raise PermissionDenied("您沒有權限查看此使用者的行程。")
            return Trip.objects.filter(personnel=target_user).order_by('-start_time')
        else:
            if user.is_staff:
                return Trip.objects.all().order_by('-start_time')
            return Trip.objects.filter(personnel=user).order_by('-start_time')

class TripDetailAPIView(generics.RetrieveAPIView):
    """(需權限) 讀取單一行程的完整詳情。"""
    queryset = Trip.objects.all()
    serializer_class = TripDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

class VideoListAPIView(generics.ListAPIView):
    """(需登入) 影片列表 API，管理者可使用 ?user_id=<id> 查詢特定成員。"""
    serializer_class = VideoRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if target_user_id := self.request.query_params.get('user_id'):
            target_user = get_object_or_404(User, pk=target_user_id)
            if not is_leader_of(user, target_user):
                raise PermissionDenied("您沒有權限查看此使用者的影片。")
            return VideoRecord.objects.filter(trip__personnel=target_user).order_by('-start_time')
        else:
            return VideoRecord.objects.filter(trip__personnel=user).order_by('-start_time')

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def generate_trip_report_pdf(request, trip_pk):
    """(需權限) 根據 trip_pk 動態生成一份 PDF 報告並回傳。"""
    trip = get_object_or_404(Trip, pk=trip_pk)
    if trip.personnel != request.user and not request.user.is_staff:
        raise PermissionDenied("您沒有權限生成此報告。")
    context = {'trip': trip}
    html_string = render_to_string('api/report_template.html', context)
    pdf_file = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="trip_report_{trip.trip_number}.pdf"'
    return response

# =============================================================================
# 5. 車機端上傳 API (Device Upload APIs)
# =============================================================================

class TripStartAPIView(generics.CreateAPIView):
    """(車機用) 開始一趟新行程。"""
    queryset = Trip.objects.all()
    serializer_class = TripStartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        driver = request.user
        if is_driver_on_active_trip(driver):
            logger.warning(f"使用者 {driver.username} 試圖在已有進行中行程的狀況下開啟新行程")
            return Response({"error": "駕駛員已有一趟進行中的行程。"}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

class TripEndAPIView(generics.UpdateAPIView):
    """(車機用) 結束一趟行程，並觸發計分。"""
    queryset = Trip.objects.all()
    serializer_class = TripEndSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            if trip_id := kwargs.get('pk'):
                calculate_trip_score(trip_id)
        return response

class AiVisionLogCreateAPIView(generics.CreateAPIView):
    """(車機用) 上傳一筆 AI 視覺事件紀錄。"""
    queryset = AiVisionLog.objects.all()
    serializer_class = AiVisionLogCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

class VideoRegisterAPIView(generics.CreateAPIView):
    """(車機用) 註冊一筆已上傳至雲端的影片。"""
    queryset = VideoRecord.objects.all()
    serializer_class = VideoRegisterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        trip = serializer.validated_data['trip']
        if trip.personnel != self.request.user:
            raise PermissionDenied("您沒有權限為這趟行程註冊影片。")
        serializer.save()

# =============================================================================
# 6. AI、統計與系統 API (AI, Stats & System APIs)
# =============================================================================

class ChatbotAPIView(views.APIView):
    """(需登入) AI 智慧客服對話 API。"""
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        chat_history = request.data.get('messages', [])
        if not isinstance(chat_history, list) or not chat_history:
            return Response({"error": "請求的 'messages' 欄位必須是一個非空的列表。"}, status=status.HTTP_400_BAD_REQUEST)
        logger.info(f"來自使用者 {request.user.username} 的 Chatbot 請求")
        ai_reply = get_chatbot_response(chat_history)
        return Response({"reply": ai_reply}, status=status.HTTP_200_OK)

class UserTrendsAPIView(views.APIView):
    """(需登入) 使用者駕駛分數趨勢 API (月平均)。"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        if target_user_id := request.query_params.get('user_id'):
            target_user = get_object_or_404(User, pk=target_user_id)
            if not is_leader_of(user, target_user):
                raise PermissionDenied("您沒有權限查看此使用者的統計資料。")
        else:
            target_user = user
        trends = Trip.objects.filter(personnel=target_user, score__isnull=False).annotate(month=TruncMonth('start_time')).values('month').annotate(average_score=Avg('score')).values('month', 'average_score').order_by('month')
        formatted_trends = [{"month": item['month'].strftime('%Y-%m'), "average_score": round(item['average_score'], 1)} for item in trends]
        return Response(formatted_trends)

class TripSuggestionFeedbackAPIView(generics.CreateAPIView):
    """(需登入) 接收使用者對 AI 行程建議的回饋。"""
    queryset = TripSuggestionFeedback.objects.all()
    serializer_class = TripSuggestionFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        trip = serializer.validated_data['trip']
        user = self.request.user
        if trip.personnel != user:
            raise PermissionDenied("您只能對自己的行程提供回饋。")
        if TripSuggestionFeedback.objects.filter(trip=trip, user=user).exists():
            raise serializer.ValidationError("您已經對此行程提交過回饋。")
        serializer.save(user=user)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """(公開) 系統健康檢查 API。"""
    try:
        from django.db import connection
        with connection.cursor() as cursor: cursor.execute("SELECT 1")
        from .services import client
        ai_status = "available" if client else "unavailable"
        return JsonResponse({'status': 'healthy', 'database': 'connected', 'ai_service': ai_status})
    except Exception as e:
        logger.error(f"健康檢查失敗: {e}")
        return JsonResponse({'status': 'unhealthy', 'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def system_stats(request):
    """(管理者用) 獲取高階系統統計數據。"""
    stats = {
        'total_users': User.objects.count(),
        'total_trips': Trip.objects.count(),
        'active_trips': Trip.objects.filter(end_time__isnull=True).count(),
        'total_groups': Group.objects.count(),
        'active_devices': VehicleDevice.objects.filter(is_active=True).count(),
    }
    return JsonResponse(stats)

# =============================================================================
# 7. NFC 相關 API
# =============================================================================

class FindUserByNFCAPIView(views.APIView):
    """(需登入) (GET) 根據 NFC 卡 ID 查詢對應的使用者。"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        nfc_id = request.query_params.get('nfc_id')
        if not nfc_id:
            return Response({"error": "請提供 nfc_id 查詢參數。"}, status=status.HTTP_400_BAD_REQUEST)
        profile = get_object_or_404(PersonnelProfile, nfc_card_id=nfc_id)
        serializer = UserSerializer(profile.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class BindNFCAPIView(views.APIView):
    """(管理者用) (PATCH) 為指定的使用者綁定一張 NFC 卡。"""
    permission_classes = [IsAdminUser]

    def patch(self, request, user_id, *args, **kwargs):
        nfc_id = request.data.get('nfc_id')
        if not nfc_id:
            return Response({"error": "請在請求內容中提供 nfc_id。"}, status=status.HTTP_400_BAD_REQUEST)
        if PersonnelProfile.objects.filter(nfc_card_id=nfc_id).exclude(user__id=user_id).exists():
            return Response({"error": "此 NFC 卡已被其他使用者綁定。"}, status=status.HTTP_409_CONFLICT)
        profile = get_object_or_404(PersonnelProfile, user__id=user_id)
        profile.nfc_card_id = nfc_id
        profile.save()
        return Response({"success": f"已成功為使用者 {profile.user.username} 綁定 NFC 卡 ID: {nfc_id}"}, status=status.HTTP_200_OK)

class UserSelfBindNFCAPIView(views.APIView):
    """(需登入) (POST) 讓當前登入的使用者自行綁定 NFC 卡。"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        nfc_id = request.data.get('nfc_id')
        if not nfc_id:
            return Response({"error": "請在請求內容中提供 nfc_id。"}, status=status.HTTP_400_BAD_REQUEST)
        if PersonnelProfile.objects.filter(nfc_card_id=nfc_id).exclude(user=request.user).exists():
            return Response({"error": "此 NFC 卡已被其他使用者綁定。"}, status=status.HTTP_409_CONFLICT)
        profile = request.user.personnelprofile
        profile.nfc_card_id = nfc_id
        profile.save()
        return Response({"success": f"您已成功綁定 NFC 卡 ID: {nfc_id}"}, status=status.HTTP_200_OK)

# =============================================================================
# (管理員專用) 基礎模型管理 API
# =============================================================================

class PersonnelListAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        return User.objects.filter(is_active=True).order_by('username')

class GroupListAPIView(generics.ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAdminUser]

class DeviceListAPIView(generics.ListAPIView):
    queryset = VehicleDevice.objects.filter(is_active=True)
    serializer_class = VehicleDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]