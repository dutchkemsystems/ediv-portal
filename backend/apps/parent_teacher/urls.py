from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ParentTeacherMessageViewSet, PTAMeetingViewSet, StudentReportShareViewSet

router = DefaultRouter()
router.register("meetings", PTAMeetingViewSet)
router.register("messages", ParentTeacherMessageViewSet)
router.register("reports", StudentReportShareViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
