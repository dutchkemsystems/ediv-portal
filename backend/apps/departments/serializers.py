from rest_framework import serializers
from .models import Department, Unit


class UnitSerializer(serializers.ModelSerializer):
    head_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Unit
        fields = ['id', 'name', 'code', 'description', 'head', 'head_name', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_head_name(self, obj):
        if obj.head:
            return obj.head.get_full_name()
        return None


class DepartmentSerializer(serializers.ModelSerializer):
    head_name = serializers.SerializerMethodField()
    units = UnitSerializer(many=True, read_only=True)
    sub_departments = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'category', 'description', 'head', 'head_name', 
                  'parent', 'units', 'sub_departments', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_head_name(self, obj):
        if obj.head:
            return obj.head.get_full_name()
        return None
    
    def get_sub_departments(self, obj):
        sub_depts = obj.sub_departments.filter(is_active=True)
        return DepartmentListSerializer(sub_depts, many=True).data


class DepartmentListSerializer(serializers.ModelSerializer):
    head_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'category', 'head_name', 'is_active']
    
    def get_head_name(self, obj):
        if obj.head:
            return obj.head.get_full_name()
        return None

