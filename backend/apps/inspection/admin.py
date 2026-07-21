from django.contrib import admin
from .models import Inspection, InspectionChecklist, InspectionAction


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'school', 'inspection_type', 'scheduled_date', 'status', 'overall_rating']
    list_filter = ['inspection_type', 'status', 'overall_rating']
    search_fields = ['title', 'school__name']
    raw_id_fields = ['school', 'lead_inspector']
    filter_horizontal = ['team_members']


@admin.register(InspectionChecklist)
class InspectionChecklistAdmin(admin.ModelAdmin):
    list_display = ['inspection', 'category', 'item', 'is_mandatory', 'rating']
    list_filter = ['category', 'is_mandatory', 'rating']
    raw_id_fields = ['inspection']


@admin.register(InspectionAction)
class InspectionActionAdmin(admin.ModelAdmin):
    list_display = ['inspection', 'action', 'assigned_to', 'due_date', 'status']
    list_filter = ['status']
    search_fields = ['action', 'description']
    raw_id_fields = ['inspection', 'assigned_to']
