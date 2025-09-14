# api/views.py

from rest_framework import generics, status, permissions, views # 【修改】匯入 views
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Group, Trip, VehicleDevice, AiVisionLog, VideoRecord
from .serializers import (
    UserSerializer, GroupSerializer, TripListSerializer,
    TripDetailSerializer, VehicleDeviceSerializer, TripStartSerializer,
    AiVisionLogCreateSerializer, VideoRecordCreateSerializer, TripEndSerializer,
    UserRegisterSerializer
)
# 【修改】導入 get_chatbot_response 服務
from .services import calculate_trip_score, is_driver_on_active_trip, get_chatbot_response
from .permissions import IsOwnerOrAdmin
from datetime import datetime

# --- 註冊與登入 ---
class UserRegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

# --- 數據讀取 API (加入更精細的權限) ---
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
        driver = request.user
        if is_driver_on_active_trip(driver):
            return Response(
                {"error": "Driver is already on an active trip."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

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
            
# --- 其他保持不變的 API ---
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
# 【全新】AI 助理聊天 API 端點
# =============================================================================
class ChatbotAPIView(views.APIView):
    """
    處理前端 AI 助理的即時聊天請求。
    接收前端傳來的完整對話歷史，回傳 AI 的單次回覆。
    """
    permission_classes = [permissions.IsAuthenticated] # 只有登入的使用者才能使用聊天功能

    def post(self, request, *args, **kwargs):
        # 1. 從前端請求中獲取對話歷史
        chat_history = request.data.get('messages', [])

        # 2. 進行基本驗證
        if not isinstance(chat_history, list) or not chat_history:
            return Response(
                {"error": "請求的 'messages' 欄位必須是一個非空的列表。"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. 呼叫我們在 services.py 中寫好的強大邏輯
        try:
            ai_reply = get_chatbot_response(chat_history)
            # 4. 將 AI 的回覆打包成 JSON 回傳給前端
            return Response({"reply": ai_reply}, status=status.HTTP_200_OK)
        except Exception as e:
            # 處理 service 層可能發生的未知錯誤
            print(f"[ChatbotAPIView] 發生未預期錯誤: {e}")
            return Response(
                {"error": "助理系統內部發生錯誤，請稍後再試。"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )