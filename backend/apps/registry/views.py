from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models as db_models
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
import datetime as dt

from config.security import AuditLogger
from .models import (
    Document, Correspondence, Filing, DocumentVersion,
    MemoWorkflow, MemoApproval, MemoCirculation
)
from .serializers import (
    DocumentSerializer, DocumentListSerializer,
    CorrespondenceSerializer, FilingSerializer, DocumentVersionSerializer,
    MemoWorkflowSerializer, MemoApprovalSerializer, MemoCirculationSerializer
)

User = get_user_model()


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


class MemoWorkflowViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        return MemoWorkflowSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ('SYSADMIN', 'TG', 'PS'):
            return MemoWorkflow.objects.select_related('document', 'document__created_by').all()
        return MemoWorkflow.objects.select_related('document', 'document__created_by').filter(
            db_models.Q(document__created_by=user) |
            db_models.Q(approvals__approver=user) |
            db_models.Q(circulations__recipient=user)
        ).distinct()

    def perform_create(self, serializer):
        memo = serializer.save()

        AuditLogger.log_action(
            user=self.request.user, action='CREATE', resource_type='MemoWorkflow',
            resource_id=memo.id, description=f"Created {memo.workflow_type} workflow for {memo.document.reference_number}",
        )

    @action(detail=True, methods=['post'], url_path='approve')
    def approve_memo(self, request, pk=None):
        memo = self.get_object()
        user = request.user
        comments = request.data.get('comments', '')

        if user.role not in ('SYSADMIN', 'TG', 'PS', 'PRI', 'VP'):
            return Response({'error': 'No permission to approve.'}, status=status.HTTP_403_FORBIDDEN)

        approval = MemoApproval.objects.filter(
            memo_workflow=memo, approver=user, status='PENDING'
        ).first()

        if not approval:
            return Response({'error': 'No pending approval found for you.'}, status=status.HTTP_400_BAD_REQUEST)

        approval.status = 'APPROVED'
        approval.comments = comments
        approval.approved_date = dt.datetime.now()
        approval.save(update_fields=['status', 'comments', 'approved_date'])

        pending_count = MemoApproval.objects.filter(memo_workflow=memo, status='PENDING').count()
        if pending_count == 0:
            memo.status = 'CIRCULATING'
            memo.save(update_fields=['status', 'updated_at'])

        AuditLogger.log_action(
            user=user, action='APPROVE', resource_type='MemoWorkflow',
            resource_id=memo.id, description=f"Approved {memo.document.reference_number}",
        )
        return Response({'message': 'Memo approved.', 'remaining_approvals': pending_count})

    @action(detail=True, methods=['post'], url_path='reject')
    def reject_memo(self, request, pk=None):
        memo = self.get_object()
        user = request.user
        comments = request.data.get('comments', '')

        if user.role not in ('SYSADMIN', 'TG', 'PS', 'PRI', 'VP'):
            return Response({'error': 'No permission to reject.'}, status=status.HTTP_403_FORBIDDEN)

        approval = MemoApproval.objects.filter(
            memo_workflow=memo, approver=user, status='PENDING'
        ).first()

        if not approval:
            return Response({'error': 'No pending approval found for you.'}, status=status.HTTP_400_BAD_REQUEST)

        approval.status = 'REJECTED'
        approval.comments = comments
        approval.approved_date = dt.datetime.now()
        approval.save(update_fields=['status', 'comments', 'approved_date'])

        memo.status = 'DRAFT'
        memo.save(update_fields=['status', 'updated_at'])

        AuditLogger.log_action(
            user=user, action='REJECT', resource_type='MemoWorkflow',
            resource_id=memo.id, description=f"Rejected {memo.document.reference_number}: {comments}",
        )
        return Response({'message': 'Memo rejected.'})

    @action(detail=True, methods=['post'], url_path='circulate')
    def circulate_memo(self, request, pk=None):
        memo = self.get_object()
        recipient_ids = request.data.get('recipient_ids', [])

        if memo.status != 'CIRCULATING':
            return Response({'error': f'Memo is {memo.status}, must be CIRCULATING.'}, status=status.HTTP_400_BAD_REQUEST)

        created = []
        for rid in recipient_ids:
            try:
                recipient = User.objects.get(id=rid)
                circ, _ = MemoCirculation.objects.get_or_create(
                    memo_workflow=memo, recipient=recipient
                )
                created.append(recipient.get_full_name())
            except User.DoesNotExist:
                continue

        AuditLogger.log_action(
            user=request.user, action='UPDATE', resource_type='MemoWorkflow',
            resource_id=memo.id, description=f"Circulated to {len(created)} recipients",
        )
        return Response({'message': f'Circulated to {len(created)} recipients.', 'recipients': created})

    @action(detail=True, methods=['post'], url_path='acknowledge')
    def acknowledge_memo(self, request, pk=None):
        memo = self.get_object()
        user = request.user
        notes = request.data.get('acknowledgement_notes', '')

        circ = MemoCirculation.objects.filter(
            memo_workflow=memo, recipient=user, status='SENT'
        ).first()

        if not circ:
            return Response({'error': 'No pending circulation for you.'}, status=status.HTTP_400_BAD_REQUEST)

        circ.status = 'ACKNOWLEDGED'
        circ.date_acknowledged = dt.datetime.now()
        circ.acknowledgement_notes = notes
        circ.save(update_fields=['status', 'date_acknowledged', 'acknowledgement_notes'])

        all_acknowledged = not MemoCirculation.objects.filter(
            memo_workflow=memo, status='SENT'
        ).exists()

        if all_acknowledged:
            memo.status = 'ACKNOWLEDGED'
            memo.save(update_fields=['status', 'updated_at'])

        AuditLogger.log_action(
            user=user, action='UPDATE', resource_type='MemoWorkflow',
            resource_id=memo.id, description=f"Acknowledged {memo.document.reference_number}",
        )
        return Response({'message': 'Acknowledged.', 'all_acknowledged': all_acknowledged})

    @action(detail=True, methods=['post'], url_path='archive')
    def archive_memo(self, request, pk=None):
        memo = self.get_object()
        memo.status = 'ARCHIVED'
        memo.save(update_fields=['status', 'updated_at'])

        AuditLogger.log_action(
            user=request.user, action='UPDATE', resource_type='MemoWorkflow',
            resource_id=memo.id, description=f"Archived {memo.document.reference_number}",
        )
        return Response({'message': 'Memo archived.'})
