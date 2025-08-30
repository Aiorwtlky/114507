# api/views.py

from rest_framework import generics
from django.contrib.auth.models import User
from .models import Group, Trip, VehicleDevice
from .serializers import (
    UserSerializer, GroupSerializer, TripListSerializer, 
    TripDetailSerializer, VehicleDeviceSerializer
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
    # lookup_field = 'id' # 預設就是用 id 查詢