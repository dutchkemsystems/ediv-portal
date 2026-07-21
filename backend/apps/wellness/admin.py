from django.contrib import admin
from .models import CounselingSession, WellnessCheckIn, WellnessResource


@admin.register(CounselingSession)
class CounselingSessionAdmin(admin.ModelAdmin):
    list_display = ['student', 'counselor', 'counseling_type', 'session_date', 'session_time']
    list_filter = ['counseling_type', 'session_date']
    raw_id_fields = ['student', 'counselor']


@admin.register(WellnessCheckIn)
class WellnessCheckInAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'mood', 'stress_level', 'is_flagged']
    list_filter = ['mood', 'is_flagged', 'date']
    raw_id_fields = ['student', 'flagged_by']


@admin.register(WellnessResource)
class WellnessResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'resource_type', 'is_emergency', 'is_active']
    list_filter = ['resource_type', 'is_emergency', 'is_active']
    search_fields = ['name', 'description']
