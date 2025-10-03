# api/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Avg
from django.utils import timezone 
from .models import (
    PersonnelProfile, Group, Trip, ScoringStandard,
    AiVisionLog, VideoRecord, VehicleDevice, GroupAnnouncement,
    InvitationCode, GroupMember
)

# =============================================================================
# 基礎模型序列化器 (用於資料讀取與巢狀顯示)
# =============================================================================

class PersonnelProfileSerializer(serializers.ModelSerializer):
    """
    序列化「人員詳細資料」，特別處理頭像 avatar 欄位，使其回傳完整的 URL。
    """
    # 【關鍵修正 A】將 avatar 改為 SerializerMethodField，以便自訂其輸出格式。
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = PersonnelProfile
        # 欄位列表中包含我們自訂的 avatar。
        fields = ['personnel_number', 'gender', 'license_number', 'avatar', 'phone', 'license_type', 'driving_experience']

    def get_avatar(self, obj):
        """
        自訂取得 avatar 欄位值的方法。
        - obj: PersonnelProfile 的實例。
        """
        # 從 context 中獲取當前的 request 物件，這對於建立絕對 URL 至關重要。
        request = self.context.get('request')
        # 檢查 obj.avatar 是否存在且有 url 屬性。
        if obj.avatar and hasattr(obj.avatar, 'url'):
            # 使用 request.build_absolute_uri 將相對路徑 (/media/avatars/...)
            # 轉換為絕對 URL (http://127.0.0.1:8000/media/avatars/...)。
            return request.build_absolute_uri(obj.avatar.url)
        # 如果使用者沒有上傳頭像，則回傳 null。
        return None

class UserSerializer(serializers.ModelSerializer):
    """
    序列化「使用者」基本資料，並巢狀包含其詳細資料 (PersonnelProfile)。
    同時動態計算 'is_group_leader' 和 'administered_groups' 兩個欄位。
    """
    # 【關鍵修正 B】將 personnelprofile 從直接宣告改為 SerializerMethodField。
    # 這樣可以確保我們在序列化 Profile 時，能手動傳遞 'request' context，解決圖片 URL 的問題。
    personnelprofile = serializers.SerializerMethodField()
    
    is_group_leader = serializers.SerializerMethodField()
    administered_groups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_group_leader', 'personnelprofile', 'administered_groups']

    def get_is_group_leader(self, obj):
        """判斷 obj (使用者) 是否為任何群組的 created_by。"""
        return Group.objects.filter(created_by=obj).exists()
    
    def get_administered_groups(self, obj):
        """找出 obj (使用者) 是管理員 (role='ADMIN') 的所有群組 ID。"""
        admin_memberships = GroupMember.objects.filter(user=obj, role='ADMIN')
        return [membership.group.id for membership in admin_memberships]

    def get_personnelprofile(self, obj):
        """
        自訂取得 personnelprofile 的方法。
        - obj: User 的實例。
        """
        try:
            # 取得關聯的 profile 物件
            profile = obj.personnelprofile
            # 從父層的 context 中獲取 request 物件
            request = self.context.get('request')
            # 實例化 PersonnelProfileSerializer，並手動傳入 context
            # 這樣 PersonnelProfileSerializer 內部的 get_avatar 才能建立絕對 URL
            return PersonnelProfileSerializer(profile, context={'request': request}).data
        except PersonnelProfile.DoesNotExist:
            return None

class GroupMemberSerializer(serializers.ModelSerializer):
    """
    【最終修正版】
    序列化「群組成員」資料，現在會一併回傳包含完整 URL 的頭像等 profile 資訊。
    """
    average_score = serializers.FloatField(read_only=True, default=0)
    role = serializers.SerializerMethodField()
    # 【新增】personnelprofile 欄位，用來獲取頭像等詳細資訊
    personnelprofile = serializers.SerializerMethodField()

    class Meta:
        model = User
        # 【修改】在 fields 中加入 'personnelprofile'
        fields = ['id', 'username', 'first_name', 'last_name', 'average_score', 'role', 'personnelprofile']

    def get_role(self, obj):
        """根據 context 中的 group_id，查詢使用者在該群組中的角色。"""
        group_id = self.context.get('group_id')
        if not group_id:
            return 'MEMBER'
        try:
            membership = GroupMember.objects.get(user=obj, group__id=group_id)
            return membership.role
        except GroupMember.DoesNotExist:
            return 'MEMBER'

    def get_personnelprofile(self, obj):
        """
        【新增】手動序列化 Profile 的方法。
        確保 request context 能被傳遞，以便 PersonnelProfileSerializer 產生頭像的完整 URL。
        """
        try:
            profile = obj.personnelprofile
            request = self.context.get('request')
            # 呼叫 PersonnelProfileSerializer 並傳入 request，這是產生完整 URL 的關鍵
            return PersonnelProfileSerializer(profile, context={'request': request}).data
        except PersonnelProfile.DoesNotExist:
            # 如果使用者沒有 Profile，回傳 null
            return None

