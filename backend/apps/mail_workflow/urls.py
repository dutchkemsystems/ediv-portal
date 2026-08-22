from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IncomingMailViewSet,
    MailAssignmentViewSet,
    MailCorrespondenceMovementViewSet,
    MailCorrespondenceViewSet,
    MailMovementViewSet,
    OutgoingMailMovementViewSet,
    OutgoingMailViewSet,
    SchoolHQCorrespondenceMovementViewSet,
    SchoolHQCorrespondenceViewSet,
)

router = DefaultRouter()
router.register("incoming-mail", IncomingMailViewSet, basename="incomingmail")
router.register("assignments", MailAssignmentViewSet, basename="mailassignment")
router.register("incoming-movements", MailMovementViewSet, basename="mailmovement")
router.register("outgoing-mail", OutgoingMailViewSet, basename="outgoingmail")
router.register("outgoing-movements", OutgoingMailMovementViewSet, basename="outgoingmailmovement")
router.register("school-hq", SchoolHQCorrespondenceViewSet, basename="schoolhq")
router.register("school-hq-movements", SchoolHQCorrespondenceMovementViewSet, basename="schoolhqmovement")
router.register("correspondences", MailCorrespondenceViewSet, basename="mailcorrespondence")
router.register("correspondence-movements", MailCorrespondenceMovementViewSet, basename="mailcorrespondencemovement")

urlpatterns = [
    path("", include(router.urls)),
]
