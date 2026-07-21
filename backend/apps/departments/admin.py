from django.contrib import admin
from .models import Department, Unit


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'category', 'head', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'code']


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'head', 'is_active']
    list_filter = ['department', 'is_active']
    search_fields = ['name', 'code']
