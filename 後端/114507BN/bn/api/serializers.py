# api/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Avg
from google.cloud import storage
from datetime import timedelta
from urllib.parse import urlparse
from django.utils import timezone 
from .models import (
    PersonnelProfile, Group, Trip, ScoringStandard,
    AiVisionLog, VideoRecord, VehicleDevice, GroupAnnouncement,
    InvitationCode, GroupMember, TripSuggestionFeedback,
    ActivationCode , SystemAnnouncement,
)

# =============================================================================
# 區塊 1：唯讀與巢狀序列化器 (For Data Reading & Nesting)
# =============================================================================

class PersonnelProfileSerializer(serializers.ModelSerializer):
    """【最終修正版】序列化人員詳細資料，並手動產生完整的頭像 URL。"""
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = PersonnelProfile
        fields = ['personnel_number', 'gender', 'license_number', 'avatar', 'phone', 'license_type', 'driving_experience', 'nfc_card_id']

    def get_avatar(self, obj):
        request = self.context.get('request')
        if request and obj.avatar and hasattr(obj.avatar, 'url'):
            return request.build_absolute_uri(obj.avatar.url)
        return None

class UserSerializer(serializers.ModelSerializer):
    """
    【最新修正版】
    序列化使用者核心資料，並正確處理巢狀 Profile 的讀取與更新，
    同時提供前端需要的權限相關欄位。
    """
    # 讀取時，使用 PersonnelProfileSerializer 來巢狀顯示詳細資料 (唯讀)
    personnelprofile = PersonnelProfileSerializer(read_only=True)
    
    # 新增以下三個欄位，用來告訴前端使用者的權限 
    is_group_admin = serializers.SerializerMethodField()
    administered_groups = serializers.SerializerMethodField()
    group_memberships = serializers.SerializerMethodField() # <-- 問題的關鍵！
    
    # 專門用於接收變更密碼時的新密碼
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

    # 為了讓更新 (PATCH) 時能接收扁平化的 FormData
    personnel_number = serializers.CharField(source='personnelprofile.personnel_number', write_only=True, required=False, allow_blank=True)
    gender = serializers.CharField(source='personnelprofile.gender', write_only=True, required=False)
    license_number = serializers.CharField(source='personnelprofile.license_number', write_only=True, required=False, allow_blank=True)
    avatar = serializers.ImageField(source='personnelprofile.avatar', write_only=True, required=False, allow_null=True)
    phone = serializers.CharField(source='personnelprofile.phone', write_only=True, required=False, allow_blank=True)
    license_type = serializers.CharField(source='personnelprofile.license_type', write_only=True, required=False, allow_blank=True)
    driving_experience = serializers.IntegerField(source='personnelprofile.driving_experience', write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            # 讀取用的欄位
            'id', 'username', 'last_login', 'first_name', 'last_name', 'email', 
            'is_staff', 
            'is_group_admin', 'administered_groups', 'group_memberships', # <-- 加入到 fields
            'personnelprofile',
            # 寫入用的欄位
            'password', 'personnel_number', 'gender', 'license_number', 'avatar', 'phone', 
            'license_type', 'driving_experience'
        ]
        read_only_fields = [
            'id', 'username', 'last_login', 'is_staff', 
            'is_group_admin', 'administered_groups', 'group_memberships', # <-- 加入到 read_only_fields
            'personnelprofile'
        ]

    def get_is_group_admin(self, obj):
        """檢查使用者是否為任何群組的管理員。"""
        return GroupMember.objects.filter(user=obj, role='ADMIN').exists()
    
    def get_administered_groups(self, obj):
        """獲取使用者被指派為管理員的所有群組 ID 列表。"""
        admin_memberships = GroupMember.objects.filter(user=obj, role='ADMIN')
        return [membership.group.id for membership in admin_memberships]

    def get_group_memberships(self, obj):
        """獲取使用者所有的群組成員身份 (群組ID 和 角色)。"""
        memberships = GroupMember.objects.filter(user=obj)
        return [{'group_id': m.group.id, 'role': m.role} for m in memberships]

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        覆寫 update 方法，以支援密碼、個人資料、Profile 的巢狀更新。
        """
        # --- 處理密碼更新 ---
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
            instance.save()

        # --- 處理 Profile 更新 ---
        profile_data = validated_data.pop('personnelprofile', {})
        
        # --- 處理 User 其他欄位更新 ---
        instance = super().update(instance, validated_data)

        if profile_data:
            profile = instance.personnelprofile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
            
        return instance
    
class GroupMemberSerializer(serializers.ModelSerializer):
    """【最終修正版】序列化群組成員資料，明確包含角色和加入日期。"""
    average_score = serializers.FloatField(read_only=True, default=0)
    personnelprofile = PersonnelProfileSerializer(read_only=True)
    
    role = serializers.SerializerMethodField()
    joined_at = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'average_score', 'role', 'personnelprofile', 'joined_at']

    def get_role(self, obj):
        """從傳入的 context 中獲取群組 ID，並查詢該使用者在此群組的角色。"""
        group_id = self.context.get('group_id')
        if not group_id:
            first_membership = obj.groupmember_set.first()
            return first_membership.role if first_membership else 'MEMBER'
        try:
            membership = GroupMember.objects.get(user=obj, group__id=group_id)
            return membership.role
        except GroupMember.DoesNotExist:
            return 'UNKNOWN'

    def get_joined_at(self, obj):
        """查詢這位使用者是在何時加入這個群組的。"""
        group_id = self.context.get('group_id')
        if not group_id:
            return None
        try:
            membership = GroupMember.objects.get(user=obj, group__id=group_id)
            return membership.joined_at
        except GroupMember.DoesNotExist:
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
    """序列化影像紀錄的文字資訊，並動態生成有時效性的 GCS 簽署後 URL。"""
    
    # 將 video_url 改為 SerializerMethodField
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = VideoRecord
        # 確保 video_url 和 file_size 都在 fields 中
        fields = ['video_number', 'start_time', 'end_time', 'location', 'video_url', 'file_size']

    def get_video_url(self, obj):
        """
        將 GCS URI (gs://bucket/object) 轉換為有時效性的 HTTPS URL。
        """
        gcs_uri = obj.video_url
        if not gcs_uri or not gcs_uri.startswith('gs://'):
            # 如果 URL 無效或不是 GCS URI，則直接返回 None
            return None

        try:
            # 初始化 GCS 客戶端 (它會自動讀取您設定的環境變數)
            storage_client = storage.Client()
            
            # 解析 GCS URI
            parsed_uri = urlparse(gcs_uri)
            bucket_name = parsed_uri.netloc
            object_name = parsed_uri.path.lstrip('/')

            # 獲取 bucket 和 blob (檔案) 物件
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(object_name)

            # 生成一個 15 分鐘後過期的簽署後 URL
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=15),
                method="GET",
            )
            return signed_url
            
        except Exception as e:
            # 如果出錯，在後端日誌中印出錯誤，並回傳 None
            print(f"Error generating signed URL for {gcs_uri}: {e}")
            return None

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
    """【讀取用】唯讀序列化器，用於顯示已生成的邀請碼資訊。"""
    group = serializers.StringRelatedField() # 顯示群組名稱而非 ID
    created_by = serializers.StringRelatedField() # 顯示建立者名稱而非 ID

    class Meta:
        model = InvitationCode
        # 我們新增了 'name' 欄位來對應前端的「邀請名稱」
        fields = ['id', 'name', 'code', 'expires_at', 'is_used', 'group', 'created_by']
        read_only_fields = fields

class InvitationCodeCreateSerializer(serializers.ModelSerializer):
    """【建立用】寫入專用序列化器，用於建立新的邀請碼。"""
    class Meta:
        model = InvitationCode
        # 前端只需要提供 'name' 和 'expires_at'
        # 'group' 和 'created_by' 將由 view 自動填入
        fields = ['name', 'expires_at']
        
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
    【最新版】處理使用者註冊，支援可多次使用的啟用碼。
    """
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
        【最新版】自訂驗證邏輯：
        1. 檢查 code 是否存在
        2. 檢查 code 是否已達到使用次數上限
        3. 檢查 code 是否已過期
        """
        try:
            code = ActivationCode.objects.get(code=value)
            if code.current_uses >= code.max_uses:
                raise serializers.ValidationError("此啟用碼已達到使用次數上限。")
            if code.expires_at and code.expires_at < timezone.now():
                raise serializers.ValidationError("此啟用碼已過期。")
            return value
        except ActivationCode.DoesNotExist:
            raise serializers.ValidationError("無效的啟用碼。")

    @transaction.atomic
    def create(self, validated_data):
        """
        【最新版】覆寫 create 方法，將 ActivationCode 的使用次數 +1。
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
        
        # 將啟用碼的使用次數 +1
        try:
            activation_code_obj = ActivationCode.objects.get(code=activation_code_str)
            activation_code_obj.current_uses += 1
            activation_code_obj.save()
        except ActivationCode.DoesNotExist:
            pass

        # 處理群組邀請碼 (邏輯不變)
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
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), required=False, allow_null=True)
    name = serializers.CharField(max_length=200, required=False, allow_null=True)

    class Meta:
        model = Trip
        # --- 將修改後的 name 欄位加回 fields 中 ---
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

class SystemAnnouncementSerializer(serializers.ModelSerializer):
    """序列化系統公告。"""
    class Meta:
        model = SystemAnnouncement
        fields = ['id', 'announcement_number', 'content', 'date', 'is_active']
