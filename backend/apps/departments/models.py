from django.db import models
from django.conf import settings


class DepartmentCategory(models.TextChoices):
    CORE = 'CORE', 'Core Department'
    SUPPORT = 'SUPPORT', 'Support Unit'


class Department(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    category = models.CharField(max_length=10, choices=DepartmentCategory.choices)
    description = models.TextField(blank=True)
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_departments'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'departments'
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Unit(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='units')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_units'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['department', 'code']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.department.name} - {self.name}"
