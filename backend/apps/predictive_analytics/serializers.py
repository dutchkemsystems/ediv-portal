from rest_framework import serializers
from .models import StudentRiskProfile, EarlyWarningAlert, Intervention, RiskTrend


class StudentRiskProfileSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()

    class Meta:
        model = StudentRiskProfile
        fields = ['id', 'student', 'student_name', 'school_name', 'risk_score', 'risk_level',
                  'attendance_risk', 'academic_risk', 'discipline_risk', 'financial_risk',
                  'engagement_risk', 'risk_factors', 'recommendations', 'last_analyzed',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_student_name(self, obj):
        return obj.student.user.get_full_name() if obj.student.user else str(obj.student)

    def get_school_name(self, obj):
        return obj.student.school.name if obj.student.school else None


class EarlyWarningAlertSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    acknowledged_by_name = serializers.SerializerMethodField()

    class Meta:
        model = EarlyWarningAlert
        fields = ['id', 'student', 'student_name', 'alert_type', 'risk_level',
                  'message', 'details', 'acknowledged', 'acknowledged_by',
                  'acknowledged_by_name', 'acknowledged_at', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_student_name(self, obj):
        return obj.student.user.get_full_name() if obj.student.user else str(obj.student)

    def get_acknowledged_by_name(self, obj):
        return obj.acknowledged_by.get_full_name() if obj.acknowledged_by else None


class InterventionSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = Intervention
        fields = ['id', 'student', 'student_name', 'intervention_type', 'title',
                  'description', 'assigned_to', 'assigned_to_name', 'status',
                  'outcome', 'due_date', 'completed_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_student_name(self, obj):
        return obj.student.user.get_full_name() if obj.student.user else str(obj.student)

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.get_full_name() if obj.assigned_to else None


class RiskTrendSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = RiskTrend
        fields = ['id', 'student', 'student_name', 'risk_score', 'risk_level',
                  'attendance_risk', 'academic_risk', 'discipline_risk',
                  'financial_risk', 'snapshot_date']

    def get_student_name(self, obj):
        return obj.student.user.get_full_name() if obj.student.user else str(obj.student)
