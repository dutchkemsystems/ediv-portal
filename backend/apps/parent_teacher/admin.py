from django.contrib import admin
from .models import PTAMeeting, ParentTeacherMessage, StudentReportShare


@admin.register(PTAMeeting)
class PTAMeetingAdmin(admin.ModelAdmin):
    list_display = ['title', 'meeting_type', 'school', 'scheduled_date', 'scheduled_time', 'status']
    list_filter = ['meeting_type', 'status', 'is_mandatory']
    search_fields = ['title', 'school__name', 'venue']
    raw_id_fields = ['school', 'organized_by']
    filter_horizontal = ['attendees_parents']


@admin.register(ParentTeacherMessage)
class ParentTeacherMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'student', 'category', 'subject', 'is_read', 'created_at']
    list_filter = ['category', 'is_read', 'is_urgent']
    search_fields = ['subject', 'body', 'sender__email', 'recipient__email']
    raw_id_fields = ['sender', 'recipient', 'student']


@admin.register(StudentReportShare)
class StudentReportShareAdmin(admin.ModelAdmin):
    list_display = ['student', 'report_type', 'academic_year', 'term', 'shared_by', 'is_read']
    list_filter = ['report_type', 'academic_year', 'is_read']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    raw_id_fields = ['student', 'shared_by', 'shared_with']
