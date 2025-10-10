# api/models.py

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
import secrets
from datetime import timedelta

# =============================================================================
# 1. 人員與權限管理 (User & Permission Management)
# =============================================================================

class PersonnelProfile(models.Model):
    """人員詳細資料，一對一擴充 Django 內建的 User 模型。"""
    GENDER_CHOICES = [('MALE', '男'), ('FEMALE', '女'), ('UNSPECIFIED', '不願透漏')]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name="使用者帳號")
    personnel_number = models.CharField(max_length=50, unique=True, verbose_name="人員編號")
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='UNSPECIFIED', verbose_name="性別")
    license_number = models.CharField(max_length=20, blank=True, verbose_name="駕照號碼")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="個人頭像")
    phone = models.CharField(max_length=20, blank=True, verbose_name="聯絡電話")
    license_type = models.CharField(max_length=50, blank=True, verbose_name="駕照等級")
    driving_experience = models.PositiveIntegerField(default=0, verbose_name="駕駛年資")
    nfc_card_id = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="NFC 卡片識別碼")

    class Meta:
        db_table = 'personnel_profile' 
        verbose_name = "人員詳細資料"
        verbose_name_plural = "1. 人員詳細資料" # Admin 後台顯示名稱
    def __str__(self): return self.user.username

class Group(models.Model):
    """群組模型，用於組織使用者。"""
    id = models.BigAutoField(primary_key=True)
    group_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='owned_groups')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='GroupMember', related_name='joined_groups')

    class Meta:
        db_table = 'group'
        verbose_name = "群組"
        verbose_name_plural = "2. 群組管理"
    def __str__(self): return self.name

class GroupMember(models.Model):
    """群組與使用者之間的多對多中介模型，用於定義角色。"""
    ROLE_CHOICES = [('MEMBER', '成員'), ('ADMIN', '管理員')]
    
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='MEMBER', verbose_name="群組角色")
    
    class Meta:
        db_table = 'group_member'
        unique_together = (('group', 'user'),)
        verbose_name = "群組成員"
        verbose_name_plural = "3. 群組成員"

class ActivationCode(models.Model):
    """用於管理系統級別的一次性註冊啟用碼。"""
    code = models.CharField(max_length=16, unique=True, verbose_name="啟用碼")
    is_used = models.BooleanField(default=False, verbose_name="是否已使用")
    used_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='used_activation_code',
        verbose_name="使用者"
    )
    used_at = models.DateTimeField(null=True, blank=True, verbose_name="使用時間")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="過期時間")
    notes = models.TextField(blank=True, verbose_name="備註") # 例如：這批 code 是給哪個客戶的

    def save(self, *args, **kwargs):
        if not self.code:
            # 生成一個更複雜、不易猜測的 code
            self.code = f"MDG-{secrets.token_hex(6).upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "系統啟用碼"
        verbose_name_plural = "14. 系統啟用碼管理" # 讓它在 Admin 後台排後面
        
# =============================================================================
# 2. 系統與公告 (System & Announcement)
# =============================================================================

class SystemAnnouncement(models.Model):
    """系統級公告。"""
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
    """群組內部公告，具備自動編號功能。"""
    id = models.BigAutoField(primary_key=True)
    announcement_number = models.CharField(max_length=50, unique=True, blank=True) 
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    publisher = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    publish_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.announcement_number:
            self.announcement_number = f"ANN-{self.group.id}-{secrets.token_hex(4).upper()}"
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'group_announcement'
        verbose_name = "群組公告"
        verbose_name_plural = "5. 群組公告"

class InvitationCode(models.Model):
    """具時效性、一次性的群組邀請碼。"""
    name = models.CharField(max_length=100, default='Default Invite', verbose_name="邀請名稱") 
    code = models.CharField(max_length=8, unique=True, verbose_name="邀請碼")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name="所屬群組")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="建立者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    expires_at = models.DateTimeField(verbose_name="過期時間")
    is_used = models.BooleanField(default=False, verbose_name="是否已使用")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.code = secrets.token_hex(4).upper()
            self.expires_at = timezone.now() + timedelta(days=1)
        super().save(*args, **kwargs)

    def __str__(self): return f"{self.group.name} 的邀請碼: {self.code}"

    class Meta:
        verbose_name = "群組邀請碼"
        verbose_name_plural = "12. 群組邀請碼"

# =============================================================================
# 3. 車輛與行程管理 (Vehicle & Trip Management)
# =============================================================================

class VehicleDevice(models.Model):
    """車機設備模型。"""
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

class Trip(models.Model):
    """核心的行程紀錄模型。"""
    id = models.BigAutoField(primary_key=True)
    trip_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    device = models.ForeignKey(VehicleDevice, on_delete=models.CASCADE)
    personnel = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    in_car_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="車內評分")
    out_car_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="車外評分")
    ai_suggestion = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_mileage = models.FloatField(blank=True, null=True, verbose_name="總里程(KM)")

    class Meta:
        db_table = 'trip'
        verbose_name = "行程"
        verbose_name_plural = "7. 行程管理"

class RouteLog(models.Model):
    """儲存行程中的地理軌跡資料。"""
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
    """定義危險駕駛事件的評分標準與扣分。"""
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
    """儲存行程中由 AI 偵測到的具體駕駛事件。"""
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
    """儲存與行程關聯的影像紀錄資訊。"""
    id = models.BigAutoField(primary_key=True)
    video_number = models.CharField(max_length=50, unique=True, blank=True)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='videorecord_set')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=500)
    file_size = models.BigIntegerField(blank=True, null=True)
    video_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="影片雲端網址")

    def save(self, *args, **kwargs):
        if not self.video_number:
            self.video_number = f"VID-{self.trip.id}-{secrets.token_hex(4).upper()}"
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'video_record'
        verbose_name = "影像紀錄"
        verbose_name_plural = "11. 影像紀錄"

# =============================================================================
# 4. 回饋 (Feedback)
# =============================================================================

class TripSuggestionFeedback(models.Model):
    """用於儲存使用者對 AI 行程建議的回饋。"""
    FEEDBACK_CHOICES = [(1, '有幫助'), (-1, '沒有幫助')]

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, verbose_name="關聯行程")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="回饋使用者")
    feedback_type = models.IntegerField(choices=FEEDBACK_CHOICES, verbose_name="回饋類型")
    comment = models.TextField(blank=True, null=True, verbose_name="使用者評論")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="回饋時間")

    def __str__(self): return f"Feedback for Trip {self.trip.id} by {self.user.username}"

    class Meta:
        unique_together = ('trip', 'user') # 確保同一使用者對同一行程只能回饋一次
        verbose_name = "AI行程建議回饋"
        verbose_name_plural = "13. AI行程建議回饋"