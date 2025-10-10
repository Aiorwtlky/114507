# api/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Avg
from django.utils import timezone 
from .models import (
    PersonnelProfile, Group, Trip, ScoringStandard,
    AiVisionLog, VideoRecord, VehicleDevice, GroupAnnouncement,
    InvitationCode, GroupMember, TripSuggestionFeedback,
    ActivationCode
)

# =============================================================================
# 區塊 1：唯讀與巢狀序列化器 (For Data Reading & Nesting)
# 這些 Serializer 主要用於 GET 請求，提供豐富且適合前端展示的資料結構。
# =============================================================================

class PersonnelProfileSerializer(serializers.ModelSerializer):
    """序列化人員詳細資料 (PersonnelProfile)，並處理頭像的完整 URL。"""
    # 讓 avatar 欄位在更新時也能被接收，但非必填
    avatar = serializers.ImageField(required=False, allow_null=True) 
    
    class Meta:
        model = PersonnelProfile
        fields = ['personnel_number', 'gender', 'license_number', 'avatar', 'phone', 'license_type', 'driving_experience']

    def get_avatar(self, obj):
        """
        覆寫 avatar 欄位的輸出，將相對路徑轉換為前端可直接使用的絕對 URL。
        """
        request = self.context.get('request')
        # 檢查 obj.avatar 是否存在且有 url 屬性
        if obj.avatar and hasattr(obj.avatar, 'url'):
            return request.build_absolute_uri(obj.avatar.url)
        return None

class UserSerializer(serializers.ModelSerializer):
    """
    序列化使用者核心資料 (User)，並巢狀包含 Profile。
    【已強化】此 Serializer 同時支援個人資料的讀取與巢狀更新。
    """
    # 直接將 PersonnelProfileSerializer 作為巢狀欄位。
    # DRF 會自動處理讀取時的巢狀序列化。更新邏輯則由下面的 update 方法處理。
    personnelprofile = PersonnelProfileSerializer()
    
    # 使用 SerializerMethodField 產生一些計算後的唯讀欄位
    is_group_leader = serializers.SerializerMethodField()
    administered_groups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'last_login', 'first_name', 'last_name', 'email', 
            'is_staff', 'is_group_leader', 'administered_groups', 'personnelprofile'
        ]
        # 確保在讀取 Profile 時，這些核心欄位是唯讀的
        read_only_fields = ['id', 'username', 'last_login', 'is_staff', 'is_group_leader', 'administered_groups']

    def get_is_group_leader(self, obj):
        """檢查使用者是否為任何群組的建立者。"""
        return Group.objects.filter(created_by=obj).exists()
    
    def get_administered_groups(self, obj):
        """獲取使用者被指派為管理員的所有群組 ID 列表。"""
        admin_memberships = GroupMember.objects.filter(user=obj, role='ADMIN')
        return [membership.group.id for membership in admin_memberships]

    @transaction.atomic
    def update(self, instance, validated_data):
        # 【微調】從 validated_data 中手動分離出 profile 的欄位
        profile_fields = ['personnel_number', 'gender', 'license_number', 'avatar', 'phone', 'license_type', 'driving_experience']
        profile_data = {}
        for field in profile_fields:
            if field in validated_data:
                profile_data[field] = validated_data.pop(field)

        # 更新 Profile 物件
        if profile_data:
            profile = instance.personnelprofile
            profile_serializer = PersonnelProfileSerializer(instance=profile, data=profile_data, partial=True, context=self.context)
            if profile_serializer.is_valid(raise_exception=True):
                profile_serializer.save()

        # 更新 User 物件
        instance = super().update(instance, validated_data)
        return instance

class GroupMemberSerializer(serializers.ModelSerializer):
    """序列化群組成員資料，包含其在特定群組的角色與 Profile。"""
    average_score = serializers.FloatField(read_only=True, default=0)
    role = serializers.SerializerMethodField()
    personnelprofile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'average_score', 'role', 'personnelprofile']

    def get_role(self, obj):
        """根據從 View 傳入的 context 中的 group_id，查詢使用者在該群組中的角色。"""
        group_id = self.context.get('group_id')
        if not group_id: return 'MEMBER'
        try:
            membership = GroupMember.objects.get(user=obj, group__id=group_id)
            return membership.role
        except GroupMember.DoesNotExist:
            return 'MEMBER' # 如果出錯，預設為一般成員

    def get_personnelprofile(self, obj):
        """手動序列化 Profile，確保 request context 被正確傳遞以生成頭像 URL。"""
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
    """序列化行程列表，用於顯示簡化的行程資訊，提高 API 效能。"""
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
# 區塊 2：寫入專用序列化器 (For Data Writing & Creation)
# 這些 Serializer 主要用於 POST, PUT, PATCH 請求，處理資料的建立與更新。
# =============================================================================

