# api/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from django.db.models import Avg
from django.utils import timezone  # 【新增】匯入 timezone
from .models import (
    PersonnelProfile, Group, Trip, ScoringStandard,
    AiVisionLog, VideoRecord, VehicleDevice, GroupAnnouncement,
    InvitationCode, GroupMember  # 【新增】匯入 InvitationCode 和 GroupMember
)

# --- 基礎序列化器 ---

class PersonnelProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonnelProfile
        fields = ['personnel_number', 'gender', 'license_number', 'avatar', 'phone', 'license_type', 'driving_experience']

class UserSerializer(serializers.ModelSerializer):
    personnelprofile = PersonnelProfileSerializer(read_only=True)
    is_group_leader = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_group_leader', 'personnelprofile']

    def get_is_group_leader(self, obj):
        return Group.objects.filter(created_by=obj).exists()

class GroupMemberSerializer(serializers.ModelSerializer):
    average_score = serializers.FloatField(read_only=True, default=0)
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'average_score']

class GroupSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Group
        fields = ['id', 'group_number', 'name', 'description', 'created_by', 'created_at']

# --- 【新增這個 Serializer】 ---
class InvitationCodeSerializer(serializers.ModelSerializer):
    """用於顯示邀請碼的序列化器"""
    class Meta:
        model = InvitationCode
        fields = ['code', 'expires_at', 'group']
        read_only_fields = fields # 設為唯讀，因為這個 Serializer 只用於顯示

class GroupAnnouncementSerializer(serializers.ModelSerializer):
    publisher = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = GroupAnnouncement
        fields = ['id', 'announcement_number', 'content', 'publish_date', 'is_active', 'publisher', 'group']
        read_only_fields = ['publisher', 'group']

class VehicleDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleDevice
        fields = '__all__'

# --- (用於行程詳情的巢狀序列化器 - 維持不變) ---
class ScoringStandardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoringStandard
        fields = ['event_number', 'description', 'deduction_points']

class AiVisionLogSerializer(serializers.ModelSerializer):
    event = ScoringStandardSerializer(read_only=True)
    class Meta:
        model = AiVisionLog
        fields = ['timestamp', 'event_details', 'confidence_score', 'event']

class VideoRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoRecord
        fields = ['video_number', 'start_time', 'end_time', 'location']

# --- (行程列表與詳情的序列化器 - 維持不變) ---
class TripListSerializer(serializers.ModelSerializer):
    personnel = serializers.StringRelatedField()
    group = serializers.StringRelatedField()
    device = serializers.StringRelatedField()
    class Meta:
        model = Trip
        fields = ['id', 'trip_number', 'name', 'score', 'start_time', 'end_time', 'personnel', 'group', 'device', 'total_mileage']

class TripDetailSerializer(serializers.ModelSerializer):
    personnel = UserSerializer(read_only=True)
    group = GroupSerializer(read_only=True)
    device = VehicleDeviceSerializer(read_only=True)
    aivisionlog_set = AiVisionLogSerializer(many=True, read_only=True)
    videorecord_set = VideoRecordSerializer(many=True, read_only=True)
    class Meta:
        model = Trip
        fields = [
            'id', 'trip_number', 'name', 'score', 'ai_suggestion', 'start_time', 'end_time',
            'personnel', 'group', 'device', 'aivisionlog_set', 'videorecord_set', 'total_mileage'
        ]

# --- (資料建立/更新用的序列化器) ---
class TripStartSerializer(serializers.ModelSerializer):
    device = serializers.PrimaryKeyRelatedField(queryset=VehicleDevice.objects.all())
    personnel = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    class Meta:
        model = Trip
        fields = ['id', 'trip_number', 'name', 'group', 'device', 'personnel', 'start_time']

class TripEndSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['end_time']

class AiVisionLogCreateSerializer(serializers.ModelSerializer):
    trip = serializers.PrimaryKeyRelatedField(queryset=Trip.objects.all())
    event = serializers.PrimaryKeyRelatedField(queryset=ScoringStandard.objects.all())
    class Meta:
        model = AiVisionLog
        fields = ['trip', 'event', 'timestamp', 'event_details', 'confidence_score']

class VideoRecordCreateSerializer(serializers.ModelSerializer):
    trip = serializers.PrimaryKeyRelatedField(queryset=VideoRecord.objects.all())
    class Meta:
        model = VideoRecord
        fields = ['video_number', 'trip', 'start_time', 'end_time', 'location', 'file_size']

# --- 【修改這個 Serializer】 ---
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    personnelprofile = PersonnelProfileSerializer()
    
    # 【新增】接收前端傳來的邀請碼，非必填
    invitation_code = serializers.CharField(write_only=True, required=False, allow_blank=True, max_length=8)

    class Meta:
        model = User
        # 【修改】在 fields 中加入 invitation_code
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'personnelprofile', 'invitation_code']

    def create(self, validated_data):
        # 【修改】擴充 create 方法以處理邀請碼
        invitation_code = validated_data.pop('invitation_code', None)
        profile_data = validated_data.pop('personnelprofile')

        # 建立 User (這部分不變)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        # 建立 Profile (這部分不變)
        PersonnelProfile.objects.create(user=user, **profile_data)

        # 【新增】處理邀請碼的邏輯
        if invitation_code:
            try:
                # 尋找有效 (未使用、未過期) 的邀請碼
                invite = InvitationCode.objects.get(
                    code=invitation_code.upper(), # 轉換為大寫以匹配
                    is_used=False,
                    expires_at__gt=timezone.now()
                )
                # 將新使用者加入對應的群組
                GroupMember.objects.create(group=invite.group, user=user)
                # 將邀請碼標記為已使用
                invite.is_used = True
                invite.save()
            except InvitationCode.DoesNotExist:
                # 如果找不到有效的邀請碼，靜默處理，僅讓使用者成功註冊但不加入群組
                print(f"警告：使用者 {user.username} 提供了無效的邀請碼 '{invitation_code}'")
                pass
                
        return user