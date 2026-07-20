from django.contrib import admin
from .models import (
    Class, Subject, ClassSubject, Exam, ExamResult, ReportCard,
    AcademicCalendar, StudentEnrollment
)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'level', 'section', 'class_teacher', 'academic_year', 'is_active']
    list_filter = ['school', 'level', 'academic_year', 'is_active']
    search_fields = ['name', 'school__name']
    raw_id_fields = ['school', 'class_teacher']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'category', 'is_compulsory']
    list_filter = ['category', 'is_compulsory']
    search_fields = ['name', 'code']


@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ['class_obj', 'subject', 'teacher', 'is_active']
    list_filter = ['is_active']
    raw_id_fields = ['class_obj', 'subject', 'teacher']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'exam_type', 'academic_year', 'term', 'start_date', 'end_date']
    list_filter = ['school', 'exam_type', 'academic_year', 'term']
    search_fields = ['name', 'school__name']
    raw_id_fields = ['school']


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'subject', 'marks_obtained', 'grade']
    list_filter = ['exam', 'subject']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    raw_id_fields = ['student', 'exam', 'subject', 'entered_by']


@admin.register(ReportCard)
class ReportCardAdmin(admin.ModelAdmin):
    list_display = ['student', 'academic_year', 'term', 'average_marks', 'class_position', 'is_released']
    list_filter = ['academic_year', 'term', 'is_released']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    raw_id_fields = ['student']


@admin.register(AcademicCalendar)
class AcademicCalendarAdmin(admin.ModelAdmin):
    list_display = ['title', 'school', 'event_type', 'start_date', 'end_date', 'academic_year']
    list_filter = ['school', 'event_type', 'academic_year']
    search_fields = ['title']
    raw_id_fields = ['school']


@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'class_obj', 'academic_year', 'term', 'enrollment_date', 'status']
    list_filter = ['academic_year', 'term', 'status']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    raw_id_fields = ['student', 'class_obj']
