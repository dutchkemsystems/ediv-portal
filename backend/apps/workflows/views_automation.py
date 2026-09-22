"""Extension Plan Feature B: manual routing / preview endpoints (staff-only, flag-gated).

All three endpoints are read/action endpoints for admins, TG, and department heads.
Preview persists nothing; assign creates a workflow Task via the existing distributors.
"""

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from config.permissions import IsAdminOrTGOrDeptHead

from apps.files.models import File
from apps.registry.models import Document

from apps.workflows.automation import (
    DEPARTMENT_CODES,
    DEPARTMENT_KEYWORDS,
    AgenticRouter,
    FileDistributor,
    MailDistributor,
)

User = get_user_model()


def _load_item(item_type, item_id):
    if item_type == "file":
        return "file", File.objects.filter(id=item_id).first()
    if item_type in ("mail", "document"):
        return "mail", Document.objects.filter(id=item_id).first()
    return None, None


def _analysis_text(kind, obj):
    if kind == "file":
        return " ".join(
            filter(
                None, [obj.title or "", obj.description or "", " ".join(obj.tags or [])]
            )
        )
    return " ".join(filter(None, [obj.title or "", obj.content or ""]))


class AssignmentConfigView(APIView):
    """Read-only routing config: department -> name + keywords + head|role (BE-004)."""

    permission_classes = [IsAdminOrTGOrDeptHead]

    def get(self, request):
        router = AgenticRouter()
        config = {}
        for dept_code, keywords in DEPARTMENT_KEYWORDS.items():
            head = router.get_department_head(dept_code)
            config[dept_code] = {
                "department_name": DEPARTMENT_CODES.get(dept_code, dept_code),
                "keywords": keywords,
                "head_role": head.role if head else None,
                "head_email": head.email if head else None,
            }
        return Response({"departments": config})


class AssignmentPreviewView(APIView):
    """Preview routing for an item WITHOUT persisting anything (BE-004)."""

    permission_classes = [IsAdminOrTGOrDeptHead]

    def post(self, request):
        item_type = request.data.get("type", "")
        item_id = request.data.get("id")
        if item_id is None or item_type not in ("file", "mail", "document"):
            return Response(
                {"error": "type (file|mail) and id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        kind, obj = _load_item(item_type, item_id)
        if obj is None:
            return Response(
                {"error": "Item not found."}, status=status.HTTP_404_NOT_FOUND
            )

        router = AgenticRouter()
        dept_code = router.determine_department(_analysis_text(kind, obj))
        dept_head = router.get_department_head(dept_code)
        return Response(
            {
                "department_code": dept_code,
                "department_name": DEPARTMENT_CODES.get(dept_code, "Registry"),
                "assignee": dept_head.email if dept_head else None,
                "assignee_name": dept_head.get_full_name() if dept_head else None,
                "keywords_used": DEPARTMENT_KEYWORDS.get(dept_code, []),
            }
        )


class AssignmentAssignView(APIView):
    """Assign item to the routed department head; creates workflow Task(s) (BE-004)."""

    permission_classes = [IsAdminOrTGOrDeptHead]

    def post(self, request):
        item_type = request.data.get("type", "")
        item_id = request.data.get("id")
        action_required = request.data.get("action_required", "Process item")
        deadline = request.data.get("deadline")
        if item_id is None or item_type not in ("file", "mail", "document"):
            return Response(
                {"error": "type (file|mail) and id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        kind, obj = _load_item(item_type, item_id)
        if obj is None:
            return Response(
                {"error": "Item not found."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            if kind == "file":
                result = FileDistributor().distribute(obj)
            else:
                result = MailDistributor().assign_action(
                    mail=obj,
                    action_required=action_required,
                    deadline=deadline,
                )
        except Exception as exc:
            return Response(
                {"error": f"Assignment failed: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        assignee = (result or {}).get("assignee")
        doc = (result or {}).get("document")
        return Response(
            {
                "assigned": result is not None,
                "assignee": assignee.email if assignee else None,
                "assignee_name": assignee.get_full_name() if assignee else None,
                "document_id": doc.id if doc else None,
            }
        )
