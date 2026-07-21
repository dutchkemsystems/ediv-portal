from rest_framework import serializers
from .models import Report, Dashboard, Widget


class ReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = ['id', 'title', 'report_type', 'description', 'generated_by',
                  'generated_by_name', 'parameters', 'file', 'is_scheduled',
                  'schedule_cron', 'last_generated', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_generated_by_name(self, obj):
        return obj.generated_by.get_full_name()


class WidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Widget
        fields = ['id', 'dashboard', 'title', 'widget_type', 'data_source', 'config',
                  'position_x', 'position_y', 'width', 'height', 'is_active',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DashboardSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    widgets = WidgetSerializer(many=True, read_only=True)
    
    class Meta:
        model = Dashboard
        fields = ['id', 'name', 'description', 'owner', 'owner_name', 'is_default',
                  'layout', 'widgets', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_owner_name(self, obj):
        return obj.owner.get_full_name()


class DashboardListSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Dashboard
        fields = ['id', 'name', 'owner_name', 'is_default', 'created_at']
    
    def get_owner_name(self, obj):
        return obj.owner.get_full_name()

