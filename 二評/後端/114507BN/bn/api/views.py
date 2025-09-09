# api/views.py

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Group, Trip, VehicleDevice, AiVisionLog, VideoRecord
from .serializers import (
    UserSerializer, GroupSerializer, TripListSerializer,
    TripDetailSerializer, VehicleDeviceSerializer, TripStartSerializer,
    AiVisionLogCreateSerializer, VideoRecordCreateSerializer, TripEndSerializer,
    UserRegisterSerializer
)
# 導入我們擴充後的服務和新建的權限
from .services import calculate_trip_score, is_driver_on_active_trip
from .permissions import IsOwnerOrAdmin

# --- 註冊與登入 ---
class UserRegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

# --- 數據讀取 API (加入更精細的權限) ---
class PersonnelListAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser] # 【修改】只有管理員才能看所有人員列表
    def get_queryset(self):
        return User.objects.filter(is_active=True).order_by('username')

class TripListAPIView(generics.ListAPIView):
    serializer_class = TripListSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        """
        Overrides the default queryset to return trips only for the current user.
        If the user is an admin (staff), return all trips.
        """
        user = self.request.user
        if user.is_staff:
            return Trip.objects.all().order_by('-start_time')
        # 【修改】普通使用者只能看到自己的行程
        return Trip.objects.filter(personnel=user).order_by('-start_time')

class TripDetailAPIView(generics.RetrieveAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripDetailSerializer
    # 【修改】登入且是行程擁有者或管理員才能看
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin] 

# --- 數據接收 API (加入商業邏輯驗證) ---
class TripStartAPIView(generics.CreateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripStartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # 將當前登入的使用者，自動設為行程的駕駛員
        serializer.save(personnel=self.request.user)

    def create(self, request, *args, **kwargs):
        # 【商業邏輯】檢查駕駛是否已在另一趟行程中
        driver = request.user
        if is_driver_on_active_trip(driver):
            return Response(
                {"error": "Driver is already on an active trip."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 如果檢查通過，才執行預設的建立操作
        return super().create(request, *args, **kwargs)

class TripEndAPIView(generics.UpdateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripEndSerializer
    # 【修改】只有行程擁有者或管理員才能結束行程
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