class GroupSerializer(serializers.ModelSerializer):
    """序列化「群組」的基本資料。"""
    # 將 created_by (ForeignKey) 顯示為其 username 字串。
    created_by = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Group
        fields = ['id', 'group_number', 'name', 'description', 'created_by', 'created_at']

class InvitationCodeSerializer(serializers.ModelSerializer):
    """唯讀序列化器，用於在前端顯示已生成的「邀請碼」資訊。"""
    class Meta:
        model = InvitationCode
        fields = ['code', 'expires_at', 'group']
        read_only_fields = fields

class GroupAnnouncementSerializer(serializers.ModelSerializer):
    """序列化「群組公告」。"""
    publisher = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = GroupAnnouncement
        fields = ['id', 'announcement_number', 'content', 'publish_date', 'is_active', 'publisher', 'group']
        # 'publisher' 和 'group' 在建立時由 View 自動設定，因此設為唯讀。
        read_only_fields = ['publisher', 'group']

class VehicleDeviceSerializer(serializers.ModelSerializer):
    """序列化「車機設備」。"""
    class Meta:
        model = VehicleDevice
        fields = '__all__'

# =============================================================================
# 行程相關序列化器 (用於巢狀顯示行程詳情)
# =============================================================================

class ScoringStandardSerializer(serializers.ModelSerializer):
    """序列化「評分標準」(也就是事件類型)。"""
    class Meta:
        model = ScoringStandard
        fields = ['event_number', 'description', 'deduction_points']

class AiVisionLogSerializer(serializers.ModelSerializer):
    """序列化「AI 視覺事件紀錄」，並巢狀包含事件類型。"""
    event = ScoringStandardSerializer(read_only=True)
    class Meta:
        model = AiVisionLog
        fields = ['timestamp', 'event_details', 'confidence_score', 'event']

class VideoRecordSerializer(serializers.ModelSerializer):
    """序列化「影像紀錄」。"""
    class Meta:
        model = VideoRecord
        fields = ['video_number', 'start_time', 'end_time', 'location']

class TripListSerializer(serializers.ModelSerializer):
    """序列化「行程列表」，用於顯示簡化的行程資訊。"""
    personnel = serializers.StringRelatedField()
    group = serializers.StringRelatedField()
    device = serializers.StringRelatedField()
    class Meta:
        model = Trip
        fields = ['id', 'trip_number', 'name', 'score', 'start_time', 'end_time', 'personnel', 'group', 'device', 'total_mileage']

class TripDetailSerializer(serializers.ModelSerializer):
    """序列化單一「行程的完整詳情」，包含所有相關的巢狀資料。"""
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

# =============================================================================
# 資料建立/更新專用序列化器 (Write-Only)
# =============================================================================

class UserRegisterSerializer(serializers.ModelSerializer):
    """
    處理使用者註冊請求，支援頭像上傳和邀請碼。
    使用「扁平化」欄位設計以簡化檔案上傳的處理。
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    # 從 PersonnelProfile 模型來的欄位，全部設為 write_only。
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
        """
        覆寫 create 方法，以在同一個請求中同時建立 User 和 PersonnelProfile。
        """
        # 將屬於 Profile 的資料從 validated_data 中分離出來。
        profile_data = {
            'personnel_number': validated_data.pop('personnel_number'),
            'phone': validated_data.pop('phone', ''),
            'license_type': validated_data.pop('license_type', ''),
            'driving_experience': validated_data.pop('driving_experience', 0),
            'avatar': validated_data.pop('avatar', None)
        }
        invitation_code = validated_data.pop('invitation_code', None)

        # 剩下的 validated_data 只包含 User 模型的欄位，可以直接用來建立 User。
        user = User.objects.create_user(**validated_data)
        
        # 建立與 User 關聯的 PersonnelProfile。
        PersonnelProfile.objects.create(user=user, **profile_data)

        # 處理邀請碼的邏輯。
        if invitation_code:
            try:
                invite = InvitationCode.objects.get(
                    code=invitation_code.upper(), is_used=False, expires_at__gt=timezone.now()
                )
                GroupMember.objects.create(group=invite.group, user=user)
                invite.is_used = True
                invite.save()
            except InvitationCode.DoesNotExist:
                print(f"警告：使用者 {user.username} 提供了無效的邀請碼 '{invitation_code}'")
                pass
                
        return user

# --- (以下為車機上傳資料用的序列化器，通常不需要修改) ---

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
    trip = serializers.PrimaryKeyRelatedField(queryset=Trip.objects.all())
    class Meta:
        model = VideoRecord
        fields = ['video_number', 'trip', 'start_time', 'end_time', 'location', 'file_size']

