from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    IncomingMailViewSet, MailAssignmentViewSet,
    OutgoingMailViewSet, SchoolHQCorrespondenceViewSet, MailCorrespondenceViewSet
)

router = DefaultRouter()
router.register('incoming-mail', IncomingMailViewSet, basename='incomingmail')
router.register('assignments', MailAssignmentViewSet, basename='mailassignment')
router.register('outgoing-mail', OutgoingMailViewSet, basename='outgoingmail')
router.register('school-hq', SchoolHQCorrespondenceViewSet, basename='schoolhq')
router.register('correspondences', MailCorrespondenceViewSet, basename='mailcorrespondence')

urlpatterns = [
    path('', include(router.urls)),
]
