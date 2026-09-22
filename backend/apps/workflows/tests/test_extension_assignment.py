"""Extension Plan Feature B tests: assignment config, preview, and assign endpoints."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.registry.models import Document
from apps.workflows.models import Task, WorkflowInstance
from apps.workflows.services.workflow_service import WorkflowService

User = get_user_model()


class AutomationAssignmentAPITest(APITestCase):
    """Assignment endpoints are staff-only and drive the agentic distributors."""

    def setUp(self):
        self.admin = User.objects.create_user(
            email="assign-admin@ediv.gov.ng",
            password="AdminPass123!@#",
            first_name="Admin",
            last_name="Assign",
            role="SYSADMIN",
        )
        self.dept_head = User.objects.create_user(
            email="hr-head@ediv.gov.ng",
            password="HeadPass123!@#",
            first_name="HR",
            last_name="Head",
            role="HR",
        )
        self.staff = User.objects.create_user(
            email="assign-staff@ediv.gov.ng",
            password="StaffPass123!@#",
            first_name="Staff",
            last_name="Member",
            role="SA_OFF",
        )
        WorkflowService.seed_all()
        self.token = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token.access_token}")

    def _make_document(self):
        return Document.objects.create(
            reference_number="EDIV/2026/AUTOTEST/0001",
            title="Staff recruitment request",
            content="Human resource management request for recruitment and appointment",
            document_type="CORRESPONDENCE",
            created_by=self.admin,
            status="PENDING",
        )

    def test_config_requires_staff_role(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(self.staff).access_token}"
        )
        response = self.client.get("/api/workflows/assignment/config/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_config_lists_departments(self):
        response = self.client.get("/api/workflows/assignment/config/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("HR", response.data["departments"])

    def test_preview_persists_nothing(self):
        doc = self._make_document()
        before_instances = WorkflowInstance.objects.count()
        response = self.client.post(
            "/api/workflows/assignment/preview/", {"type": "mail", "id": doc.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["department_code"], "HR")
        self.assertEqual(WorkflowInstance.objects.count(), before_instances)
        self.assertEqual(Task.objects.count(), 0)

    def test_assign_creates_task(self):
        doc = self._make_document()
        response = self.client.post(
            "/api/workflows/assignment/assign/", {"type": "mail", "id": doc.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["assigned"])
        self.assertTrue(
            Task.objects.filter(workflow_instance__data__document_id=doc.id).exists()
        )

    def test_assign_missing_item_404(self):
        response = self.client.post(
            "/api/workflows/assignment/assign/", {"type": "file", "id": 999999}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
