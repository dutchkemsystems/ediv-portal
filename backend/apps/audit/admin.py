from django.contrib import admin
from .models import AuditLog, ComplianceItem, ComplianceRecord, Violation


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'module', 'object_type', 'ip_address', 'created_at']
    list_filter = ['action', 'module', 'created_at']
    search_fields = ['user__email', 'object_repr', 'description', 'ip_address']
    raw_id_fields = ['user']
    readonly_fields = ['created_at']


@admin.register(ComplianceItem)
class ComplianceItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'frequency', 'is_mandatory', 'is_active']
    list_filter = ['category', 'is_mandatory', 'is_active']
    search_fields = ['title', 'description']


@admin.register(ComplianceRecord)
class ComplianceRecordAdmin(admin.ModelAdmin):
    list_display = ['item', 'school', 'department', 'status', 'academic_year', 'due_date']
    list_filter = ['status', 'academic_year', 'item__category']
    search_fields = ['item__title', 'school__name', 'evidence']
    raw_id_fields = ['item', 'school', 'department', 'reviewed_by', 'created_by']


@admin.register(Violation)
class ViolationAdmin(admin.ModelAdmin):
    list_display = ['title', 'severity', 'status', 'category', 'school', 'incident_date']
    list_filter = ['severity', 'status', 'category']
    search_fields = ['title', 'description', 'school__name']
    raw_id_fields = ['school', 'department', 'reported_by', 'assigned_to']
