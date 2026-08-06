from rest_framework import serializers
from .models import BenchmarkMetric, SchoolBenchmark, BenchmarkComparison


class BenchmarkMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = BenchmarkMetric
        fields = ['id', 'name', 'code', 'category', 'description', 'unit',
                  'higher_is_better', 'is_active']


class SchoolBenchmarkSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    metric_name = serializers.SerializerMethodField()

    class Meta:
        model = SchoolBenchmark
        fields = ['id', 'school', 'school_name', 'metric', 'metric_name',
                  'value', 'period', 'academic_session', 'calculated_at']
        read_only_fields = ['id', 'calculated_at']

    def get_school_name(self, obj):
        return obj.school.name

    def get_metric_name(self, obj):
        return obj.metric.name


class BenchmarkComparisonSerializer(serializers.ModelSerializer):
    school_a_name = serializers.SerializerMethodField()
    school_b_name = serializers.SerializerMethodField()
    metric_name = serializers.SerializerMethodField()

    class Meta:
        model = BenchmarkComparison
        fields = ['id', 'school_a', 'school_a_name', 'school_b', 'school_b_name',
                  'metric', 'metric_name', 'value_a', 'value_b', 'difference',
                  'percentage_difference', 'period', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_school_a_name(self, obj):
        return obj.school_a.name

    def get_school_b_name(self, obj):
        return obj.school_b.name

    def get_metric_name(self, obj):
        return obj.metric.name
