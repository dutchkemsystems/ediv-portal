from rest_framework import serializers
from .models import Staff, StaffLeave, StaffPerformance
from apps.users.models import User
from apps.users.serializers import UserSerializer


class StaffSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )
    full_name = serializers.SerializerMethodField()
    years_of_service = serializers.ReadOnlyField()
    
    class Meta:
        model = Staff
        fields = ['id', 'user', 'user_id', 'full_name', 'staff_id', 'employee_number',
                  'school', 'department', 'category', 'designation', 'employment_type',
                  'qualification', 'date_of_birth', 'gender', 'marital_status',
                  'state_of_origin', 'lga_of_origin', 'residential_address',
                  'emergency_contact_name', 'emergency_contact_phone',
                  'bank_name', 'bank_account_number', 'bank_account_name',
                  'pension_pin', 'tax_id', 'date_joined', 'date_of_first_appointment',
                  'date_of_retirement', 'grade_level', 'step', 'salary',
                  'is_active', 'is_suspended', 'suspension_reason',
                  'profile_photo', 'years_of_service', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()


class StaffListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Staff
        fields = ['id', 'full_name', 'staff_id', 'employee_number', 'school_name',
                  'category', 'designation', 'is_active']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    
    def get_school_name(self, obj):
        if obj.school:
            return obj.school.name
        return None


class StaffLeaveSerializer(serializers.ModelSerializer):
    staff_name = serializers.SerializerMethodField()
    duration_days = serializers.ReadOnlyField()
    approved_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StaffLeave
        fields = ['id', 'staff', 'staff_name', 'leave_type', 'start_date', 'end_date',
                  'reason', 'status', 'approved_by', 'approved_by_name', 'approval_date',
                  'remarks', 'duration_days', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_staff_name(self, obj):
        return obj.staff.user.get_full_name()
    
    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return obj.approved_by.get_full_name()
        return None


class StaffPerformanceSerializer(serializers.ModelSerializer):
    staff_name = serializers.SerializerMethodField()
    average_score = serializers.ReadOnlyField()
    reviewed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StaffPerformance
        fields = ['id', 'staff', 'staff_name', 'academic_year', 'term', 'rating',
                  'punctuality_score', 'dedication_score', 'teaching_quality_score',
                  'student_performance_score', 'average_score', 'comments',
                  'reviewed_by', 'reviewed_by_name', 'review_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_staff_name(self, obj):
        return obj.staff.user.get_full_name()
    
    def get_reviewed_by_name(self, obj):
        if obj.reviewed_by:
            return obj.reviewed_by.get_full_name()
        return None

