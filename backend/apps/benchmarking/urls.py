from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BenchmarkMetricViewSet, SchoolBenchmarkViewSet, BenchmarkComparisonViewSet

router = DefaultRouter()
router.register('metrics', BenchmarkMetricViewSet)
router.register('benchmarks', SchoolBenchmarkViewSet)
router.register('comparisons', BenchmarkComparisonViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
