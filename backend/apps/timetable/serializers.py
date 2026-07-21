from rest_framework import serializers
from .models import Period, Timetable, TimetableEntry, TeacherTimetable


class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = ['id', 'school', 'name', 'start_time', 'end_time', 'period_number', 'is_break', 'is_active']
        read_only_fields = ['id']


class TimetableEntrySerializer(serializers.ModelSerializer):
    subject_name = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    period_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TimetableEntry
        fields = ['id', 'timetable', 'day', 'period', 'period_name', 'subject', 'subject_name',
                  'teacher', 'teacher_name', 'room', 'is_active']
        read_only_fields = ['id']
    
    def get_subject_name(self, obj):
        return obj.subject.name
    
    def get_teacher_name(self, obj):
        if obj.teacher:
            return obj.teacher.get_full_name()
        return None
    
    def get_period_name(self, obj):
        return obj.period.name


class TimetableSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    class_name = serializers.SerializerMethodField()
    entries = TimetableEntrySerializer(many=True, read_only=True)
    
    class Meta:
        model = Timetable
        fields = ['id', 'school', 'school_name', 'class_obj', 'class_name',
                  'academic_year', 'term', 'is_active', 'entries', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_school_name(self, obj):
        return obj.school.name
    
    def get_class_name(self, obj):
        return obj.class_obj.name


class TeacherTimetableSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    timetable_display = serializers.SerializerMethodField()
    
    class Meta:
        model = TeacherTimetable
        fields = ['id', 'teacher', 'teacher_name', 'timetable', 'timetable_display']
        read_only_fields = ['id']
    
    def get_teacher_name(self, obj):
        return obj.teacher.get_full_name()
    
    def get_timetable_display(self, obj):
        return str(obj.timetable)

