from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, CorrespondenceViewSet, FilingViewSet, DocumentVersionViewSet

router = DefaultRouter()
router.register('documents', DocumentViewSet)
router.register('correspondence', CorrespondenceViewSet)
router.register('filings', FilingViewSet)
router.register('versions', DocumentVersionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
