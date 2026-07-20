from rest_framework import serializers
from .models import CounselingSession, WellnessCheckIn, WellnessResource


class CounselingSessionSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    counselor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CounselingSession
        fields = ['id', 'student', 'student_name', 'counselor', 'counselor_name',
                  'counseling_type', 'session_date', 'session_time', 'duration_minutes',
                  'notes', 'recommendations', 'follow_up_date', 'is_confidential',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()
    
    def get_counselor_name(self, obj):
        return obj.counselor.get_full_name()


class WellnessCheckInSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    
    class Meta:
        model = WellnessCheckIn
        fields = ['id', 'student', 'student_name', 'date', 'mood', 'stress_level',
                  'sleep_hours', 'exercise_minutes', 'notes', 'concerns',
                  'is_flagged', 'flagged_by', 'flag_reason', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()


class WellnessResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WellnessResource
        fields = ['id', 'name', 'resource_type', 'description', 'url', 'contact_phone',
                  'contact_email', 'is_emergency', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

