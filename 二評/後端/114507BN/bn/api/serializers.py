# api/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    PersonnelProfile, Group, Trip, ScoringStandard,
    AiVisionLog, VideoRecord, VehicleDevice
)

# --- 基礎序列化器 ---

class PersonnelProfileSerializer(serializers.ModelSerializer):
    """【修改】Serializer for our custom profile data, now including all new fields."""
    class Meta:
        model = PersonnelProfile
        # 【修改】加入所有我們在 models.py 新增的欄位
        fields = [
            'personnel_number',
            'gender',
            'license_number',
            'avatar',                 # 新增
            'phone',                  # 新增
            'license_type',           # 新增
            'driving_experience'      # 新增
        ]

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model, including basic profile info."""
    personnelprofile = PersonnelProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'personnelprofile']

class GroupSerializer(serializers.ModelSerializer):
    """Serializer for the Group model."""
    class Meta:
        model = Group
        fields = '__all__' # 簡單起見，先回傳所有欄位

class VehicleDeviceSerializer(serializers.ModelSerializer):
    """Serializer for the VehicleDevice model."""
    class Meta:
        model = VehicleDevice
        fields = '__all__'

# --- 用於行程詳情的巢狀序列化器 ---

class ScoringStandardSerializer(serializers.ModelSerializer):
    """Serializer for ScoringStandard, used in AiVisionLog."""
    class Meta:
        model = ScoringStandard
        fields = ['event_number', 'description', 'deduction_points']

class AiVisionLogSerializer(serializers.ModelSerializer):
    """Serializer for AiVisionLog, with nested event details."""
    event = ScoringStandardSerializer(read_only=True)
    class Meta:
        model = AiVisionLog
        fields = ['timestamp', 'event_details', 'confidence_score', 'event']

class VideoRecordSerializer(serializers.ModelSerializer):
    """Serializer for VideoRecord."""
    class Meta:
        model = VideoRecord
        fields = ['video_number', 'start_time', 'end_time', 'location']

# --- 行程列表與詳情的序列化器 ---

class TripListSerializer(serializers.ModelSerializer):
    """
    Serializer for the Trip list view.
    Provides a summary of each trip.
    """
    # 顯示關聯物件的文字，而不是 ID
    personnel = serializers.StringRelatedField()
    group = serializers.StringRelatedField()
    device = serializers.StringRelatedField()

    class Meta:
        model = Trip
        # 【修改】將我們在 Trip 模型中新增的 total_mileage 欄位也加進來
        fields = ['id', 'trip_number', 'name', 'score', 'start_time', 'end_time', 'personnel', 'group', 'device', 'total_mileage']

class TripDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for the Trip detail view.
    Includes nested lists of all related logs and videos.
    """
    personnel = UserSerializer(read_only=True) # 巢狀顯示完整人員資訊
    group = GroupSerializer(read_only=True)
    device = VehicleDeviceSerializer(read_only=True)

    # 透過 related_name (需要您在 models.py 中定義) 來取得所有關聯的紀錄
    aivisionlog_set = AiVisionLogSerializer(many=True, read_only=True)
    videorecord_set = VideoRecordSerializer(many=True, read_only=True)

    class Meta:
        model = Trip
        # 【修改】將我們在 Trip 模型中新增的 total_mileage 欄位也加進來
        fields = [
            'id', 'trip_number', 'name', 'score', 'ai_suggestion', 'start_time', 'end_time',
            'personnel', 'group', 'device', 'aivisionlog_set', 'videorecord_set', 'total_mileage'
        ]

class TripStartSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for creating a new trip.
    It validates the incoming data from the Raspberry Pi.
    """
    # 我們讓 device 和 personnel 欄位可以直接接收傳入的 ID
    device = serializers.PrimaryKeyRelatedField(queryset=VehicleDevice.objects.all())
    personnel = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = Trip
        # 指定樹莓派在開始行程時，必須提供的欄位
        fields = ['id', 'trip_number', 'name', 'group', 'device', 'personnel', 'start_time']

class AiVisionLogCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new AiVisionLog entry from the Pi.
    """
    # Allows receiving the raw ID for foreign keys.
    trip = serializers.PrimaryKeyRelatedField(queryset=Trip.objects.all())
    event = serializers.PrimaryKeyRelatedField(queryset=ScoringStandard.objects.all())

    class Meta:
        model = AiVisionLog
        # Fields that the Raspberry Pi needs to send.
        fields = ['trip', 'event', 'timestamp', 'event_details', 'confidence_score']

class VideoRecordCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new VideoRecord entry from the Pi.
    """
    trip = serializers.PrimaryKeyRelatedField(queryset=VideoRecord.objects.all())

    class Meta:
        model = VideoRecord
        # Fields that the Raspberry Pi needs to send.
        fields = ['video_number', 'trip', 'start_time', 'end_time', 'location', 'file_size']

class TripEndSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for updating the end_time of a trip.
    """
    class Meta:
        model = Trip
        # Only the 'end_time' field can be updated through this serializer.
        fields = ['end_time']

class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles validation and creation of a new user with an encrypted password.
    """
    # 讓密碼欄位只在寫入時使用，讀取時不會被回傳
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    # 我們自訂的 Profile 欄位，一併處理
    personnelprofile = PersonnelProfileSerializer()

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'personnelprofile']

    def create(self, validated_data):
        """
        Override the create method to handle user creation and password hashing.
        """
        profile_data = validated_data.pop('personnelprofile')

        # 使用 User.objects.create_user() 來建立使用者，它會自動處理密碼加密
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )

        # 建立關聯的 PersonnelProfile
        PersonnelProfile.objects.create(user=user, **profile_data)

        return user