# 檔案路徑: api/admin.py (移除 RouteLog 版)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

#從匯入列表中移除 RouteLog 
from .models import (
    PersonnelProfile,
    Group,
    GroupMember,
    SystemAnnouncement,
    GroupAnnouncement,
    VehicleDevice,
    Trip,
    ScoringStandard,
    AiVisionLog,
    VideoRecord
)


class PersonnelProfileInline(admin.StackedInline):
    model = PersonnelProfile
    can_delete = False
    verbose_name_plural = '人員詳細資料 (Profile)'

class UserAdmin(BaseUserAdmin):
    inlines = (PersonnelProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('group_number', 'name', 'created_at')
    search_fields = ('group_number', 'name')

@admin.register(VehicleDevice)
class VehicleDeviceAdmin(admin.ModelAdmin):
    list_display = ('device_number', 'vehicle_type', 'activation_date', 'is_active')
    search_fields = ('device_number',)
    list_filter = ('vehicle_type', 'is_active')

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('trip_number', 'name', 'personnel', 'device', 'score', 'start_time', 'end_time')
    search_fields = ('trip_number', 'name', 'personnel__username')
    list_filter = ('group', 'start_time')
    autocomplete_fields = ['personnel', 'group', 'device']

@admin.register(ScoringStandard)
class ScoringStandardAdmin(admin.ModelAdmin):
    list_display = ('event_number', 'description', 'deduction_points', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('event_number', 'description')
    
@admin.register(AiVisionLog)
class AiVisionLogAdmin(admin.ModelAdmin):
    list_display = ('get_trip_name', 'event', 'timestamp', 'confidence_score')
    list_filter = ('event__description', 'timestamp')
    autocomplete_fields = ['trip', 'event']

    def get_trip_name(self, obj):
        return obj.trip.name
    get_trip_name.short_description = '行程名稱'

@admin.register(VideoRecord)
class VideoRecordAdmin(admin.ModelAdmin):
    list_display = ('video_number', 'trip', 'start_time', 'end_time')
    search_fields = ('video_number',)
    autocomplete_fields = ['trip']

# --- 簡單註冊其他模型 ---
admin.site.register(GroupMember)
admin.site.register(SystemAnnouncement)
admin.site.register(GroupAnnouncement)