from django.contrib import admin
from .models import Student, StudentParent, StudentMedicalRecord


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['admission_number', 'user', 'school', 'class_name', 'gender', 'status']
    list_filter = ['school', 'status', 'gender', 'is_boarding']
    search_fields = ['admission_number', 'user__first_name', 'user__last_name']
    raw_id_fields = ['user', 'school', 'class_name']


@admin.register(StudentParent)
class StudentParentAdmin(admin.ModelAdmin):
    list_display = ['student', 'user', 'relation', 'is_primary']
    list_filter = ['relation', 'is_primary']
    raw_id_fields = ['student', 'user']


@admin.register(StudentMedicalRecord)
class StudentMedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'record_date', 'condition']
    list_filter = ['record_date']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'condition']
