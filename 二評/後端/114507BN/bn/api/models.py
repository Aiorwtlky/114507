from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

# =============================================================================
# 1. 人員與群組管理 (User & Group Management)
# =============================================================================

class PersonnelProfile(models.Model):
    GENDER_CHOICES = [('MALE', '男'), ('FEMALE', '女'), ('UNSPECIFIED', '不願透漏')]
    license_validator = RegexValidator(regex=r'^[A-Z]\d{9}$', message='駕照號碼格式必須為：1位英文大寫字母 + 9位數字。')
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name="使用者帳號")
    personnel_number = models.CharField(max_length=50, unique=True, verbose_name="人員編號")
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='UNSPECIFIED', verbose_name="性別")
    license_number = models.CharField(max_length=10, unique=True, validators=[license_validator], verbose_name="駕照號碼")

    class Meta:
        db_table = 'personnel_profile' # 建議為 profile 建立獨立的表
        verbose_name = "人員詳細資料"
        verbose_name_plural = "1. 人員詳細資料"
    def __str__(self): return self.user.username

class Group(models.Model):
    id = models.BigAutoField(primary_key=True)
    group_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

    class Meta:
        db_table = 'group_member'
        unique_together = (('group', 'user'),)
        verbose_name = "群組成員"
        verbose_name_plural = "3. 群組成員"

# =============================================================================
# 2. 公告與行程管理 (Announcement & Trip Management)
# =============================================================================

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
    announcement_number = models.CharField(max_length=50, unique=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    publisher = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    publish_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
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
    class Meta:
        db_table = 'trip'
        verbose_name = "行程"
        verbose_name_plural = "7. 行程管理"

# =============================================================================
# 3. 數據記錄與評分 (Data Logging & Scoring)
# =============================================================================

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