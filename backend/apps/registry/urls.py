from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DocumentViewSet, CorrespondenceViewSet, FilingViewSet, DocumentVersionViewSet,
    MemoWorkflowViewSet, MemoApprovalViewSet, MemoCirculationViewSet
)

router = DefaultRouter()
router.register('documents', DocumentViewSet)
router.register('correspondence', CorrespondenceViewSet)
router.register('filings', FilingViewSet)
router.register('versions', DocumentVersionViewSet)
router.register('memos', MemoWorkflowViewSet, basename='memoworkflow')
router.register('memo-approvals', MemoApprovalViewSet, basename='memoapproval')
router.register('memo-circulations', MemoCirculationViewSet, basename='memocirculation')

urlpatterns = [
    path('', include(router.urls)),
]
