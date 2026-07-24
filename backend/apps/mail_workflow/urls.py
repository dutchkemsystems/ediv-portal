from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IncomingMailViewSet, MailAssignmentViewSet

router = DefaultRouter()
router.register('incoming-mail', IncomingMailViewSet, basename='incomingmail')
router.register('assignments', MailAssignmentViewSet, basename='mailassignment')

urlpatterns = [
    path('', include(router.urls)),
]
