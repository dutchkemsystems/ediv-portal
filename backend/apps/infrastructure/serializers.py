from rest_framework import serializers
from .models import Facility, MaintenanceRequest, Project


class FacilitySerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Facility
        fields = ['id', 'school', 'school_name', 'name', 'facility_type', 'description',
                  'condition', 'capacity', 'year_built', 'last_maintenance', 'next_maintenance',
                  'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_school_name(self, obj):
        return obj.school.name


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    facility_name = serializers.SerializerMethodField()
    requested_by_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    
    class Meta:
        model = MaintenanceRequest
        fields = ['id', 'facility', 'facility_name', 'title', 'description', 'priority',
                  'status', 'requested_by', 'requested_by_name', 'estimated_cost', 'actual_cost',
                  'assigned_to', 'assigned_to_name', 'completion_date', 'notes',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_facility_name(self, obj):
        return obj.facility.name
    
    def get_requested_by_name(self, obj):
        return obj.requested_by.get_full_name()
    
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name()
        return None


class ProjectSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    project_manager_name = serializers.SerializerMethodField()
    remaining_budget = serializers.ReadOnlyField()
    
    class Meta:
        model = Project
        fields = ['id', 'school', 'school_name', 'name', 'description', 'status',
                  'start_date', 'end_date', 'budget', 'spent', 'remaining_budget',
                  'project_manager', 'project_manager_name', 'progress_percentage',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_school_name(self, obj):
        return obj.school.name
    
    def get_project_manager_name(self, obj):
        if obj.project_manager:
            return obj.project_manager.get_full_name()
        return None

