from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinLengthValidator
from .managers import UserManager


class User(AbstractUser):
    """Custom user model with role-based access control."""
    
    class Role(models.TextChoices):
        SYSADMIN = 'SYSADMIN', 'System Administrator'
        TG = 'TG', 'Tutor General'
        PS = 'PS', 'Permanent Secretary'
        HR = 'HR', 'Admin & HR Head'
        FIN = 'FIN', 'Finance Director'
        AUDIT = 'AUDIT', 'Internal Audit Head'
        QA = 'QA', 'Quality Assurance Head'
        CC = 'CC', 'Co-Curricular Head'
        EMIS = 'EMIS', 'EMIS Head'
        PLAN = 'PLAN', 'Planning Head'
        PROC = 'PROC', 'Procurement Head'
        PA = 'PA', 'Public Affairs Head'
        SA = 'SA', 'Schools Admin Head'
        FRENCH = 'FRENCH', 'French Unit Head'
        REG = 'REG', 'Registry Head'
        PRI = 'PRI', 'Principal'
        VP = 'VP', 'Vice Principal'
        TCH = 'TCH', 'Teacher'
        STD = 'STD', 'Student'
        PAR = 'PAR', 'Parent'
        REG_OFF = 'REG_OFF', 'Registry Officer'
        SA_OFF = 'SA_OFF', 'School Admin Officer'
    
    username = None
    email = models.EmailField('email address', unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STD)
    phone_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=64, blank=True)  # Base32 encoded 32 bytes = 52 chars
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']
    
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
    
    @property
    def is_department_head(self):
        return self.role in ['HR', 'FIN', 'AUDIT', 'QA', 'CC', 'EMIS', 'PLAN', 'PROC', 'PA', 'SA', 'FRENCH', 'REG']
    
    @property
    def is_school_staff(self):
        return self.role in ['PRI', 'VP', 'TCH', 'SA_OFF']
    
    @property
    def is_head_office_staff(self):
        return self.role in ['TG', 'PS', 'HR', 'FIN', 'AUDIT', 'QA', 'CC', 'EMIS', 'PLAN', 'PROC', 'PA', 'SA', 'FRENCH', 'REG', 'REG_OFF']
    
    def can_access_module(self, module):
        """Check if user can access a specific module based on role."""
        permissions = {
            'dashboard': ['SYSADMIN', 'TG', 'PS', 'HR', 'FIN', 'AUDIT', 'QA', 'CC', 'EMIS', 'PLAN', 'PROC', 'PA', 'SA', 'FRENCH', 'REG', 'PRI', 'VP', 'TCH', 'STD', 'PAR'],
            'registry': ['SYSADMIN', 'TG', 'PS', 'HR', 'FIN', 'AUDIT', 'QA', 'CC', 'EMIS', 'PLAN', 'PROC', 'PA', 'SA', 'FRENCH', 'REG', 'REG_OFF', 'PRI', 'VP', 'TCH', 'STD', 'PAR'],
            'hr': ['SYSADMIN', 'TG', 'PS', 'HR'],
            'finance': ['SYSADMIN', 'TG', 'PS', 'FIN'],
            'qa': ['SYSADMIN', 'TG', 'PS', 'QA'],
            'academics': ['SYSADMIN', 'TG', 'PS', 'PRI', 'VP', 'TCH', 'STD', 'PAR'],
            'attendance': ['SYSADMIN', 'TG', 'PS', 'PRI', 'VP', 'TCH', 'STD', 'PAR'],
            'co_curricular': ['SYSADMIN', 'TG', 'PS', 'CC', 'PRI', 'VP', 'TCH', 'STD'],
            'reports': ['SYSADMIN', 'TG', 'PS', 'HR', 'FIN', 'AUDIT', 'QA', 'CC', 'EMIS', 'PLAN', 'PROC', 'PA', 'SA', 'FRENCH', 'REG', 'PRI', 'VP', 'TCH', 'STD', 'PAR'],
        }
        return module in permissions and self.role in permissions[module]


class Module(models.TextChoices):
    DASHBOARD = 'dashboard', 'Dashboard'
    SCHOOLS = 'schools', 'Schools'
    STAFF = 'staff', 'Staff Management'
    STUDENTS = 'students', 'Students'
    ATTENDANCE = 'attendance', 'Attendance'
    ACADEMICS = 'academics', 'Academics'
    FINANCE = 'finance', 'Finance'
    GRANTS = 'grants', 'Grants'
    HR = 'hr', 'HR & Recruitment'
    REGISTRY = 'registry', 'E-Registry'
    FILES = 'files', 'Files'
    WORKFLOWS = 'workflows', 'Workflows'
    COMMUNICATION = 'communication', 'Communication'
    NOTIFICATIONS = 'notifications', 'Notifications'
    TIMETABLE = 'timetable', 'Timetable'
    TRANSPORT = 'transport', 'Transport'
    ASSETS = 'assets', 'Assets'
    DISCIPLINE = 'discipline', 'Discipline'
    LIBRARY = 'library', 'Library'
    E_LEARNING = 'e_learning', 'E-Learning'
    WELLNESS = 'wellness', 'Wellness'
    ALUMNI = 'alumni', 'Alumni'
    INFRASTRUCTURE = 'infrastructure', 'Infrastructure'
    INSPECTION = 'inspection', 'Inspection'
    FRENCH = 'french', 'French Unit'
    CO_CURRICULAR = 'co_curricular', 'Co-Curricular'
    CPD = 'cpd', 'CPD'
    REPORTS = 'reports', 'Reports'
    ANALYTICS = 'analytics', 'Analytics'
    PRIVILEGES = 'privileges', 'Privileges'


class Privilege(models.Model):
    """Role-based module access privileges."""
    role = models.CharField(max_length=15, choices=User.Role.choices)
    module = models.CharField(max_length=30, choices=Module.choices)
    can_view = models.BooleanField(default=True)
    can_create = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_approve = models.BooleanField(default=False)
    can_export = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['role', 'module']
        ordering = ['role', 'module']
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['module']),
        ]

    def __str__(self):
        return f"{self.role} - {self.module} (View: {self.can_view}, Edit: {self.can_edit})"


class RolePrivilege(models.Model):
    """Default privilege template for a role."""
    role = models.CharField(max_length=15, choices=User.Role.choices, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['role']

    def __str__(self):
        return f"Privilege Template: {self.role}"
