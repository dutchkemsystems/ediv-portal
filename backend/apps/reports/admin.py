from django.contrib import admin
from .models import Report, Dashboard, Widget


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'generated_by', 'is_scheduled', 'last_generated']
    list_filter = ['report_type', 'is_scheduled']
    search_fields = ['title', 'description']
    raw_id_fields = ['generated_by']


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'is_default', 'created_at']
    list_filter = ['is_default']
    search_fields = ['name', 'description']
    raw_id_fields = ['owner']


@admin.register(Widget)
class WidgetAdmin(admin.ModelAdmin):
    list_display = ['title', 'dashboard', 'widget_type', 'position_x', 'position_y', 'is_active']
    list_filter = ['widget_type', 'is_active']
    raw_id_fields = ['dashboard']
