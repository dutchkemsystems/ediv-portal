from django.contrib import admin
from .models import AnalyticsReport, KPI


@admin.register(AnalyticsReport)
class AnalyticsReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'generated_by', 'is_scheduled', 'last_generated', 'is_active']
    list_filter = ['report_type', 'is_scheduled', 'is_active']
    search_fields = ['title', 'description']
    raw_id_fields = ['generated_by']


@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = ['name', 'metric_type', 'target_value', 'current_value', 'academic_year', 'is_active']
    list_filter = ['metric_type', 'academic_year', 'is_active']
    search_fields = ['name', 'description']