class UserRegisterSerializer(serializers.ModelSerializer):
    """
    【僅限建立】處理使用者註冊請求，支援扁平化的 Profile 欄位、頭像上傳、邀請碼與啟用碼。
    """
    # write_only=True 確保這些欄位只在接收請求時有效，不會在回應中洩漏
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    personnel_number = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    license_type = serializers.CharField(write_only=True, required=False, allow_blank=True)
    driving_experience = serializers.IntegerField(write_only=True, required=False, default=0)
    avatar = serializers.ImageField(write_only=True, required=False)
    invitation_code = serializers.CharField(write_only=True, required=False, allow_blank=True, max_length=8)
    gender = serializers.CharField(write_only=True, required=False, allow_blank=True)
    license_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    activation_code = serializers.CharField(write_only=True, required=True, label="MDG Pro 啟用碼")

    class Meta:
        model = User
        fields = [
            'username', 'password', 'email', 'first_name', 'last_name', 
            'personnel_number', 'phone', 'license_type', 'driving_experience', 'avatar',
            'invitation_code', 'gender', 'license_number', 'activation_code'
        ]

    def validate_activation_code(self, value):
        """
        自訂驗證邏輯：在儲存前檢查啟用碼的有效性。
        1. 檢查 code 是否存在
        2. 檢查 code 是否已被使用 (is_used=False)
        3. 檢查 code 是否已過期
        """
        try:
            code = ActivationCode.objects.get(code=value, is_used=False)
            if code.expires_at and code.expires_at < timezone.now():
                raise serializers.ValidationError("此啟用碼已過期。")
            return value
        except ActivationCode.DoesNotExist:
            raise serializers.ValidationError("無效的啟用碼或已被使用。")

    @transaction.atomic
    def create(self, validated_data):
        """
        覆寫 create 方法，以在同一個資料庫事務中完成以下操作：
        1. 從驗證資料中分離出 User 和 Profile 的欄位。
        2. 建立 User 實例。
        3. 建立與之關聯的 PersonnelProfile 實例。
        4. 將使用的 ActivationCode 標記為已使用。
        5. (可選) 處理群組邀請碼。
        """
        activation_code_str = validated_data.pop('activation_code')
        profile_data = {
            'personnel_number': validated_data.pop('personnel_number'),
            'phone': validated_data.pop('phone', ''),
            'license_type': validated_data.pop('license_type', ''),
            'driving_experience': validated_data.pop('driving_experience', 0),
            'avatar': validated_data.pop('avatar', None),
            'gender': validated_data.pop('gender', 'UNSPECIFIED'),
            'license_number': validated_data.pop('license_number', ''),
        }
        invitation_code = validated_data.pop('invitation_code', None)
        
        user = User.objects.create_user(**validated_data)
        PersonnelProfile.objects.create(user=user, **profile_data)
        
        # 標記啟用碼為已使用
        try:
            activation_code_obj = ActivationCode.objects.get(code=activation_code_str)
            activation_code_obj.is_used = True
            activation_code_obj.used_by = user
            activation_code_obj.used_at = timezone.now()
            activation_code_obj.save()
        except ActivationCode.DoesNotExist:
            # 此處應不會觸發，因為 validate 方法已先檢查過。作為防呆。
            pass

        # 處理群組邀請碼
        if invitation_code:
            try:
                invite = InvitationCode.objects.get(code=invitation_code.upper(), is_used=False, expires_at__gt=timezone.now())
                GroupMember.objects.create(group=invite.group, user=user)
                invite.is_used = True
                invite.save()
            except InvitationCode.DoesNotExist:
                # 若邀請碼無效，靜默失敗，不影響主註冊流程
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
        fields = ['end_time', 'total_mileage']

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