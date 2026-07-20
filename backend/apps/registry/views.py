from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Document, Correspondence, Filing, DocumentVersion
from .serializers import (
    DocumentSerializer, DocumentListSerializer,
    CorrespondenceSerializer, FilingSerializer, DocumentVersionSerializer
)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.select_related('created_by', 'department').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['document_type', 'status', 'classification', 'department']
    search_fields = ['reference_number', 'title', 'content']
    ordering_fields = ['reference_number', 'created_at', 'effective_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DocumentListSerializer
        return DocumentSerializer


class CorrespondenceViewSet(viewsets.ModelViewSet):
    queryset = Correspondence.objects.select_related('document').all()
    serializer_class = CorrespondenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['direction', 'is_urgent', 'requires_response']
    search_fields = ['subject', 'sender', 'recipient']
    ordering_fields = ['date_received', 'created_at']


class FilingViewSet(viewsets.ModelViewSet):
    queryset = Filing.objects.select_related('document', 'filed_by').all()
    serializer_class = FilingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['document']
    search_fields = ['file_code', 'box_number']
    ordering_fields = ['filed_date']


class DocumentVersionViewSet(viewsets.ModelViewSet):
    queryset = DocumentVersion.objects.select_related('document', 'created_by').all()
    serializer_class = DocumentVersionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['document', 'version_number']
    ordering_fields = ['version_number', 'created_at']
