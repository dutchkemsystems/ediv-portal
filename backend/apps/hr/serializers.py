from rest_framework import serializers
from .models import JobPosting, JobApplication, PayrollPeriod, Payslip


class JobPostingSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    application_count = serializers.SerializerMethodField()
    
    class Meta:
        model = JobPosting
        fields = ['id', 'title', 'description', 'department', 'department_name', 'school',
                  'status', 'salary_range', 'requirements', 'closing_date', 'created_by',
                  'created_by_name', 'application_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name()
    
    def get_department_name(self, obj):
        return obj.department.name
    
    def get_application_count(self, obj):
        return obj.applications.count()


class JobApplicationSerializer(serializers.ModelSerializer):
    applicant_name = serializers.SerializerMethodField()
    job_title = serializers.SerializerMethodField()
    reviewed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = JobApplication
        fields = ['id', 'job_posting', 'job_title', 'applicant', 'applicant_name',
                  'cover_letter', 'resume', 'status', 'notes', 'reviewed_by',
                  'reviewed_by_name', 'review_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_applicant_name(self, obj):
        return obj.applicant.get_full_name()
    
    def get_job_title(self, obj):
        return obj.job_posting.title
    
    def get_reviewed_by_name(self, obj):
        if obj.reviewed_by:
            return obj.reviewed_by.get_full_name()
        return None


class PayrollPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollPeriod
        fields = ['id', 'name', 'start_date', 'end_date', 'payment_date', 'is_processed', 'created_at']
        read_only_fields = ['id', 'created_at']


class PayslipSerializer(serializers.ModelSerializer):
    staff_name = serializers.SerializerMethodField()
    period_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Payslip
        fields = ['id', 'staff', 'staff_name', 'period', 'period_name', 'basic_salary',
                  'allowances', 'deductions', 'tax', 'pension', 'net_salary',
                  'is_paid', 'payment_date', 'created_at']
        read_only_fields = ['id', 'created_at', 'net_salary']
    
    def get_staff_name(self, obj):
        return obj.staff.user.get_full_name()
    
    def get_period_name(self, obj):
        return obj.period.name

