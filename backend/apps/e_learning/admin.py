from django.contrib import admin
from .models import (
    Course, CourseModule, Lesson, Enrollment,
    Quiz, QuizQuestion, QuizAttempt
)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'school', 'instructor', 'status', 'start_date']
    list_filter = ['school', 'status']
    search_fields = ['title', 'code']
    raw_id_fields = ['school', 'subject', 'instructor']


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'is_active']
    list_filter = ['is_active']
    raw_id_fields = ['course']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'lesson_type', 'duration_minutes', 'order']
    list_filter = ['lesson_type']
    raw_id_fields = ['module']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrollment_date', 'status', 'progress_percentage']
    list_filter = ['status']
    raw_id_fields = ['course', 'student']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'time_limit_minutes', 'passing_score', 'is_active']
    list_filter = ['is_active']
    raw_id_fields = ['lesson']


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'question', 'question_type', 'points', 'order']
    list_filter = ['question_type']
    raw_id_fields = ['quiz']


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'quiz', 'score', 'is_passed', 'started_at']
    list_filter = ['is_passed']
    raw_id_fields = ['quiz', 'student']
