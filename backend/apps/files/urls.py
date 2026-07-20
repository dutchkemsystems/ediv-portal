from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FileViewSet, FileMovementViewSet, FileAttachmentViewSet, FileCommentViewSet

router = DefaultRouter()
router.register('files', FileViewSet)
router.register('movements', FileMovementViewSet)
router.register('attachments', FileAttachmentViewSet)
router.register('comments', FileCommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
