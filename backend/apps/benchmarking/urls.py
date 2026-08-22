from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BenchmarkComparisonViewSet, BenchmarkMetricViewSet, SchoolBenchmarkViewSet

router = DefaultRouter()
router.register("metrics", BenchmarkMetricViewSet)
router.register("benchmarks", SchoolBenchmarkViewSet)
router.register("comparisons", BenchmarkComparisonViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
