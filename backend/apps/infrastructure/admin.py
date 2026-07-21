from django.contrib import admin
from .models import Facility, MaintenanceRequest, Project


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'facility_type', 'condition', 'capacity', 'is_active']
    list_filter = ['school', 'facility_type', 'condition', 'is_active']
    search_fields = ['name', 'description']
    raw_id_fields = ['school']


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'facility', 'priority', 'status', 'requested_by', 'completion_date']
    list_filter = ['status', 'priority']
    search_fields = ['title', 'description']
    raw_id_fields = ['facility', 'requested_by', 'assigned_to']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'status', 'start_date', 'budget', 'progress_percentage']
    list_filter = ['status']
    search_fields = ['name', 'description']
    raw_id_fields = ['school', 'project_manager']
