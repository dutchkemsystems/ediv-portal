from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    FileAttachmentViewSet,
    FileBulkActionView,
    FileBulkImportView,
    FileClassificationViewSet,
    FileCommentViewSet,
    FileDashboardView,
    FileExportView,
    FileImportFormatsView,
    FileImportView,
    FileMovementViewSet,
    FileSearchSuggestionsView,
    FileSearchView,
    FileTemplateViewSet,
    FileViewSet,
    NotificationListView,
    NotificationReadView,
    OCRView,
    OfflineQueueViewSet,
    OverdueFilesView,
    ReindexSearchView,
    WorkflowAdvanceView,
    WorkflowConfigViewSet,
    WorkflowDetailView,
    WorkflowMoveView,
    WorkflowVisualizationView,
)

router = DefaultRouter()
router.register("files", FileViewSet)
router.register("movements", FileMovementViewSet)
router.register("attachments", FileAttachmentViewSet)
router.register("comments", FileCommentViewSet)
router.register("workflow-configs", WorkflowConfigViewSet)
router.register("templates", FileTemplateViewSet)
router.register("classifications", FileClassificationViewSet)
router.register("offline-queue", OfflineQueueViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("search/", FileSearchView.as_view(), name="file-search"),
    path(
        "search/suggestions/",
        FileSearchSuggestionsView.as_view(),
        name="file-search-suggestions",
    ),
    path("import/", FileImportView.as_view(), name="file-import"),
    path(
        "import/formats/", FileImportFormatsView.as_view(), name="file-import-formats"
    ),
    path("export/", FileExportView.as_view(), name="file-export"),
    path("bulk-import/", FileBulkImportView.as_view(), name="file-bulk-import"),
    path("notifications/", NotificationListView.as_view(), name="notification-list"),
    path(
        "notifications/<int:pk>/read/",
        NotificationReadView.as_view(),
        name="notification-read",
    ),
    path("dashboard/", FileDashboardView.as_view(), name="file-dashboard"),
    path("bulk-action/", FileBulkActionView.as_view(), name="file-bulk-action"),
    path(
        "workflow/<int:pk>/", WorkflowVisualizationView.as_view(), name="file-workflow"
    ),
    path(
        "workflow/<int:pk>/advance/",
        WorkflowAdvanceView.as_view(),
        name="workflow-advance",
    ),
    path("workflow/<int:pk>/move/", WorkflowMoveView.as_view(), name="workflow-move"),
    path(
        "workflow/<int:pk>/detail/",
        WorkflowDetailView.as_view(),
        name="workflow-detail",
    ),
    path("overdue/", OverdueFilesView.as_view(), name="overdue-files"),
    path("reindex/", ReindexSearchView.as_view(), name="reindex-search"),
    path("ocr/", OCRView.as_view(), name="ocr-extract"),
]
