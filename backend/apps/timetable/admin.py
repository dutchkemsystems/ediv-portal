from django.contrib import admin
from .models import Period, Timetable, TimetableEntry, TeacherTimetable


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'start_time', 'end_time', 'period_number', 'is_break']
    list_filter = ['school', 'is_break', 'is_active']
    raw_id_fields = ['school']


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['class_obj', 'school', 'academic_year', 'term', 'is_active']
    list_filter = ['school', 'academic_year', 'term', 'is_active']
    raw_id_fields = ['school', 'class_obj']


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ['timetable', 'day', 'period', 'subject', 'teacher', 'room']
    list_filter = ['day']
    raw_id_fields = ['timetable', 'period', 'subject', 'teacher']


@admin.register(TeacherTimetable)
class TeacherTimetableAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'timetable']
    raw_id_fields = ['teacher', 'timetable']
