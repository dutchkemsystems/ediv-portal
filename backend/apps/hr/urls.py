from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import JobApplicationViewSet, JobPostingViewSet, PayrollPeriodViewSet, PayslipViewSet

router = DefaultRouter()
router.register("job-postings", JobPostingViewSet)
router.register("applications", JobApplicationViewSet)
router.register("payroll-periods", PayrollPeriodViewSet)
router.register("payslips", PayslipViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
