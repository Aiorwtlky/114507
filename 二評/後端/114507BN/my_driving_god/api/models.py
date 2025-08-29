from django.db import models
from django.core.validators import RegexValidator 

class Personnel(models.Model):
    GENDER_CHOICES = [
        ('MALE', '男'),
        ('FEMALE', '女'),
        ('UNSPECIFIED', '不願透漏'),
    ]

    license_validator = RegexValidator(
        regex=r'^[A-Z]\d{9}$', 
        message='駕照號碼格式必須為：1位英文大寫字母 + 9位數字。'
    )

    id = models.BigAutoField(primary_key=True) 
    personnel_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=255, unique=True) 
    password = models.CharField(max_length=255)
    
    gender = models.CharField(
        max_length=20, 
        choices=GENDER_CHOICES, 
        default='UNSPECIFIED',
        verbose_name="性別"
    )
    
    license_number = models.CharField(
        max_length=10, 
        unique=True,
        validators=[license_validator],
        verbose_name="駕照號碼"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'personnel'
        verbose_name = "人員"
        verbose_name_plural = "personnel"

    def __str__(self):
        return self.name

class Group(models.Model):
    id = models.BigAutoField(primary_key=True)
    group_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'group'

class GroupMember(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(Group, models.DO_NOTHING)
    personnel = models.ForeignKey('Personnel', models.DO_NOTHING)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'group_member'
        unique_together = (('group', 'personnel'),)

class SystemAnnouncement(models.Model):
    id = models.BigAutoField(primary_key=True)
    announcement_number = models.CharField(max_length=50, unique=True)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'system_announcement'

class GroupAnnouncement(models.Model):
    id = models.BigAutoField(primary_key=True)
    announcement_number = models.CharField(max_length=50, unique=True)
    group = models.ForeignKey(Group, models.DO_NOTHING)
    publisher = models.ForeignKey('Personnel', models.DO_NOTHING)
    content = models.TextField()
    publish_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'group_announcement'

class VehicleDevice(models.Model):
    id = models.BigAutoField(primary_key=True)
    device_number = models.CharField(max_length=50, unique=True)
    vehicle_type = models.CharField(max_length=20)
    activation_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vehicle_device'

class Trip(models.Model):
    id = models.BigAutoField(primary_key=True)
    trip_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    group = models.ForeignKey(Group, models.DO_NOTHING)
    device = models.ForeignKey('VehicleDevice', models.DO_NOTHING)
    personnel = models.ForeignKey('Personnel', models.DO_NOTHING)
    score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    ai_suggestion = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'trip'

class RouteLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    trip = models.ForeignKey('Trip', models.DO_NOTHING)
    timestamp = models.DateTimeField()
    location = models.CharField(max_length=100)
    speed = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'route_log'

class ScoringStandard(models.Model):
    id = models.AutoField(primary_key=True)
    event_number = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255)
    deduction_points = models.IntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'scoring_standard'

class AiVisionLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    trip = models.ForeignKey('Trip', models.DO_NOTHING)
    event = models.ForeignKey('ScoringStandard', models.DO_NOTHING)
    timestamp = models.DateTimeField()
    event_details = models.CharField(max_length=255)
    confidence_score = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'ai_vision_log'

class VideoRecord(models.Model):
    id = models.BigAutoField(primary_key=True)
    video_number = models.CharField(max_length=50, unique=True)
    trip = models.ForeignKey('Trip', models.DO_NOTHING)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=500)
    file_size = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'video_record'