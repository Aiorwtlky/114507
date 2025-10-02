# api/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from django.db.models import Avg
from .models import (
    PersonnelProfile, Group, Trip, ScoringStandard,
    AiVisionLog, VideoRecord, VehicleDevice, GroupAnnouncement # 【新增】
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
        # 【修正一】將 is_groups_leader (複數) 改為 is_group_leader (單數)
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_group_leader', 'personnelprofile']

    def get_is_group_leader(self, obj):
        """
        【修正二】判斷邏輯改為：檢查此使用者(obj)是否為任何一個群組的建立者(created_by)。
        """
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


# --- 用於行程詳情的巢狀序列化器 ---

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

# --- 行程列表與詳情的序列化器 ---

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

# --- 資料建立/更新用的序列化器 ---

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

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    personnelprofile = PersonnelProfileSerializer()
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'personnelprofile']

    def create(self, validated_data):
        profile_data = validated_data.pop('personnelprofile')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        PersonnelProfile.objects.create(user=user, **profile_data)
        return user