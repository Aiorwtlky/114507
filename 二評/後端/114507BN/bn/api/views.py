from rest_framework import generics
from django.contrib.auth.models import User
from .models import Group, Trip, VehicleDevice
from .serializers import (
    UserSerializer, GroupSerializer, TripListSerializer, VideoRecord, AiVisionLog,
    TripDetailSerializer, VehicleDeviceSerializer, TripStartSerializer,
    AiVisionLogCreateSerializer, VideoRecordCreateSerializer, TripEndSerializer,
    UserRegisterSerializer
)

# --- 人員相關 API ---
class PersonnelListAPIView(generics.ListAPIView):
    """API endpoint for listing personnel."""
    queryset = User.objects.filter(is_active=True).order_by('username')
    serializer_class = UserSerializer

# --- 群組相關 API ---
class GroupListAPIView(generics.ListAPIView):
    """API endpoint for listing groups."""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

# --- 車機相關 API ---
class DeviceListAPIView(generics.ListAPIView):
    """API endpoint for listing devices."""
    queryset = VehicleDevice.objects.filter(is_active=True)
    serializer_class = VehicleDeviceSerializer

# --- 行程相關 API ---
class TripListAPIView(generics.ListAPIView):
    """API endpoint for listing all trips."""
    queryset = Trip.objects.all().order_by('-start_time') # 依照開始時間倒序
    serializer_class = TripListSerializer

class TripDetailAPIView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a single trip's details.
    'Retrieve' means getting a single object.
    """
    queryset = Trip.objects.all()
    serializer_class = TripDetailSerializer

# --- 用於接收樹莓派數據的 API ---
class TripStartAPIView(generics.CreateAPIView):
    """
    API endpoint for the Raspberry Pi to start a new trip.
    Handles POST requests to create a new Trip instance.
    """
    queryset = Trip.objects.all()
    serializer_class = TripStartSerializer

class AiVisionLogCreateAPIView(generics.CreateAPIView):
    """
    API endpoint for the Pi to report a dangerous event.
    Handles POST requests to create a new AiVisionLog instance.
    """
    queryset = AiVisionLog.objects.all()
    serializer_class = AiVisionLogCreateSerializer

class VideoRecordCreateAPIView(generics.CreateAPIView):
    """
    API endpoint for the Pi to notify about a new video upload.
    Handles POST requests to create a new VideoRecord instance.
    """
    queryset = VideoRecord.objects.all()
    serializer_class = VideoRecordCreateSerializer

class TripEndAPIView(generics.UpdateAPIView):
    """
    API endpoint for the Pi to end a trip.
    Handles PUT/PATCH requests to update a Trip instance.
    """
    queryset = Trip.objects.all()
    serializer_class = TripEndSerializer

class UserRegisterAPIView(generics.CreateAPIView):
    """
    API endpoint for new user registration.
    """
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer