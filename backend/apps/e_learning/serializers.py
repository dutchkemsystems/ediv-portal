from rest_framework import serializers
from .models import (
    Course, CourseModule, Lesson, Enrollment,
    Quiz, QuizQuestion, QuizAttempt
)


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'module', 'title', 'lesson_type', 'content', 'video_url',
                  'document', 'duration_minutes', 'order', 'is_free', 'created_at']
        read_only_fields = ['id', 'created_at']


class CourseModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    
    class Meta:
        model = CourseModule
        fields = ['id', 'course', 'title', 'description', 'order', 'is_active', 'lessons', 'created_at']
        read_only_fields = ['id', 'created_at']


class CourseSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    instructor_name = serializers.SerializerMethodField()
    modules = CourseModuleSerializer(many=True, read_only=True)
    enrolled_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Course
        fields = ['id', 'school', 'school_name', 'title', 'code', 'description',
                  'subject', 'instructor', 'instructor_name', 'status', 'thumbnail',
                  'start_date', 'end_date', 'max_students', 'is_certified',
                  'enrolled_count', 'modules', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_school_name(self, obj):
        return obj.school.name
    
    def get_instructor_name(self, obj):
        return obj.instructor.get_full_name()


class CourseListSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    enrolled_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Course
        fields = ['id', 'school_name', 'title', 'code', 'status', 'enrolled_count']
    
    def get_school_name(self, obj):
        return obj.school.name


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    course_title = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'student', 'student_name', 'course_title',
                  'enrollment_date', 'status', 'completion_date', 'certificate',
                  'progress_percentage', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()
    
    def get_course_title(self, obj):
        return obj.course.title


class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = ['id', 'quiz', 'question', 'question_type', 'options', 'correct_answer', 'points', 'order']
        read_only_fields = ['id']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'lesson', 'title', 'description', 'time_limit_minutes',
                  'passing_score', 'max_attempts', 'is_active', 'questions', 'created_at']
        read_only_fields = ['id', 'created_at']


class QuizAttemptSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    quiz_title = serializers.SerializerMethodField()
    
    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'quiz_title', 'student', 'student_name', 'score',
                  'is_passed', 'started_at', 'completed_at', 'answers']
        read_only_fields = ['id']
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()
    
    def get_quiz_title(self, obj):
        return obj.quiz.title

