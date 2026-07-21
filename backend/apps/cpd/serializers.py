from rest_framework import serializers
from .models import CPDActivity, CPDEnrollment, CPDRecord


class CPDActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CPDActivity
        fields = ['id', 'title', 'training_type', 'description', 'provider', 'venue',
                  'start_date', 'end_date', 'duration_hours', 'cost', 'max_participants',
                  'status', 'is_mandatory', 'certificate_available', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CPDEnrollmentSerializer(serializers.ModelSerializer):
    staff_name = serializers.SerializerMethodField()
    activity_title = serializers.SerializerMethodField()
    
    class Meta:
        model = CPDEnrollment
        fields = ['id', 'activity', 'activity_title', 'staff', 'staff_name', 'enrollment_date',
                  'completion_date', 'certificate', 'hours_completed', 'feedback', 'rating',
                  'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_staff_name(self, obj):
        return obj.staff.user.get_full_name()
    
    def get_activity_title(self, obj):
        return obj.activity.title


class CPDRecordSerializer(serializers.ModelSerializer):
    staff_name = serializers.SerializerMethodField()
    completion_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = CPDRecord
        fields = ['id', 'staff', 'staff_name', 'academic_year', 'total_hours_required',
                  'total_hours_completed', 'activities_completed', 'certificates_earned',
                  'is_compliant', 'last_review_date', 'completion_percentage',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_staff_name(self, obj):
        return obj.staff.user.get_full_name()

