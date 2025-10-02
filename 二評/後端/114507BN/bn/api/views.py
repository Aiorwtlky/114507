# api/views.py

from rest_framework import generics, status, permissions, views
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.http import JsonResponse
from datetime import datetime
import logging

from .models import Group, Trip, VehicleDevice, AiVisionLog, VideoRecord, PersonnelProfile # 【修改】匯入 PersonnelProfile
from .serializers import (
    UserSerializer, GroupSerializer, TripListSerializer,
    TripDetailSerializer, VehicleDeviceSerializer, TripStartSerializer,
    AiVisionLogCreateSerializer, VideoRecordCreateSerializer, TripEndSerializer,
    UserRegisterSerializer, PersonnelProfileSerializer # 【修改】匯入 PersonnelProfileSerializer
)
from .services import calculate_trip_score, is_driver_on_active_trip, get_chatbot_response
from .permissions import IsOwnerOrAdmin

logger = logging.getLogger(__name__)

# =============================================================================
# 認證相關 Views
# =============================================================================
class CustomAuthToken(ObtainAuthToken):
    """
    自定義的 Token 認證 API，回傳更完整的用戶資訊
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        logger.info(f"User {user.username} logged in from {request.META.get('REMOTE_ADDR')}")
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff,
            'first_name': user.first_name,
            'last_name': user.last_name,
        })

class UserRegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]
    # 【說明】這個 View 不需要修改，因為 UserRegisterSerializer 已經處理了所有巢狀邏輯。

# --- 【以下為主要修改部分】 ---

class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """
    【修改】讓用戶查看和更新自己的個人資料 (User + PersonnelProfile)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    # 【修改】我們需要兩個 serializer，一個用於讀取 (GET)，一個用於寫入 (PUT/PATCH)
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            # 在更新時，我們只需要用到 Profile 的 serializer
            return PersonnelProfileSerializer
        # 在讀取時，我們使用 UserSerializer 來顯示完整的巢狀資料
        return UserSerializer

    def get_object(self):
        # 根據請求方法，決定要操作 User 物件還是其關聯的 Profile 物件
        if self.request.method in ['PUT', 'PATCH']:
            # 找到或建立該使用者的 Profile
            profile, created = PersonnelProfile.objects.get_or_create(user=self.request.user)
            return profile
        return self.request.user

    def update(self, request, *args, **kwargs):
        """
        【新增】自訂 update 方法以同時處理 User 和 PersonnelProfile 的更新
        """
        # 取得 User 和 Profile 物件
        user = request.user
        profile = self.get_object()
        
        # 取得傳入的資料
        data = request.data

        # 1. 更新 User 模型的欄位
        user_fields = ['username', 'email', 'first_name', 'last_name']
        user_data_to_update = {key: data[key] for key in user_fields if key in data}
        
        # 如果提供了 password，則需要特殊處理
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        # 將其他 User 欄位更新到物件
        for key, value in user_data_to_update.items():
            setattr(user, key, value)
        user.save()

        # 2. 更新 PersonnelProfile 模型的欄位
        # 使用 get_serializer 方法來處理 Profile 的部分更新 (partial=True)
        profile_serializer = self.get_serializer(profile, data=data, partial=True)
        profile_serializer.is_valid(raise_exception=True)
        profile_serializer.save()

        # 3. 回傳完整的、更新後的使用者資料
        # 我們用 UserSerializer 來回傳完整的巢狀結構
        final_user_serializer = UserSerializer(user, context=self.get_serializer_context())
        return Response(final_user_serializer.data, status=status.HTTP_200_OK)


# =============================================================================
# 數據讀取 API (加入更精細的權限)
# =============================================================================
class PersonnelListAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return User.objects.filter(is_active=True).order_by('username')

class TripListAPIView(generics.ListAPIView):
    serializer_class = TripListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Trip.objects.all().order_by('-start_time')
        return Trip.objects.filter(personnel=user).order_by('-start_time')

class TripDetailAPIView(generics.RetrieveAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

class TripStartAPIView(generics.CreateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripStartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            driver = request.user
            if is_driver_on_active_trip(driver):
                logger.warning(f"User {driver.username} tried to start trip while already on active trip")
                return Response(
                    {"error": "Driver is already on an active trip."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            response = super().create(request, *args, **kwargs)
            
            if response.status_code == status.HTTP_201_CREATED:
                logger.info(f"Trip started successfully by user {driver.username}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error starting trip for user {request.user.username}: {e}")
            return Response(
                {"error": "Failed to start trip. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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

# =============================================================================
# 其他資料 API
# =============================================================================
class GroupListAPIView(generics.ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class DeviceListAPIView(generics.ListAPIView):
    queryset = VehicleDevice.objects.filter(is_active=True)
    serializer_class = VehicleDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

class AiVisionLogCreateAPIView(generics.CreateAPIView):
    queryset = AiVisionLog.objects.all()
    serializer_class = AiVisionLogCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

class VideoRecordCreateAPIView(generics.CreateAPIView):
    queryset = VideoRecord.objects.all()
    serializer_class = VideoRecordCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

# =============================================================================
# AI 助理聊天 API 端點
# =============================================================================
class ChatbotAPIView(views.APIView):
    """
    處理前端 AI 助理的即時聊天請求。
    接收前端傳來的完整對話歷史，回傳 AI 的單次回覆。
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            chat_history = request.data.get('messages', [])

            if not isinstance(chat_history, list) or not chat_history:
                return Response(
                    {"error": "請求的 'messages' 欄位必須是一個非空的列表。"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            logger.info(f"Chatbot request from user {request.user.username}")
            
            ai_reply = get_chatbot_response(chat_history)
            
            return Response({"reply": ai_reply}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Chatbot error for user {request.user.username}: {e}")
            return Response(
                {"error": "助理系統內部發生錯誤，請稍後再試。"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# =============================================================================
# 系統健康檢查與狀態 API
# =============================================================================
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    系統健康檢查 API - 讓你知道系統是否正常運行
    """
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        from .services import client
        ai_status = "available" if client else "unavailable"
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'ai_service': ai_status,
            'version': '1.0.0'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def system_stats(request):
    """
    系統統計資訊 - 只有管理員可以查看
    """
    try:
        from django.contrib.auth.models import User
        from .models import Trip, Group, VehicleDevice
        
        stats = {
            'total_users': User.objects.count(),
            'total_trips': Trip.objects.count(),
            'active_trips': Trip.objects.filter(end_time__isnull=True).count(),
            'total_groups': Group.objects.count(),
            'active_devices': VehicleDevice.objects.filter(is_active=True).count(),
        }
        
        return JsonResponse(stats)
    except Exception as e:
        logger.error(f"System stats failed: {e}")
        return JsonResponse({'error': str(e)}, status=500)