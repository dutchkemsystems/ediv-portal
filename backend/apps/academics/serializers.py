from rest_framework import serializers
from .models import (
    Class, Subject, ClassSubject, Exam, ExamResult, ReportCard,
    AcademicCalendar, StudentEnrollment
)


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'description', 'category', 'is_compulsory',
                  'applicable_levels', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ClassSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    class_teacher_name = serializers.SerializerMethodField()
    current_enrollment = serializers.ReadOnlyField()
    class_subjects = serializers.SerializerMethodField()
    
    class Meta:
        model = Class
        fields = ['id', 'school', 'school_name', 'name', 'level', 'section', 'capacity',
                  'class_teacher', 'class_teacher_name', 'academic_year', 'term',
                  'is_active', 'current_enrollment', 'class_subjects', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_school_name(self, obj):
        return obj.school.name
    
    def get_class_teacher_name(self, obj):
        if obj.class_teacher:
            return obj.class_teacher.get_full_name()
        return None
    
    def get_class_subjects(self, obj):
        return ClassSubjectSerializer(obj.class_subjects.all(), many=True).data


class ClassListSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    current_enrollment = serializers.ReadOnlyField()
    
    class Meta:
        model = Class
        fields = ['id', 'school_name', 'name', 'level', 'section', 'academic_year', 'current_enrollment']
    
    def get_school_name(self, obj):
        return obj.school.name


class ClassSubjectSerializer(serializers.ModelSerializer):
    subject_name = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ClassSubject
        fields = ['id', 'class_obj', 'subject', 'subject_name', 'teacher', 'teacher_name', 'is_active']
        read_only_fields = ['id']
    
    def get_subject_name(self, obj):
        return obj.subject.name
    
    def get_teacher_name(self, obj):
        if obj.teacher:
            return obj.teacher.get_full_name()
        return None


class ExamSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Exam
        fields = ['id', 'school', 'school_name', 'name', 'exam_type', 'academic_year',
                  'term', 'start_date', 'end_date', 'total_marks', 'pass_marks',
                  'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_school_name(self, obj):
        return obj.school.name


class ExamResultSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()
    exam_name = serializers.SerializerMethodField()
    percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = ExamResult
        fields = ['id', 'student', 'student_name', 'exam', 'exam_name', 'subject', 'subject_name',
                  'marks_obtained', 'grade', 'remark', 'entered_by', 'percentage',
                  'entered_at', 'updated_at']
        read_only_fields = ['id', 'entered_at', 'updated_at']
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()
    
    def get_subject_name(self, obj):
        return obj.subject.name
    
    def get_exam_name(self, obj):
        return obj.exam.name


class ReportCardSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    position_suffix = serializers.ReadOnlyField()
    
    class Meta:
        model = ReportCard
        fields = ['id', 'student', 'student_name', 'academic_year', 'term', 'total_marks',
                  'average_marks', 'class_position', 'total_students', 'teacher_remark',
                  'principal_remark', 'next_term_begins', 'is_released', 'position_suffix',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()


class AcademicCalendarSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AcademicCalendar
        fields = ['id', 'school', 'school_name', 'title', 'event_type', 'description',
                  'start_date', 'end_date', 'is_recurring', 'academic_year', 'term',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_school_name(self, obj):
        return obj.school.name


class StudentEnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    class_name = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentEnrollment
        fields = ['id', 'student', 'student_name', 'class_obj', 'class_name', 'school_name',
                  'academic_year', 'term', 'enrollment_date', 'status', 'previous_class',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()
    
    def get_class_name(self, obj):
        return obj.class_obj.name
    
    def get_school_name(self, obj):
        return obj.class_obj.school.name

