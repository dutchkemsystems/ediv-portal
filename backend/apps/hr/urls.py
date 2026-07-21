from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobPostingViewSet, JobApplicationViewSet, PayrollPeriodViewSet, PayslipViewSet

router = DefaultRouter()
router.register('job-postings', JobPostingViewSet)
router.register('applications', JobApplicationViewSet)
router.register('payroll-periods', PayrollPeriodViewSet)
router.register('payslips', PayslipViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
