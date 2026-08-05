from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FileViewSet, FileMovementViewSet, FileAttachmentViewSet, FileCommentViewSet,
    WorkflowConfigViewSet, FileTemplateViewSet, FileClassificationViewSet,
    OfflineQueueViewSet, FileSearchView, FileSearchSuggestionsView,
    FileImportView, FileExportView, FileBulkImportView,
    NotificationListView, NotificationReadView,
    FileDashboardView, FileBulkActionView, WorkflowVisualizationView,
    WorkflowAdvanceView, WorkflowMoveView, WorkflowDetailView,
    OverdueFilesView, ReindexSearchView,
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
    path('dashboard/', FileDashboardView.as_view(), name='file-dashboard'),
    path('bulk-action/', FileBulkActionView.as_view(), name='file-bulk-action'),
    path('workflow/<int:pk>/', WorkflowVisualizationView.as_view(), name='file-workflow'),
    path('workflow/<int:pk>/advance/', WorkflowAdvanceView.as_view(), name='workflow-advance'),
    path('workflow/<int:pk>/move/', WorkflowMoveView.as_view(), name='workflow-move'),
    path('workflow/<int:pk>/detail/', WorkflowDetailView.as_view(), name='workflow-detail'),
    path('overdue/', OverdueFilesView.as_view(), name='overdue-files'),
    path('reindex/', ReindexSearchView.as_view(), name='reindex-search'),
]
