from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FileViewSet, FileMovementViewSet, FileAttachmentViewSet, FileCommentViewSet,
    WorkflowConfigViewSet, FileTemplateViewSet, FileClassificationViewSet,
    OfflineQueueViewSet, FileSearchView, FileSearchSuggestionsView,
    FileImportView, FileExportView, FileBulkImportView,
    NotificationListView, NotificationReadView,
)

router = DefaultRouter()
router.register('files', FileViewSet)
router.register('movements', FileMovementViewSet)
router.register('attachments', FileAttachmentViewSet)
router.register('comments', FileCommentViewSet)
router.register('workflow-configs', WorkflowConfigViewSet)
router.register('templates', FileTemplateViewSet)
router.register('classifications', FileClassificationViewSet)
router.register('offline-queue', OfflineQueueViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('search/', FileSearchView.as_view(), name='file-search'),
    path('search/suggestions/', FileSearchSuggestionsView.as_view(), name='file-search-suggestions'),
    path('import/', FileImportView.as_view(), name='file-import'),
    path('export/', FileExportView.as_view(), name='file-export'),
    path('bulk-import/', FileBulkImportView.as_view(), name='file-bulk-import'),
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/read/', NotificationReadView.as_view(), name='notification-read'),
]
