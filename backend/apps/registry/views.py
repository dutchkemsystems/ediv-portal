from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
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

    def perform_create(self, serializer):
        import datetime
        year = datetime.date.today().year
        doc_type = serializer.validated_data.get('document_type', 'OTHER')
        dept_code = 'GEN'
        if serializer.validated_data.get('department'):
            dept_code = serializer.validated_data['department'].code[:3]

        seq = Document.objects.filter(
            reference_number__startswith=f'EDIV/{year}/{dept_code}'
        ).count() + 1
        reference_number = f'EDIV/{year}/{dept_code}/{seq:04d}'

        doc = serializer.save(
            reference_number=reference_number,
            created_by=self.request.user,
        )

        from config.security import AuditLogger
        AuditLogger.log_action(
            user=self.request.user,
            action='CREATE',
            resource_type='Document',
            resource_id=doc.id,
            description=f"Created document {reference_number}: {doc.title}",
            new_value={'reference_number': reference_number, 'title': doc.title, 'type': doc_type},
        )

    @action(detail=True, methods=['post'], url_path='approve')
    def approve_document(self, request, pk=None):
        """Approve a document (TG/PS/Department Heads only)."""
        doc = self.get_object()
        user = request.user

        if user.role not in ('SYSADMIN', 'TG', 'PS', 'HR', 'FIN', 'AUDIT', 'QA', 'REG'):
            return Response(
                {'error': 'You do not have permission to approve documents.'},
                status=status.HTTP_403_FORBIDDEN
            )

        doc.status = 'APPROVED'
        doc.save(update_fields=['status', 'updated_at'])

        from config.security import AuditLogger
        AuditLogger.log_action(
            user=user,
            action='APPROVE',
            resource_type='Document',
            resource_id=doc.id,
            description=f"Document {doc.reference_number} approved by {user.get_full_name()}",
        )

        return Response({'message': f"Document {doc.reference_number} approved."})

    @action(detail=True, methods=['post'], url_path='reject')
    def reject_document(self, request, pk=None):
        """Reject a document."""
        doc = self.get_object()
        user = request.user

        if user.role not in ('SYSADMIN', 'TG', 'PS', 'HR', 'FIN', 'AUDIT', 'QA', 'REG'):
            return Response(
                {'error': 'You do not have permission to reject documents.'},
                status=status.HTTP_403_FORBIDDEN
            )

        reason = request.data.get('reason', '')
        doc.status = 'REJECTED'
        doc.save(update_fields=['status', 'updated_at'])

        from config.security import AuditLogger
        AuditLogger.log_action(
            user=user,
            action='REJECT',
            resource_type='Document',
            resource_id=doc.id,
            description=f"Document {doc.reference_number} rejected by {user.get_full_name()}: {reason}",
        )

        return Response({'message': f"Document {doc.reference_number} rejected."})


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

    def perform_create(self, serializer):
        serializer.save(filed_by=self.request.user)


class DocumentVersionViewSet(viewsets.ModelViewSet):
    queryset = DocumentVersion.objects.select_related('document', 'created_by').all()
    serializer_class = DocumentVersionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['document', 'version_number']
    ordering_fields = ['version_number', 'created_at']

    def perform_create(self, serializer):
        doc = serializer.validated_data['document']
        version_num = serializer.validated_data.get('version_number', doc.version + 1)

        serializer.save(created_by=self.request.user)

        doc.version = version_num
        doc.save(update_fields=['version'])
