# api/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Avg
from django.utils import timezone 
from .models import (
    PersonnelProfile, Group, Trip, ScoringStandard,
    AiVisionLog, VideoRecord, VehicleDevice, GroupAnnouncement,
    InvitationCode, GroupMember, TripSuggestionFeedback
)

# =============================================================================
# 1. 唯讀與巢狀序列化器 (For Data Reading & Nesting)
# =============================================================================

class PersonnelProfileSerializer(serializers.ModelSerializer):
    """序列化人員詳細資料，並將頭像路徑轉為完整 URL。"""
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = PersonnelProfile
        fields = ['personnel_number', 'gender', 'license_number', 'avatar', 'phone', 'license_type', 'driving_experience']

    def get_avatar(self, obj):
        """自訂 avatar 欄位的輸出，產生絕對 URL。"""
        request = self.context.get('request')
        if obj.avatar and hasattr(obj.avatar, 'url'):
            return request.build_absolute_uri(obj.avatar.url)
        return None

class UserSerializer(serializers.ModelSerializer):
    """序列化使用者基本資料，並巢狀包含 Profile 與管理權限。"""
    personnelprofile = serializers.SerializerMethodField()
    is_group_leader = serializers.SerializerMethodField()
    administered_groups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 
                  'first_name', 'last_name', 'email', 'is_staff', 'is_group_leader', 'personnelprofile', 'administered_groups']

    def get_is_group_leader(self, obj):
        """檢查使用者是否為任何群組的建立者。"""
        return Group.objects.filter(created_by=obj).exists()
    
    def get_administered_groups(self, obj):
        """獲取使用者被指派為管理員的所有群組 ID 列表。"""
        admin_memberships = GroupMember.objects.filter(user=obj, role='ADMIN')
        return [membership.group.id for membership in admin_memberships]

    def get_personnelprofile(self, obj):
        """手動序列化 Profile，以確保 request context 被正確傳遞。"""
        try:
            profile = obj.personnelprofile
            request = self.context.get('request')
            return PersonnelProfileSerializer(profile, context={'request': request}).data
        except PersonnelProfile.DoesNotExist:
            return None

class GroupMemberSerializer(serializers.ModelSerializer):
    """序列化群組成員資料，包含其角色與 Profile。"""
    average_score = serializers.FloatField(read_only=True, default=0)
    role = serializers.SerializerMethodField()
    personnelprofile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'average_score', 'role', 'personnelprofile']

    def get_role(self, obj):
        """根據 context 中的 group_id，查詢使用者在該群組中的角色。"""
        group_id = self.context.get('group_id')
        if not group_id: return 'MEMBER'
        try:
            membership = GroupMember.objects.get(user=obj, group__id=group_id)
            return membership.role
        except GroupMember.DoesNotExist:
            return 'MEMBER'

    def get_personnelprofile(self, obj):
        """手動序列化 Profile，以確保 request context 能被傳遞。"""
        try:
            profile = obj.personnelprofile
            request = self.context.get('request')
            return PersonnelProfileSerializer(profile, context={'request': request}).data
        except PersonnelProfile.DoesNotExist:
            return None

class GroupSerializer(serializers.ModelSerializer):
    """序列化群組的基本資料。"""
    created_by = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Group
        fields = ['id', 'group_number', 'name', 'description', 'created_by', 'created_at']

class ScoringStandardSerializer(serializers.ModelSerializer):
    """序列化評分標準 (事件類型)。"""
    class Meta:
        model = ScoringStandard
        fields = ['event_number', 'description', 'deduction_points']

class AiVisionLogSerializer(serializers.ModelSerializer):
    """序列化 AI 視覺事件紀錄，並巢狀包含事件類型。"""
    event = ScoringStandardSerializer(read_only=True)
    class Meta:
        model = AiVisionLog
        fields = ['timestamp', 'event_details', 'confidence_score', 'event']

class VideoRecordSerializer(serializers.ModelSerializer):
    """序列化影像紀錄的文字資訊。"""
    class Meta:
        model = VideoRecord
        fields = ['video_number', 'start_time', 'end_time', 'location', 'video_url']

class TripListSerializer(serializers.ModelSerializer):
    """序列化行程列表，用於顯示簡化的行程資訊。"""
    personnel = serializers.StringRelatedField()
    group = serializers.StringRelatedField()
    device = serializers.StringRelatedField()
    class Meta:
        model = Trip
        fields = ['id', 'trip_number', 'name', 'score', 'in_car_score', 'out_car_score', 'start_time', 'end_time', 'personnel', 'group', 'device', 'total_mileage']

