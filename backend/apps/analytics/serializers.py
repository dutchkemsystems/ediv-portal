from rest_framework import serializers
from .models import AnalyticsReport, KPI


class AnalyticsReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalyticsReport
        fields = ['id', 'title', 'report_type', 'description', 'generated_by', 'generated_by_name',
                  'parameters', 'data', 'file', 'is_scheduled', 'schedule_frequency',
                  'last_generated', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_generated_by_name(self, obj):
        return obj.generated_by.get_full_name()


class KPISerializer(serializers.ModelSerializer):
    achievement_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = KPI
        fields = ['id', 'name', 'description', 'metric_type', 'target_value', 'current_value',
                  'unit', 'academic_year', 'is_active', 'achievement_percentage',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

