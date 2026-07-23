from rest_framework import serializers
from .models import FeeStructure, StudentFee, Payment, Budget, Grant


class FeeStructureSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    
    class Meta:
        model = FeeStructure
        fields = ['id', 'school', 'school_name', 'name', 'fee_type', 'amount',
                  'academic_year', 'term', 'class_level', 'is_compulsory', 'description',
                  'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_school_name(self, obj):
        return obj.school.name


class StudentFeeSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    fee_name = serializers.SerializerMethodField()
    balance = serializers.ReadOnlyField()
    
    class Meta:
        model = StudentFee
        fields = ['id', 'student', 'student_name', 'fee_structure', 'fee_name',
                  'amount_due', 'amount_paid', 'balance', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()
    
    def get_fee_name(self, obj):
        return obj.fee_structure.name


class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    fee_name = serializers.SerializerMethodField()
    received_by_name = serializers.SerializerMethodField()
    confirmed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = ['id', 'student_fee', 'student_name', 'fee_name', 'amount', 'payment_method',
                  'reference_number', 'transaction_id', 'payment_date', 'received_by',
                  'received_by_name', 'notes', 'receipt_number', 'is_confirmed',
                  'confirmed_by', 'confirmed_by_name', 'confirmation_date',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_student_name(self, obj):
        return obj.student_fee.student.user.get_full_name()
    
    def get_fee_name(self, obj):
        return obj.student_fee.fee_structure.name
    
    def get_received_by_name(self, obj):
        if obj.received_by:
            return obj.received_by.get_full_name()
        return None
    
    def get_confirmed_by_name(self, obj):
        if obj.confirmed_by:
            return obj.confirmed_by.get_full_name()
        return None


class BudgetSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    remaining_budget = serializers.ReadOnlyField()
    utilization_rate = serializers.ReadOnlyField()

    class Meta:
        model = Budget
        fields = ['id', 'school', 'school_name', 'category', 'description',
                  'allocated_amount', 'spent_amount', 'remaining_budget', 'utilization_rate',
                  'academic_year', 'term', 'approved_by', 'approval_date', 'is_approved',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_school_name(self, obj):
        return obj.school.name


class GrantSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    remaining_amount = serializers.ReadOnlyField()
    utilization_rate = serializers.ReadOnlyField()

    class Meta:
        model = Grant
        fields = ['id', 'name', 'funding_source', 'amount', 'purpose', 'status',
                  'school', 'school_name', 'department', 'department_name',
                  'start_date', 'end_date', 'academic_year',
                  'amount_disbursed', 'amount_utilized', 'remaining_amount', 'utilization_rate',
                  'conditions', 'approved_by', 'approved_by_name', 'approval_date',
                  'notes', 'created_by', 'created_by_name', 'is_active',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_school_name(self, obj):
        return obj.school.name if obj.school else None

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None

    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return obj.approved_by.get_full_name()
        return None

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name()
        return None


class GrantListSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    remaining_amount = serializers.ReadOnlyField()

    class Meta:
        model = Grant
        fields = ['id', 'name', 'funding_source', 'amount', 'status',
                  'school_name', 'academic_year', 'remaining_amount', 'is_active']

    def get_school_name(self, obj):
        return obj.school.name if obj.school else None

