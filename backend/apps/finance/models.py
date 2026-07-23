from django.db import models
from django.conf import settings
from apps.schools.models import School


class FeeType(models.TextChoices):
    TUITION = 'TUITION', 'Tuition Fee'
    DEVELOPMENT = 'DEVELOPMENT', 'Development Levy'
    SPORTS = 'SPORTS', 'Sports Fee'
    LIBRARY = 'LIBRARY', 'Library Fee'
    LABORATORY = 'LABORATORY', 'Laboratory Fee'
    EXAMINATION = 'EXAMINATION', 'Examination Fee'
    ICT = 'ICT', 'ICT Fee'
    PTA = 'PTA', 'PTA Levy'
    INSURANCE = 'INSURANCE', 'Insurance'
    MEDICAL = 'MEDICAL', 'Medical Fee'
    TRANSPORT = 'TRANSPORT', 'Transport Fee'
    UNIFORM = 'UNIFORM', 'Uniform Fee'
    OTHER = 'OTHER', 'Other'


class FeeStructure(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='fee_structures')
    name = models.CharField(max_length=200)
    fee_type = models.CharField(max_length=20, choices=FeeType.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    academic_year = models.CharField(max_length=9)
    term = models.CharField(max_length=20, choices=[
        ('FIRST', 'First Term'),
        ('SECOND', 'Second Term'),
        ('THIRD', 'Third Term'),
    ])
    class_level = models.CharField(max_length=20, blank=True)
    is_compulsory = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['school', 'academic_year', 'term', 'fee_type']
        indexes = [
            models.Index(fields=['school']),
            models.Index(fields=['fee_type']),
            models.Index(fields=['academic_year']),
        ]
    
    def __str__(self):
        return f"{self.school.name} - {self.name} ({self.amount})"


class PaymentStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    PARTIAL = 'PARTIAL', 'Partial'
    COMPLETED = 'COMPLETED', 'Completed'
    OVERPAID = 'OVERPAID', 'Overpaid'


class StudentFee(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='fees')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='student_fees')
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'fee_structure']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.fee_structure.name}"
    
    def save(self, *args, **kwargs):
        self.balance = self.amount_due - self.amount_paid
        if self.balance <= 0:
            self.status = 'COMPLETED'
        elif self.amount_paid > 0:
            self.status = 'PARTIAL'
        else:
            self.status = 'PENDING'
        super().save(*args, **kwargs)


class PaymentMethod(models.TextChoices):
    CASH = 'CASH', 'Cash'
    BANK_TRANSFER = 'BANK_TRANSFER', 'Bank Transfer'
    ONLINE = 'ONLINE', 'Online Payment'
    POS = 'POS', 'POS'
    CHEQUE = 'CHEQUE', 'Cheque'


class Payment(models.Model):
    student_fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    reference_number = models.CharField(max_length=100, unique=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_date = models.DateField()
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='received_payments'
    )
    notes = models.TextField(blank=True)
    receipt_number = models.CharField(max_length=50, blank=True)
    is_confirmed = models.BooleanField(default=False)
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='confirmed_payments'
    )
    confirmation_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['reference_number']),
            models.Index(fields=['payment_date']),
            models.Index(fields=['is_confirmed']),
        ]
    
    def __str__(self):
        return f"{self.student_fee.student.user.get_full_name()} - {self.amount}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.student_fee.amount_paid = self.student_fee.payments.filter(is_confirmed=True).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        self.student_fee.save()


class BudgetCategory(models.TextChoices):
    PERSONNEL = 'PERSONNEL', 'Personnel Costs'
    CAPITAL = 'CAPITAL', 'Capital Expenditure'
    RECURRENT = 'RECURRENT', 'Recurrent Expenditure'
    MAINTENANCE = 'MAINTENANCE', 'Maintenance'
    SUPPLIES = 'SUPPLIES', 'Supplies'
    UTILITIES = 'UTILITIES', 'Utilities'
    TRANSPORT = 'TRANSPORT', 'Transport'
    TRAINING = 'TRAINING', 'Training'
    OTHER = 'OTHER', 'Other'


class Budget(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='budgets')
    category = models.CharField(max_length=20, choices=BudgetCategory.choices)
    description = models.CharField(max_length=200)
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2)
    spent_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    academic_year = models.CharField(max_length=9)
    term = models.CharField(max_length=20, choices=[
        ('FIRST', 'First Term'),
        ('SECOND', 'Second Term'),
        ('THIRD', 'Third Term'),
    ])
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_budgets'
    )
    approval_date = models.DateField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['school', 'academic_year', 'category']
        indexes = [
            models.Index(fields=['school']),
            models.Index(fields=['category']),
            models.Index(fields=['academic_year']),
        ]
    
    def __str__(self):
        return f"{self.school.name} - {self.description}"
    
    @property
    def remaining_budget(self):
        return self.allocated_amount - self.spent_amount
    
    @property
    def utilization_rate(self):
        if self.allocated_amount > 0:
            return (self.spent_amount / self.allocated_amount) * 100
        return 0


class GrantStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    PENDING = 'PENDING', 'Pending Approval'
    APPROVED = 'APPROVED', 'Approved'
    ACTIVE = 'ACTIVE', 'Active'
    COMPLETED = 'COMPLETED', 'Completed'
    REJECTED = 'REJECTED', 'Rejected'


class Grant(models.Model):
    name = models.CharField(max_length=200)
    funding_source = models.CharField(max_length=200, help_text='Organization or government body providing the grant')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    purpose = models.TextField()
    status = models.CharField(max_length=20, choices=GrantStatus.choices, default='DRAFT')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='grants', null=True, blank=True)
    department = models.ForeignKey('departments.Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='grants')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    academic_year = models.CharField(max_length=9, blank=True)
    amount_disbursed = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    amount_utilized = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    conditions = models.TextField(blank=True, help_text='Terms and conditions of the grant')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_grants'
    )
    approval_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_grants'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['funding_source']),
            models.Index(fields=['academic_year']),
        ]

    def __str__(self):
        return f"{self.name} - {self.funding_source} (₦{self.amount})"

    @property
    def remaining_amount(self):
        return self.amount - self.amount_utilized

    @property
    def utilization_rate(self):
        if self.amount > 0:
            return (self.amount_utilized / self.amount) * 100
        return 0
