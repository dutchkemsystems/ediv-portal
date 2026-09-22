from datetime import date

from django.contrib.auth import get_user_model
from django.db import models as db_models
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from config.permissions import IsAdminOrTGOrDeptHead
from config.security import AuditLogger

from .models import (
    Correspondence,
    Document,
    DocumentVersion,
    Filing,
    MemoApproval,
    MemoCirculation,
    MemoWorkflow,
)
from .serializers import (
    CorrespondenceSerializer,
    DocumentListSerializer,
    DocumentSerializer,
    DocumentVersionSerializer,
    FilingSerializer,
    MemoApprovalSerializer,
    MemoCirculationSerializer,
    MemoWorkflowSerializer,
)
from .services.registry_service import (
    assign_document_to_workflow,
    create_follow_up,
    export_documents,
    record_document_audit,
)

User = get_user_model()


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.select_related("created_by", "department").all()
    from config.permissions import IsAdminOrTGOrDeptHead

    permission_classes = [IsAdminOrTGOrDeptHead]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["document_type", "status", "classification", "department"]
    search_fields = ["reference_number", "title", "content"]
    ordering_fields = ["reference_number", "created_at", "effective_date"]

    def get_serializer_class(self):
        if self.action == "list":
            return DocumentListSerializer
        return DocumentSerializer

    def perform_create(self, serializer):
        year = date.today().year
        doc_type = serializer.validated_data.get("document_type", "OTHER")
        dept_code = "GEN"
        if serializer.validated_data.get("department"):
            dept_code = serializer.validated_data["department"].code[:3]

        # Atomic sequence generation using shared utility
        prefix = f"EDIV/{year}/{dept_code}/"

        from config.sequence_utils import next_sequence_number

        seq = next_sequence_number(Document, prefix, field_name="reference_number")
        reference_number = f"EDIV/{year}/{dept_code}/{seq:04d}"

        doc = serializer.save(
            reference_number=reference_number,
            created_by=self.request.user,
        )

        record_document_audit(
            doc,
            "CREATE",
            user=self.request.user,
            details=f"Created by {self.request.user.get_full_name()}",
        )

        from config.security import AuditLogger

        AuditLogger.log_action(
            user=self.request.user,
            action="CREATE",
            resource_type="Document",
            resource_id=doc.id,
            description=f"Created document {reference_number}: {doc.title}",
            new_value={
                "reference_number": reference_number,
                "title": doc.title,
                "type": doc_type,
            },
        )

    def perform_update(self, serializer):
        doc = serializer.save()
        record_document_audit(
            doc,
            "UPDATE",
            user=self.request.user,
            details=f"Updated by {self.request.user.get_full_name()}",
        )

    @action(detail=True, methods=["get"], url_path="history")
    def document_history(self, request, pk=None):
        """Per-document audit trail (BE-005)."""
        doc = self.get_object()
        data = [
            {
                "action": e.action,
                "details": e.details,
                "user": e.user.get_full_name() if e.user else None,
                "timestamp": e.timestamp,
            }
            for e in doc.audit_entries.select_related("user")
        ]
        return Response({"document": doc.reference_number, "entries": data})

    @action(detail=True, methods=["get", "post"], url_path="follow-ups")
    def follow_ups(self, request, pk=None):
        """List (GET) or create (POST) follow-up records for a document (BE-005)."""
        doc = self.get_object()
        if request.method == "GET":
            data = [
                {
                    "id": f.id,
                    "assignee_id": f.assignee_id,
                    "assignee": f.assignee.get_full_name(),
                    "due_date": f.due_date,
                    "status": f.status,
                    "notes": f.notes,
                    "created_at": f.created_at,
                }
                for f in doc.follow_ups.select_related("assignee", "created_by")
            ]
            return Response({"follow_ups": data})

        assignee = User.objects.filter(id=request.data.get("assignee_id")).first()
        if assignee is None:
            return Response(
                {"error": "assignee_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        follow_up = create_follow_up(
            doc,
            assignee,
            request.user,
            due_date=request.data.get("due_date"),
            notes=request.data.get("notes", ""),
        )
        return Response(
            {"id": follow_up.id, "status": follow_up.status},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="assign")
    def assign_document(self, request, pk=None):
        """Hand off document to workflows automation; creates a workflow Task (BE-005)."""
        doc = self.get_object()
        result = assign_document_to_workflow(
            doc,
            action_required=request.data.get("action_required", "Process"),
            deadline=request.data.get("deadline"),
        )
        if result is None:
            return Response(
                {"error": "Assignment failed."}, status=status.HTTP_400_BAD_REQUEST
            )
        assignee = result.get("assignee")
        record_document_audit(
            doc,
            "ASSIGN",
            user=request.user,
            details=f"Assigned to {assignee.get_full_name() if assignee else 'unknown'}",
        )
        return Response(
            {
                "assigned": True,
                "assignee": assignee.email if assignee else None,
                "assignee_name": assignee.get_full_name() if assignee else None,
                "document_id": doc.id,
            }
        )

    @action(detail=False, methods=["get"], url_path="export")
    def export_index(self, request):
        """Export registry index (BE-005): csv (default), xlsx, or json."""
        fmt = request.query_params.get("format", "csv").lower()
        return export_documents(fmt)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve_document(self, request, pk=None):
        """Approve a document (TG/PS/Department Heads only)."""
        doc = self.get_object()
        user = request.user

        if user.role not in ("SYSADMIN", "TG_PS", "HR", "FIN", "AUDIT", "QA", "REG"):
            return Response(
                {"error": "You do not have permission to approve documents."},
                status=status.HTTP_403_FORBIDDEN,
            )

        doc.status = "APPROVED"
        doc.save(update_fields=["status", "updated_at"])

        from config.security import AuditLogger

        AuditLogger.log_action(
            user=user,
            action="APPROVE",
            resource_type="Document",
            resource_id=doc.id,
            description=f"Document {doc.reference_number} approved by {user.get_full_name()}",
        )

        return Response({"message": f"Document {doc.reference_number} approved."})

    @action(detail=True, methods=["post"], url_path="reject")
    def reject_document(self, request, pk=None):
        """Reject a document."""
        doc = self.get_object()
        user = request.user

        if user.role not in ("SYSADMIN", "TG_PS", "HR", "FIN", "AUDIT", "QA", "REG"):
            return Response(
                {"error": "You do not have permission to reject documents."},
                status=status.HTTP_403_FORBIDDEN,
            )

        reason = request.data.get("reason", "")
        doc.status = "REJECTED"
        doc.save(update_fields=["status", "updated_at"])

        from config.security import AuditLogger

        AuditLogger.log_action(
            user=user,
            action="REJECT",
            resource_type="Document",
            resource_id=doc.id,
            description=f"Document {doc.reference_number} rejected by {user.get_full_name()}: {reason}",
        )

        return Response({"message": f"Document {doc.reference_number} rejected."})


class CorrespondenceViewSet(viewsets.ModelViewSet):
    queryset = Correspondence.objects.select_related("document").all()
    serializer_class = CorrespondenceSerializer
    permission_classes = [IsAdminOrTGOrDeptHead]
    filterset_fields = ["direction", "is_urgent", "requires_response"]
    search_fields = ["subject", "sender", "recipient"]
    ordering_fields = ["date_received", "created_at"]

    def perform_create(self, serializer):
        corr = serializer.save()
        self._maybe_create_auto_task(corr)

    def perform_update(self, serializer):
        corr = serializer.save()
        self._maybe_create_auto_task(corr)

    def _maybe_create_auto_task(self, corr):
        """Extension Plan Feature B: creates a PENDING workflow Task when REGISTRY_AUTO_TASK is on."""
        from django.conf import settings as django_settings

        if not getattr(django_settings, "REGISTRY_AUTO_TASK", False):
            return
        from apps.workflows.automation import MailDistributor

        MailDistributor().assign_action(
            mail=corr.document, action_required="Auto task from correspondence"
        )


class FilingViewSet(viewsets.ModelViewSet):
    queryset = Filing.objects.select_related("document", "filed_by").all()
    serializer_class = FilingSerializer
    permission_classes = [IsAdminOrTGOrDeptHead]
    filterset_fields = ["document"]
    search_fields = ["file_code", "box_number"]
    ordering_fields = ["filed_date"]

    def perform_create(self, serializer):
        serializer.save(filed_by=self.request.user)


class DocumentVersionViewSet(viewsets.ModelViewSet):
    queryset = DocumentVersion.objects.select_related("document", "created_by").all()
    serializer_class = DocumentVersionSerializer
    permission_classes = [IsAdminOrTGOrDeptHead]
    filterset_fields = ["document", "version_number"]
    ordering_fields = ["version_number", "created_at"]

    def perform_create(self, serializer):
        doc = serializer.validated_data["document"]
        version_num = serializer.validated_data.get("version_number", doc.version + 1)

        serializer.save(created_by=self.request.user)

        doc.version = version_num
        doc.save(update_fields=["version"])


class MemoWorkflowViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        return MemoWorkflowSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ("SYSADMIN", "TG_PS"):
            return MemoWorkflow.objects.select_related(
                "document", "document__created_by"
            ).all()
        return (
            MemoWorkflow.objects.select_related("document", "document__created_by")
            .filter(
                db_models.Q(document__created_by=user)
                | db_models.Q(approvals__approver=user)
                | db_models.Q(circulations__recipient=user)
            )
            .distinct()
        )

    def perform_create(self, serializer):
        memo = serializer.save()

        AuditLogger.log_action(
            user=self.request.user,
            action="CREATE",
            resource_type="MemoWorkflow",
            resource_id=memo.id,
            description=f"Created {memo.workflow_type} workflow for {memo.document.reference_number}",
        )

    @action(detail=True, methods=["post"], url_path="submit")
    def submit_memo(self, request, pk=None):
        """Submit a draft memo for approval — transitions DRAFT to UNDER_APPROVAL."""
        memo = self.get_object()
        if memo.status != "DRAFT":
            return Response(
                {"error": "Only draft memos can be submitted"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        memo.status = "UNDER_APPROVAL"
        memo.save(update_fields=["status", "updated_at"])

        # Create approval record for TG_PS or SYSADMIN
        approvers = User.objects.filter(role__in=["SYSADMIN", "TG_PS"], is_active=True)[
            :1
        ]
        for approver in approvers:
            MemoApproval.objects.create(
                memo_workflow=memo,
                approver=approver,
                approval_order=1,
                status="PENDING",
            )

        AuditLogger.log_action(
            user=request.user,
            action="UPDATE",
            resource_type="MemoWorkflow",
            resource_id=memo.id,
            description=f"Submitted {memo.document.reference_number} for approval",
        )
        return Response({"status": "submitted"})

    @action(detail=True, methods=["post"], url_path="approve")
    def approve_memo(self, request, pk=None):
        memo = self.get_object()
        user = request.user
        comments = request.data.get("comments", "")

        if user.role not in ("SYSADMIN", "TG_PS", "PRI", "VP"):
            return Response(
                {"error": "No permission to approve."}, status=status.HTTP_403_FORBIDDEN
            )

        approval = MemoApproval.objects.filter(
            memo_workflow=memo, approver=user, status="PENDING"
        ).first()

        if not approval:
            return Response(
                {"error": "No pending approval found for you."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        approval.status = "APPROVED"
        approval.comments = comments
        approval.approved_date = timezone.now()
        approval.save(update_fields=["status", "comments", "approved_date"])

        pending_count = MemoApproval.objects.filter(
            memo_workflow=memo, status="PENDING"
        ).count()
        if pending_count == 0:
            memo.status = "CIRCULATING"
            memo.save(update_fields=["status", "updated_at"])

        AuditLogger.log_action(
            user=user,
            action="APPROVE",
            resource_type="MemoWorkflow",
            resource_id=memo.id,
            description=f"Approved {memo.document.reference_number}",
        )
        return Response(
            {"message": "Memo approved.", "remaining_approvals": pending_count}
        )

    @action(detail=True, methods=["post"], url_path="reject")
    def reject_memo(self, request, pk=None):
        memo = self.get_object()
        user = request.user
        comments = request.data.get("comments", "")

        if user.role not in ("SYSADMIN", "TG_PS", "PRI", "VP"):
            return Response(
                {"error": "No permission to reject."}, status=status.HTTP_403_FORBIDDEN
            )

        approval = MemoApproval.objects.filter(
            memo_workflow=memo, approver=user, status="PENDING"
        ).first()

        if not approval:
            return Response(
                {"error": "No pending approval found for you."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        approval.status = "REJECTED"
        approval.comments = comments
        approval.approved_date = timezone.now()
        approval.save(update_fields=["status", "comments", "approved_date"])

        memo.status = "DRAFT"
        memo.save(update_fields=["status", "updated_at"])

        AuditLogger.log_action(
            user=user,
            action="REJECT",
            resource_type="MemoWorkflow",
            resource_id=memo.id,
            description=f"Rejected {memo.document.reference_number}: {comments}",
        )
        return Response({"message": "Memo rejected."})

    @action(detail=True, methods=["post"], url_path="circulate")
    def circulate_memo(self, request, pk=None):
        memo = self.get_object()
        recipient_ids = request.data.get("recipient_ids", [])

        if memo.status != "CIRCULATING":
            return Response(
                {"error": f"Memo is {memo.status}, must be CIRCULATING."},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
            user=request.user,
            action="UPDATE",
            resource_type="MemoWorkflow",
            resource_id=memo.id,
            description=f"Circulated to {len(created)} recipients",
        )
        return Response(
            {
                "message": f"Circulated to {len(created)} recipients.",
                "recipients": created,
            }
        )

    @action(detail=True, methods=["post"], url_path="acknowledge")
    def acknowledge_memo(self, request, pk=None):
        memo = self.get_object()
        user = request.user
        notes = request.data.get("acknowledgement_notes", "")

        circ = MemoCirculation.objects.filter(
            memo_workflow=memo, recipient=user, status="SENT"
        ).first()

        if not circ:
            return Response(
                {"error": "No pending circulation for you."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        circ.status = "ACKNOWLEDGED"
        circ.date_acknowledged = timezone.now()
        circ.acknowledgement_notes = notes
        circ.save(
            update_fields=["status", "date_acknowledged", "acknowledgement_notes"]
        )

        all_acknowledged = not MemoCirculation.objects.filter(
            memo_workflow=memo, status="SENT"
        ).exists()

        if all_acknowledged:
            memo.status = "ACKNOWLEDGED"
            memo.save(update_fields=["status", "updated_at"])

        AuditLogger.log_action(
            user=user,
            action="UPDATE",
            resource_type="MemoWorkflow",
            resource_id=memo.id,
            description=f"Acknowledged {memo.document.reference_number}",
        )
        return Response(
            {"message": "Acknowledged.", "all_acknowledged": all_acknowledged}
        )

    @action(detail=True, methods=["post"], url_path="archive")
    def archive_memo(self, request, pk=None):
        memo = self.get_object()
        memo.status = "ARCHIVED"
        memo.save(update_fields=["status", "updated_at"])

        AuditLogger.log_action(
            user=request.user,
            action="UPDATE",
            resource_type="MemoWorkflow",
            resource_id=memo.id,
            description=f"Archived {memo.document.reference_number}",
        )
        return Response({"message": "Memo archived."})


class MemoApprovalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MemoApproval.objects.select_related("memo_workflow", "approver").all()
    serializer_class = MemoApprovalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["memo_workflow", "approver", "status"]
    ordering_fields = ["approval_order", "approved_date"]


class MemoCirculationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MemoCirculation.objects.select_related(
        "memo_workflow", "recipient"
    ).all()
    serializer_class = MemoCirculationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["memo_workflow", "recipient", "status"]
    ordering_fields = ["date_sent", "date_acknowledged"]
