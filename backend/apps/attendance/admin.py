from django.contrib import admin
from .models import StudentAttendance, StaffAttendance, AttendanceSummary


@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'status', 'time_in', 'time_out']
    list_filter = ['status', 'date']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    raw_id_fields = ['student', 'recorded_by']


@admin.register(StaffAttendance)
class StaffAttendanceAdmin(admin.ModelAdmin):
    list_display = ['staff', 'date', 'status', 'time_in', 'time_out', 'overtime_hours']
    list_filter = ['status', 'date']
    search_fields = ['staff__user__first_name', 'staff__user__last_name']
    raw_id_fields = ['staff', 'recorded_by']


@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = ['school', 'academic_year', 'term', 'attendance_rate']
    list_filter = ['academic_year', 'term']
    raw_id_fields = ['school']
