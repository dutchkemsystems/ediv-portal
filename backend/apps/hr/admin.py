from django.contrib import admin
from .models import JobPosting, JobApplication, PayrollPeriod, Payslip


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'school', 'status', 'closing_date', 'created_by']
    list_filter = ['status']
    search_fields = ['title', 'description']
    raw_id_fields = ['department', 'school', 'created_by']


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['job_posting', 'applicant', 'status', 'review_date']
    list_filter = ['status']
    search_fields = ['applicant__first_name', 'applicant__last_name']
    raw_id_fields = ['job_posting', 'applicant', 'reviewed_by']


@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'payment_date', 'is_processed']
    list_filter = ['is_processed']


@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ['staff', 'period', 'basic_salary', 'net_salary', 'is_paid', 'payment_date']
    list_filter = ['is_paid']
    raw_id_fields = ['staff', 'period']
