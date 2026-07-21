from django.contrib import admin
from .models import CPDActivity, CPDEnrollment, CPDRecord


@admin.register(CPDActivity)
class CPDActivityAdmin(admin.ModelAdmin):
    list_display = ['title', 'training_type', 'provider', 'start_date', 'end_date', 'status']
    list_filter = ['training_type', 'status', 'is_mandatory']
    search_fields = ['title', 'description', 'provider']


@admin.register(CPDEnrollment)
class CPDEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['activity', 'staff', 'enrollment_date', 'hours_completed', 'rating']
    list_filter = ['rating']
    raw_id_fields = ['activity', 'staff']


@admin.register(CPDRecord)
class CPDRecordAdmin(admin.ModelAdmin):
    list_display = ['staff', 'academic_year', 'total_hours_required', 'total_hours_completed', 'is_compliant']
    list_filter = ['academic_year', 'is_compliant']
    raw_id_fields = ['staff']
