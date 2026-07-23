from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PTAMeetingViewSet, ParentTeacherMessageViewSet, StudentReportShareViewSet

router = DefaultRouter()
router.register('meetings', PTAMeetingViewSet)
router.register('messages', ParentTeacherMessageViewSet)
router.register('reports', StudentReportShareViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
