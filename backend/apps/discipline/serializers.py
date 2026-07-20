from rest_framework import serializers
from .models import DisciplinaryIncident, BehaviorPlan


class DisciplinaryIncidentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    reported_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DisciplinaryIncident
        fields = ['id', 'student', 'student_name', 'reported_by', 'reported_by_name',
                  'incident_type', 'severity', 'title', 'description', 'incident_date',
                  'incident_time', 'location', 'witnesses', 'status', 'action_taken',
                  'follow_up_required', 'follow_up_date', 'follow_up_notes',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()
    
    def get_reported_by_name(self, obj):
        return obj.reported_by.get_full_name()


class BehaviorPlanSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = BehaviorPlan
        fields = ['id', 'student', 'student_name', 'created_by', 'created_by_name',
                  'title', 'description', 'goals', 'strategies', 'start_date',
                  'end_date', 'review_date', 'is_active', 'progress_notes',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()
    
    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name()

