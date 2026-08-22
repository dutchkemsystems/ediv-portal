from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.workflows.models import WorkflowInstance
from apps.workflows.services.workflow_service import WorkflowService

User = get_user_model()


class WorkflowAPIActionTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@ediv.gov.ng",
            password="AdminPass123!@#",
            first_name="Admin",
            last_name="User",
            role="SYSADMIN",
        )
        self.staff = User.objects.create_user(
            email="staff@ediv.gov.ng",
            password="StaffPass123!@#",
            first_name="Staff",
            last_name="Member",
            role="SA_OFF",
        )
        WorkflowService.seed_all()
        self.token = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token.access_token}")

    def test_start_action_creates_instance(self):
        response = self.client.post(
            "/api/workflows/instances/start/",
            {
                "workflow_type": "INTERNAL_MEMO",
                "reference_number": "MEMO-API-0001",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "IN_PROGRESS")
        self.assertEqual(response.data["reference_number"], "MEMO-API-0001")
        self.assertEqual(WorkflowInstance.objects.count(), 1)

    def test_start_action_requires_fields(self):
        response = self.client.post(
            "/api/workflows/instances/start/",
            {
                "workflow_type": "INTERNAL_MEMO",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_start_action_unknown_type(self):
        response = self.client.post(
            "/api/workflows/instances/start/",
            {
                "workflow_type": "NOPE",
                "reference_number": "MEMO-API-0002",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_advance_action_moves_to_next_step(self):
        instance = WorkflowService.start_instance(
            workflow_type="INTERNAL_MEMO",
            initiated_by=self.admin,
            reference_number="MEMO-API-0003",
        )
        first_task = instance.tasks.filter(status="PENDING").first()
        self.staff_token = RefreshToken.for_user(self.staff)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.staff_token.access_token}")

        first_order = instance.current_step.order
        response = self.client.post(
            f"/api/workflows/instances/{instance.id}/advance/",
            {
                "decision": "APPROVE",
                "comments": "Looks good",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "IN_PROGRESS")
        first_task.refresh_from_db()
        self.assertEqual(first_task.status, "COMPLETED")
        self.assertEqual(first_task.decision, "APPROVE")
        instance.refresh_from_db()
        self.assertGreater(instance.current_step.order, first_order)

    def test_advance_action_completes_workflow(self):
        instance = WorkflowService.start_instance(
            workflow_type="INTERNAL_MEMO",
            initiated_by=self.admin,
            reference_number="MEMO-API-0004",
        )
        for _ in range(instance.workflow.steps.count()):
            assignee = instance.tasks.filter(status="PENDING").first().assigned_to
            token = RefreshToken.for_user(assignee)
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
            response = self.client.post(
                f"/api/workflows/instances/{instance.id}/advance/",
                {"decision": "APPROVE"},
            )
            self.assertIn(response.status_code, (status.HTTP_200_OK,))
            instance.refresh_from_db()

        self.assertEqual(response.data["status"], "COMPLETED")
        instance.refresh_from_db()
        self.assertEqual(instance.status, "COMPLETED")
        self.assertIsNone(instance.current_step)
        self.assertEqual(instance.tasks.filter(status="COMPLETED").count(), instance.workflow.steps.count())

    def test_advance_action_rejects_wrong_user(self):
        instance = WorkflowService.start_instance(
            workflow_type="INTERNAL_MEMO",
            initiated_by=self.admin,
            reference_number="MEMO-API-0005",
        )
        other = User.objects.create_user(
            email="other@ediv.gov.ng",
            password="OtherPass123!@#",
            first_name="Other",
            last_name="User",
            role="REG_OFF",
        )
        other_token = RefreshToken.for_user(other)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {other_token.access_token}")
        response = self.client.post(
            f"/api/workflows/instances/{instance.id}/advance/",
            {
                "decision": "APPROVE",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