class TripDetailSerializer(serializers.ModelSerializer):
    """序列化單一行程的完整詳情，包含所有相關的巢狀資料。"""
    personnel = UserSerializer(read_only=True)
    group = GroupSerializer(read_only=True)
    device = serializers.StringRelatedField(read_only=True)
    aivisionlog_set = AiVisionLogSerializer(many=True, read_only=True)
    videorecord_set = VideoRecordSerializer(many=True, read_only=True)
    class Meta:
        model = Trip
        fields = [
            'id', 'trip_number', 'name', 'score', 'in_car_score', 'out_car_score', 'ai_suggestion', 'start_time', 'end_time',
            'personnel', 'group', 'device', 'aivisionlog_set', 'videorecord_set', 'total_mileage'
        ]

class InvitationCodeSerializer(serializers.ModelSerializer):
    """唯讀序列化器，用於顯示已生成的邀請碼資訊。"""
    class Meta:
        model = InvitationCode
        fields = ['code', 'expires_at', 'group']
        read_only_fields = fields

class GroupAnnouncementSerializer(serializers.ModelSerializer):
    """序列化群組公告，部分欄位為唯讀。"""
    publisher = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = GroupAnnouncement
        fields = ['id', 'announcement_number', 'content', 'publish_date', 'is_active', 'publisher', 'group']
        read_only_fields = ['publisher', 'group', 'announcement_number']

class VehicleDeviceSerializer(serializers.ModelSerializer):
    """序列化「車機設備」。"""
    class Meta:
        model = VehicleDevice
        fields = '__all__'

# =============================================================================
# 2. 寫入專用序列化器 (For Data Writing & Creation)
# =============================================================================

class UserRegisterSerializer(serializers.ModelSerializer):
    """處理使用者註冊請求，支援扁平化的 Profile 欄位、頭像上傳和邀請碼。"""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    personnel_number = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    license_type = serializers.CharField(write_only=True, required=False, allow_blank=True)
    driving_experience = serializers.IntegerField(write_only=True, required=False, default=0)
    avatar = serializers.ImageField(write_only=True, required=False)
    invitation_code = serializers.CharField(write_only=True, required=False, allow_blank=True, max_length=8)

    class Meta:
        model = User
        fields = [
            'username', 'password', 'email', 'first_name', 'last_name', 
            'personnel_number', 'phone', 'license_type', 'driving_experience', 'avatar',
            'invitation_code'
        ]

    @transaction.atomic
    def create(self, validated_data):
        """覆寫 create 方法，以在同一個事務中同時建立 User 和 PersonnelProfile。"""
        profile_data = {
            'personnel_number': validated_data.pop('personnel_number'),
            'phone': validated_data.pop('phone', ''),
            'license_type': validated_data.pop('license_type', ''),
            'driving_experience': validated_data.pop('driving_experience', 0),
            'avatar': validated_data.pop('avatar', None)
        }
        invitation_code = validated_data.pop('invitation_code', None)
        user = User.objects.create_user(**validated_data)
        PersonnelProfile.objects.create(user=user, **profile_data)
        if invitation_code:
            try:
                invite = InvitationCode.objects.get(code=invitation_code.upper(), is_used=False, expires_at__gt=timezone.now())
                GroupMember.objects.create(group=invite.group, user=user)
                invite.is_used = True
                invite.save()
            except InvitationCode.DoesNotExist:
                pass 
        return user

class TripStartSerializer(serializers.ModelSerializer):
    """(車機用) 建立一趟新行程的序列化器。"""
    device = serializers.PrimaryKeyRelatedField(queryset=VehicleDevice.objects.all())
    personnel = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    class Meta:
        model = Trip
        fields = ['id', 'trip_number', 'name', 'group', 'device', 'personnel', 'start_time']

class TripEndSerializer(serializers.ModelSerializer):
    """(車機用) 結束一趟行程的序列化器。"""
    class Meta:
        model = Trip
        fields = ['end_time', 'total_mileage'] # 允許車機回報總里程

class AiVisionLogCreateSerializer(serializers.ModelSerializer):
    """(車機用) 新增一筆 AI 視覺事件紀錄的序列化器。"""
    trip = serializers.PrimaryKeyRelatedField(queryset=Trip.objects.all())
    event = serializers.PrimaryKeyRelatedField(queryset=ScoringStandard.objects.all())
    class Meta:
        model = AiVisionLog
        fields = ['trip', 'event', 'timestamp', 'event_details', 'confidence_score']

class VideoRegisterSerializer(serializers.ModelSerializer):
    """(車機用) 註冊一筆已上傳至雲端的影片。"""
    trip = serializers.PrimaryKeyRelatedField(queryset=Trip.objects.all())
    class Meta:
        model = VideoRecord
        fields = ['trip', 'video_url', 'start_time', 'end_time', 'location', 'file_size']

class TripSuggestionFeedbackSerializer(serializers.ModelSerializer):
    """(前端用) 新增一筆對 AI 行程建議的回饋。"""
    class Meta:
        model = TripSuggestionFeedback
        fields = ['trip', 'feedback_type', 'comment']