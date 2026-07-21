from django.contrib import admin
from .models import Staff, StaffLeave, StaffPerformance


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['staff_id', 'user', 'school', 'category', 'designation', 'is_active']
    list_filter = ['category', 'designation', 'employment_type', 'is_active']
    search_fields = ['staff_id', 'employee_number', 'user__first_name', 'user__last_name']
    raw_id_fields = ['user', 'school', 'department']


@admin.register(StaffLeave)
class StaffLeaveAdmin(admin.ModelAdmin):
    list_display = ['staff', 'leave_type', 'start_date', 'end_date', 'status']
    list_filter = ['leave_type', 'status']
    search_fields = ['staff__user__first_name', 'staff__user__last_name']


@admin.register(StaffPerformance)
class StaffPerformanceAdmin(admin.ModelAdmin):
    list_display = ['staff', 'academic_year', 'term', 'rating', 'average_score']
    list_filter = ['academic_year', 'term', 'rating']
    search_fields = ['staff__user__first_name', 'staff__user__last_name']
