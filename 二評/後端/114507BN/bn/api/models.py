# api/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.conf import settings
import datetime
import secrets
from django.utils import timezone
from datetime import timedelta

# =============================================================================
# 1. 人員與群組管理 (User & Group Management)
# =============================================================================

class PersonnelProfile(models.Model):
    GENDER_CHOICES = [('MALE', '男'), ('FEMALE', '女'), ('UNSPECIFIED', '不願透漏')]
    
    # 【註解】原有的 RegexValidator 已被移除，因為駕照號碼可能不再是必填或唯一
    # license_validator = RegexValidator(regex=r'^[A-Z]\d{9}$', message='駕照號碼格式必須為：1位英文大寫字母 + 9位數字。')

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name="使用者帳號")
    personnel_number = models.CharField(max_length=50, unique=True, verbose_name="人員編號")
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='UNSPECIFIED', verbose_name="性別")
    
    # 【修改】放寬駕照號碼的限制，使其非唯一且可為空
    license_number = models.CharField(max_length=20, blank=True, verbose_name="駕照號碼")
    
    # --- 【以下為根據前端需求新增的欄位】 ---

    # 【新增】用於儲存使用者頭像
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="個人頭像")

    # 【新增】用於儲存聯絡電話
    phone = models.CharField(max_length=20, blank=True, verbose_name="聯絡電話")

    # 【新增】用於儲存駕照等級
    license_type = models.CharField(max_length=50, blank=True, verbose_name="駕照等級")

    # 【新增】用於儲存駕駛年資
    driving_experience = models.PositiveIntegerField(default=0, verbose_name="駕駛年資")
    
    class Meta:
        db_table = 'personnel_profile' 
        verbose_name = "人員詳細資料"
        verbose_name_plural = "1. 人員詳細資料"
    def __str__(self): return self.user.username

# ... (Group 和 GroupMember 模型維持不變) ...
class Group(models.Model):
    id = models.BigAutoField(primary_key=True)
    group_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 【新增】記錄群組的建立者，用於權限判斷
    # on_delete=models.SET_NULL: 如果建立者帳號被刪除，這個欄位會設為 NULL，群組不會被跟著刪除
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='owned_groups'
    )
    
    # 【新增】透過 GroupMember 中介模型建立多對多關聯
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='GroupMember',
        related_name='joined_groups'
    )


    class Meta:
        db_table = 'group'
        verbose_name = "群組"
        verbose_name_plural = "2. 群組管理"
    def __str__(self): return self.name

class GroupMember(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    ROLE_CHOICES = [
        ('MEMBER', '成員'),
        ('ADMIN', '管理員'),
    ]
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='MEMBER',
        verbose_name="群組角色"
    )
    
    class Meta:
        db_table = 'group_member'
        unique_together = (('group', 'user'),)
        verbose_name = "群組成員"
        verbose_name_plural = "3. 群組成員"


# ... (SystemAnnouncement, GroupAnnouncement, VehicleDevice 模型維持不變) ...
class SystemAnnouncement(models.Model):
    id = models.BigAutoField(primary_key=True)
    announcement_number = models.CharField(max_length=50, unique=True)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = 'system_announcement'
        verbose_name = "系統公告"
        verbose_name_plural = "4. 系統公告"
        
class GroupAnnouncement(models.Model):
    id = models.BigAutoField(primary_key=True)
    announcement_number = models.CharField(max_length=50, unique=True, blank=True) 
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    publisher = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    publish_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.announcement_number:
            # 如果這是一則新公告 (沒有編號)，就自動生成一個
            # 格式：ANN-{群組ID}-{8位隨機碼}
            self.announcement_number = f"ANN-{self.group.id}-{secrets.token_hex(4).upper()}"
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'group_announcement'
        verbose_name = "群組公告"
        verbose_name_plural = "5. 群組公告"

class VehicleDevice(models.Model):
    id = models.BigAutoField(primary_key=True)
    device_number = models.CharField(max_length=50, unique=True)
    vehicle_type = models.CharField(max_length=20)
    activation_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'vehicle_device'
        verbose_name = "車機設備"
        verbose_name_plural = "6. 車機設備管理"

# =============================================================================
# 2. ... 行程管理 (Trip Management) ...
# =============================================================================

class Trip(models.Model):
    id = models.BigAutoField(primary_key=True)
    trip_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    device = models.ForeignKey(VehicleDevice, on_delete=models.CASCADE)
    personnel = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    ai_suggestion = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # 【新增】建議性欄位，用於儲存計算好的總里程以優化效能
    total_mileage = models.FloatField(blank=True, null=True, verbose_name="總里程(KM)")

    class Meta:
        db_table = 'trip'
        verbose_name = "行程"
        verbose_name_plural = "7. 行程管理"

# ... (RouteLog, ScoringStandard, AiVisionLog, VideoRecord 模型維持不變) ...
class RouteLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='route_logs')
    timestamp = models.DateTimeField()
    location = models.CharField(max_length=100)
    speed = models.FloatField(blank=True, null=True)
    class Meta:
        db_table = 'route_log'
        verbose_name = "路程紀錄"
        verbose_name_plural = "8. 路程紀錄"

class ScoringStandard(models.Model):
    id = models.AutoField(primary_key=True)
    event_number = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255)
    deduction_points = models.IntegerField()
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = 'scoring_standard'
        verbose_name = "評分標準"
        verbose_name_plural = "9. 評分標準"

class AiVisionLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='aivisionlog_set')
    event = models.ForeignKey(ScoringStandard, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    event_details = models.CharField(max_length=255)
    confidence_score = models.FloatField(blank=True, null=True)
    class Meta:
        db_table = 'ai_vision_log'
        verbose_name = "AI視覺事件紀錄"
        verbose_name_plural = "10. AI視覺事件紀錄"

class VideoRecord(models.Model):
    id = models.BigAutoField(primary_key=True)
    video_number = models.CharField(max_length=50, unique=True)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='videorecord_set')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=500)
    file_size = models.BigIntegerField(blank=True, null=True)
    class Meta:
        db_table = 'video_record'
        verbose_name = "影像紀錄"
        verbose_name_plural = "11. 影像紀錄"

class InvitationCode(models.Model):
    code = models.CharField(max_length=8, unique=True, verbose_name="邀請碼")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name="所屬群組")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="建立者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    expires_at = models.DateTimeField(verbose_name="過期時間")
    is_used = models.BooleanField(default=False, verbose_name="是否已使用")

    def save(self, *args, **kwargs):
        if not self.pk: # 只在第一次建立時執行
            self.code = secrets.token_hex(4).upper() # 生成一個8位數的隨機碼
            self.expires_at = timezone.now() + timedelta(days=1) # 設定 24 小時後過期
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.group.name} 的邀請碼: {self.code}"

    class Meta:
        verbose_name = "群組邀請碼"
        verbose_name_plural = "12. 群組邀請碼"