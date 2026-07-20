from django.contrib import admin
from .models import FeeStructure, StudentFee, Payment, Budget


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'fee_type', 'amount', 'academic_year', 'term']
    list_filter = ['school', 'fee_type', 'academic_year', 'term']
    search_fields = ['name', 'school__name']
    raw_id_fields = ['school']


@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):
    list_display = ['student', 'fee_structure', 'amount_due', 'amount_paid', 'balance', 'status']
    list_filter = ['status']
    search_fields = ['student__user__first_name', 'student__user__last_name']
    raw_id_fields = ['student', 'fee_structure']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['student_fee', 'amount', 'payment_method', 'reference_number', 'payment_date', 'is_confirmed']
    list_filter = ['payment_method', 'is_confirmed', 'payment_date']
    search_fields = ['reference_number', 'student_fee__student__user__first_name']
    raw_id_fields = ['student_fee', 'received_by', 'confirmed_by']


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['school', 'category', 'description', 'allocated_amount', 'spent_amount', 'is_approved']
    list_filter = ['school', 'category', 'is_approved']
    search_fields = ['description', 'school__name']
    raw_id_fields = ['school', 'approved_by']
