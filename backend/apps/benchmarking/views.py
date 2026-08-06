from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import BenchmarkMetric, SchoolBenchmark, BenchmarkComparison
from .serializers import (
    BenchmarkMetricSerializer, SchoolBenchmarkSerializer,
    BenchmarkComparisonSerializer
)
from .services.benchmarking_service import BenchmarkingService


class BenchmarkMetricViewSet(viewsets.ModelViewSet):
    queryset = BenchmarkMetric.objects.all()
    serializer_class = BenchmarkMetricSerializer
    permission_classes = [permissions.IsAdminUser]


class SchoolBenchmarkViewSet(viewsets.ModelViewSet):
    queryset = SchoolBenchmark.objects.all()
    serializer_class = SchoolBenchmarkSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['school', 'metric', 'period']

    @action(detail=False, methods=['post'], url_path='calculate')
    def calculate_metrics(self, request):
        school_id = request.data.get('school_id')
        period = request.data.get('period')
        if not school_id:
            return Response({'error': 'school_id required'}, status=status.HTTP_400_BAD_REQUEST)
        metrics = BenchmarkingService.calculate_school_metrics(school_id, period)
        return Response({'message': 'Metrics calculated', 'metrics': metrics})

    @action(detail=False, methods=['get'], url_path='rankings')
    def rankings(self, request):
        metric_code = request.query_params.get('metric_code', 'AVG_SCORE')
        period = request.query_params.get('period')
        rankings = BenchmarkingService.get_district_rankings(metric_code, period)
        return Response(rankings)

    @action(detail=False, methods=['get'], url_path='top')
    def top_performing(self, request):
        metric_code = request.query_params.get('metric_code', 'AVG_SCORE')
        limit = int(request.query_params.get('limit', 10))
        schools = BenchmarkingService.get_top_performing_schools(metric_code, limit)
        return Response(schools)

    @action(detail=False, methods=['get'], url_path='school-summary')
    def school_summary(self, request):
        school_id = request.query_params.get('school_id')
        if not school_id:
            return Response({'error': 'school_id required'}, status=status.HTTP_400_BAD_REQUEST)
        summary = BenchmarkingService.get_school_performance_summary(school_id)
        return Response(summary)


class BenchmarkComparisonViewSet(viewsets.ModelViewSet):
    queryset = BenchmarkComparison.objects.all()
    serializer_class = BenchmarkComparisonSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post']

    @action(detail=False, methods=['post'], url_path='compare')
    def compare_schools(self, request):
        school_a = request.data.get('school_a')
        school_b = request.data.get('school_b')
        metric_code = request.data.get('metric_code')
        if not school_a or not school_b:
            return Response({'error': 'school_a and school_b required'},
                          status=status.HTTP_400_BAD_REQUEST)
        comparisons = BenchmarkingService.compare_schools(school_a, school_b, metric_code)
        return Response(comparisons)
