from django.contrib import admin
from .models import (
    Personnel, Group, GroupMember, SystemAnnouncement, GroupAnnouncement,
    VehicleDevice, Trip, RouteLog, ScoringStandard, AiVisionLog, VideoRecord
)

@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    list_display = ('personnel_number', 'name', 'email', 'license_number', 'is_active')
    search_fields = ('personnel_number', 'name', 'email') 
    list_filter = ('is_active',)

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
    search_fields = ('trip_number', 'name', 'personnel__name')
    list_filter = ('group', 'start_time')
    autocomplete_fields = ['personnel', 'group', 'device']

@admin.register(ScoringStandard)
class ScoringStandardAdmin(admin.ModelAdmin):
    list_display = ('event_number', 'description', 'deduction_points', 'is_active')
    list_filter = ('is_active',)

admin.site.register(GroupMember)
admin.site.register(SystemAnnouncement)
admin.site.register(GroupAnnouncement)
admin.site.register(RouteLog)
admin.site.register(AiVisionLog)
admin.site.register(VideoRecord)