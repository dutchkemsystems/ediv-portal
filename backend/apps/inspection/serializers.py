from rest_framework import serializers
from .models import Inspection, InspectionChecklist, InspectionAction


class InspectionChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionChecklist
        fields = ['id', 'inspection', 'category', 'item', 'description', 'is_mandatory',
                  'rating', 'remarks', 'evidence_file', 'created_at']
        read_only_fields = ['id', 'created_at']


class InspectionActionSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.SerializerMethodField()
    
    class Meta:
        model = InspectionAction
        fields = ['id', 'inspection', 'action', 'description', 'assigned_to', 'assigned_to_name',
                  'due_date', 'status', 'completion_date', 'remarks', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name()
        return None


class InspectionSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    lead_inspector_name = serializers.SerializerMethodField()
    team_member_names = serializers.SerializerMethodField()
    checklists = InspectionChecklistSerializer(many=True, read_only=True)
    actions = InspectionActionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Inspection
        fields = ['id', 'school', 'school_name', 'title', 'inspection_type', 'scheduled_date',
                  'actual_date', 'status', 'lead_inspector', 'lead_inspector_name',
                  'team_members', 'team_member_names', 'objectives', 'findings',
                  'recommendations', 'overall_rating', 'report_file', 'checklists', 'actions',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_school_name(self, obj):
        return obj.school.name
    
    def get_lead_inspector_name(self, obj):
        return obj.lead_inspector.get_full_name()
    
    def get_team_member_names(self, obj):
        return [user.get_full_name() for user in obj.team_members.all()]


class InspectionListSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    lead_inspector_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Inspection
        fields = ['id', 'school_name', 'title', 'inspection_type', 'scheduled_date',
                  'status', 'lead_inspector_name', 'overall_rating']
    
    def get_school_name(self, obj):
        return obj.school.name
    
    def get_lead_inspector_name(self, obj):
        return obj.lead_inspector.get_full_name()

