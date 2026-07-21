from django.contrib import admin
from .models import School, SchoolAcademicYear


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'school_type', 'lga', 'principal', 'current_enrollment', 'is_active']
    list_filter = ['school_type', 'lga', 'is_active']
    search_fields = ['name', 'code']
    raw_id_fields = ['principal', 'vice_principal']


@admin.register(SchoolAcademicYear)
class SchoolAcademicYearAdmin(admin.ModelAdmin):
    list_display = ['school', 'year', 'start_date', 'end_date', 'is_current']
    list_filter = ['is_current']
