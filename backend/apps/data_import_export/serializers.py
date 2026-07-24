from rest_framework import serializers
from .models import ImportJob, ImportError


class ImportErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportError
        fields = ['id', 'job', 'row_number', 'field_name', 'error_message', 'raw_value']
        read_only_fields = ['id']


class ImportJobSerializer(serializers.ModelSerializer):
    errors = ImportErrorSerializer(many=True, read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ImportJob
        fields = ['id', 'file_name', 'file_type', 'target_model', 'status',
                  'total_rows', 'success_rows', 'error_rows', 'error_log',
                  'created_by', 'created_by_name', 'errors', 'created_at', 'completed_at']
        read_only_fields = ['id', 'created_at', 'completed_at', 'created_by',
                            'status', 'total_rows', 'success_rows', 'error_rows', 'error_log']

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name()


class ImportJobListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ImportJob
        fields = ['id', 'file_name', 'file_type', 'target_model', 'status',
                  'total_rows', 'success_rows', 'error_rows', 'created_by_name', 'created_at']

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name()
