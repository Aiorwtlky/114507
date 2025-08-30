# api/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# 導入我們在 models.py 中定義的所有模型
from .models import (
    PersonnelProfile,
    Group,
    GroupMember,
    SystemAnnouncement,
    GroupAnnouncement,
    VehicleDevice,
    Trip,
    RouteLog,
    ScoringStandard,
    AiVisionLog,
    VideoRecord
)

# --- 為 User 模型整合 Profile (這是讓後台更強大的關鍵) ---

# 1. 定義一個 Inline Admin，讓 Profile 可以直接在 User 頁面中嵌入編輯
class PersonnelProfileInline(admin.StackedInline):
    """
    Defines the inline admin representation for PersonnelProfile.
    This allows editing the profile directly within the User admin page.
    """
    model = PersonnelProfile
    can_delete = False # 一般不希望誤刪 Profile
    verbose_name_plural = '人員詳細資料 (Profile)'

# 2. 重新定義 User Admin，將 Profile Inline 加入
class UserAdmin(BaseUserAdmin):
    """
    Extends the base UserAdmin to include the PersonnelProfile inline.
    """
    inlines = (PersonnelProfileInline,) # 注意這裡有一個逗號

# 3. 先取消註冊 Django 預設的 User Admin，再註冊我們客製化的版本
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# --- 為其他核心模型客製化後台顯示 ---

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Admin options for the Group model."""
    list_display = ('group_number', 'name', 'created_at')
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
    get_trip_name.short_description = '行程名稱' # 設定欄位標題

@admin.register(VideoRecord)
class VideoRecordAdmin(admin.ModelAdmin):
    """Admin options for the VideoRecord model."""
    list_display = ('video_number', 'trip', 'start_time', 'end_time')
    search_fields = ('video_number',)
    autocomplete_fields = ['trip']

# --- 簡單註冊其他模型 ---
# 對於較不常異動或結構簡單的模型，可以直接註冊
admin.site.register(GroupMember)
admin.site.register(SystemAnnouncement)
admin.site.register(GroupAnnouncement)
admin.site.register(RouteLog)