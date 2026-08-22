from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.registry.models import Document, MemoApproval, MemoCirculation, MemoWorkflow

User = get_user_model()


class MemoWorkflowAPITest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@ediv.gov.ng",
            password="AdminPass123!@#",
            first_name="Admin",
            last_name="User",
            role="SYSADMIN",
        )
        self.tg = User.objects.create_user(
            email="tg@ediv.gov.ng",
            password="TgPass123!@#",
            first_name="Tutor",
            last_name="General",
            role="TG_PS",
        )
        self.staff = User.objects.create_user(
            email="staff@ediv.gov.ng",
            password="StaffPass123!@#",
            first_name="Staff",
            last_name="Member",
            role="SA_OFF",
        )
        self.recipient = User.objects.create_user(
            email="recipient@ediv.gov.ng",
            password="RecipPass123!@#",
            first_name="Recipient",
            last_name="Person",
            role="REG_OFF",
        )

        self.document = Document.objects.create(
            reference_number="EDIV/2026/GEN/0001",
            title="Monthly Staff Meeting Memo",
            document_type="MEMO",
            content="Meeting scheduled.",
            created_by=self.staff,
        )
        self.memo = MemoWorkflow.objects.create(
            document=self.document,
            workflow_type="MEMO",
            status="DRAFT",
        )

    def _auth(self, user):
        token = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")

    def test_memo_full_flow(self):
        self._auth(self.staff)

        response = self.client.post(f"/api/registry/memos/{self.memo.id}/submit/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.memo.refresh_from_db()
        self.assertEqual(self.memo.status, "UNDER_APPROVAL")
        self.assertEqual(MemoApproval.objects.filter(memo_workflow=self.memo).count(), 1)

        approver = MemoApproval.objects.get(memo_workflow=self.memo).approver
        self._auth(approver)
        response = self.client.post(
            f"/api/registry/memos/{self.memo.id}/approve/",
            {"comments": "Approved"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.memo.refresh_from_db()
        self.assertEqual(self.memo.status, "CIRCULATING")

        response = self.client.post(
            f"/api/registry/memos/{self.memo.id}/circulate/",
            {"recipient_ids": [self.recipient.id]},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            MemoCirculation.objects.filter(memo_workflow=self.memo, recipient=self.recipient, status="SENT").count(), 1
        )

        self._auth(self.recipient)
        response = self.client.post(
            f"/api/registry/memos/{self.memo.id}/acknowledge/",
            {"acknowledgement_notes": "Received"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.memo.refresh_from_db()
        self.assertEqual(self.memo.status, "ACKNOWLEDGED")

        response = self.client.post(f"/api/registry/memos/{self.memo.id}/archive/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.memo.refresh_from_db()
        self.assertEqual(self.memo.status, "ARCHIVED")

    def test_memo_approval_rejection_returns_to_draft(self):
        self._auth(self.staff)
        self.client.post(f"/api/registry/memos/{self.memo.id}/submit/")
        approver = MemoApproval.objects.get(memo_workflow=self.memo).approver
        self._auth(approver)
        response = self.client.post(
            f"/api/registry/memos/{self.memo.id}/reject/",
            {"comments": "Needs work"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.memo.refresh_from_db()
        self.assertEqual(self.memo.status, "DRAFT")

    def test_memo_approval_list_endpoint(self):
        self._auth(self.staff)
        self.client.post(f"/api/registry/memos/{self.memo.id}/submit/")
        approval = MemoApproval.objects.get(memo_workflow=self.memo)
        response = self.client.get("/api/registry/memo-approvals/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], approval.id)

        filtered = self.client.get("/api/registry/memo-approvals/?status=PENDING")
        self.assertEqual(filtered.data["count"], 1)
        filtered = self.client.get("/api/registry/memo-approvals/?status=APPROVED")
        self.assertEqual(filtered.data["count"], 0)

    def test_memo_circulation_list_endpoint(self):
        self._auth(self.staff)
        self.client.post(f"/api/registry/memos/{self.memo.id}/submit/")
        approver = MemoApproval.objects.get(memo_workflow=self.memo).approver
        self._auth(approver)
        self.client.post(f"/api/registry/memos/{self.memo.id}/approve/")
        self.client.post(
            f"/api/registry/memos/{self.memo.id}/circulate/",
            {"recipient_ids": [self.recipient.id]},
        )
        circulation = MemoCirculation.objects.get(memo_workflow=self.memo)
        response = self.client.get("/api/registry/memo-circulations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], circulation.id)
