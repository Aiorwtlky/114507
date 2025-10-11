# api/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# 導入我們在 models.py 中定義的所有模型
from .models import (
    PersonnelProfile,
    Group,
    GroupMember,
    ActivationCode,         # <-- 已匯入
    SystemAnnouncement,
    GroupAnnouncement,
    InvitationCode,         # <-- 已匯入
    VehicleDevice,
    Trip,
    RouteLog,
    ScoringStandard,
    AiVisionLog,
    VideoRecord,
    TripSuggestionFeedback  # <-- 已匯入
)

# --- 為 User 模型整合 Profile (維持您原本優秀的設定) ---

class PersonnelProfileInline(admin.StackedInline):
    """
    Defines the inline admin representation for PersonnelProfile.
    This allows editing the profile directly within the User admin page.
    """
    model = PersonnelProfile
    can_delete = False
    verbose_name_plural = '人員詳細資料 (Profile)'

class UserAdmin(BaseUserAdmin):
    """
    Extends the base UserAdmin to include the PersonnelProfile inline.
    """
    inlines = (PersonnelProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# --- 為其他核心模型客製化後台顯示 (維持原樣並新增) ---

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Admin options for the Group model."""
    list_display = ('group_number', 'name', 'created_by', 'created_at')
    search_fields = ('group_number', 'name')

@admin.register(VehicleDevice)
class VehicleDeviceAdmin(admin.ModelAdmin):
    """Admin options for the VehicleDevice model."""
    list_display = ('device_number', 'vehicle_type', 'activation_date', 'is_active')
    search_fields = ('device_number',)
    list_filter = ('vehicle_type', 'is_active')

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    """Admin options for the Trip model."""
    list_display = ('trip_number', 'name', 'personnel', 'device', 'score', 'start_time', 'end_time')
    search_fields = ('trip_number', 'name', 'personnel__username')
    list_filter = ('group', 'start_time')
    autocomplete_fields = ['personnel', 'group', 'device']

@admin.register(ScoringStandard)
class ScoringStandardAdmin(admin.ModelAdmin):
    """Admin options for the ScoringStandard model."""
    list_display = ('event_number', 'description', 'deduction_points', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('event_number', 'description')
    
@admin.register(AiVisionLog)
class AiVisionLogAdmin(admin.ModelAdmin):
    """Admin options for the AiVisionLog model."""
    list_display = ('get_trip_name', 'event', 'timestamp', 'confidence_score')
    list_filter = ('event__description', 'timestamp')
    autocomplete_fields = ['trip', 'event']

    def get_trip_name(self, obj):
        return obj.trip.name
    get_trip_name.short_description = '行程名稱'

@admin.register(VideoRecord)
class VideoRecordAdmin(admin.ModelAdmin):
    """Admin options for the VideoRecord model."""
    list_display = ('video_number', 'trip', 'start_time', 'end_time')
    search_fields = ('video_number',)
    autocomplete_fields = ['trip']

@admin.register(ActivationCode)
class ActivationCodeAdmin(admin.ModelAdmin):
    """Admin options for the new ActivationCode model."""
    list_display = ('code', 'current_uses', 'max_uses', 'expires_at', 'notes')
    list_filter = ('expires_at',)
    search_fields = ('code', 'notes')

@admin.register(InvitationCode)
class InvitationCodeAdmin(admin.ModelAdmin):
    """Admin options for the InvitationCode model."""
    list_display = ('code', 'group', 'name', 'is_used', 'expires_at', 'created_by')
    list_filter = ('is_used', 'group')
    search_fields = ('code', 'name')
    autocomplete_fields = ['group', 'created_by']

@admin.register(TripSuggestionFeedback)
class TripSuggestionFeedbackAdmin(admin.ModelAdmin):
    """Admin options for the TripSuggestionFeedback model."""
    list_display = ('trip', 'user', 'feedback_type', 'timestamp')
    list_filter = ('feedback_type',)
    autocomplete_fields = ['trip', 'user']

# --- 簡單註冊其他模型 (維持您原本的設定) ---
admin.site.register(GroupMember)
admin.site.register(SystemAnnouncement)
admin.site.register(GroupAnnouncement)
admin.site.register(RouteLog)