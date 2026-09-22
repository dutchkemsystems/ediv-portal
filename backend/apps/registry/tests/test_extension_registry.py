"""Extension Plan Feature C tests: history, follow-ups, export, assign, auto-task."""

from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.registry.models import Document, DocumentAuditEntry
from apps.workflows.models import Task
from apps.workflows.services.workflow_service import WorkflowService

User = get_user_model()


class RegistryExtensionAPITest(APITestCase):
    """Registry history/follow-ups/export/assign actions and auto-task flag."""

    def setUp(self):
        self.admin = User.objects.create_user(
            email="reg-admin@ediv.gov.ng",
            password="AdminPass123!@#",
            first_name="Reg",
            last_name="Admin",
            role="SYSADMIN",
        )
        self.other = User.objects.create_user(
            email="reg-other@ediv.gov.ng",
            password="OtherPass123!@#",
            first_name="Reg",
            last_name="Other",
            role="REG",
        )
        WorkflowService.seed_all()
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(self.admin).access_token}"
        )

    def _create_document(
        self,
        title="Budget allocation report",
        content="Annual budget and finance allocation",
    ):
        return self.client.post(
            "/api/registry/documents/",
            {
                "title": title,
                "document_type": "REPORT",
                "content": content,
                "status": "DRAFT",
                "classification": "INTERNAL",
            },
            format="json",
        )

    def test_create_writes_audit_entry(self):
        resp = self._create_document()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        doc = Document.objects.get(id=resp.data["id"])
        self.assertTrue(doc.audit_entries.filter(action="CREATE").exists())

    def test_history_lists_audit_entries(self):
        resp = self._create_document()
        history = self.client.get(f"/api/registry/documents/{resp.data['id']}/history/")
        self.assertEqual(history.status_code, status.HTTP_200_OK)
        self.assertEqual(history.data["entries"][0]["action"], "CREATE")

    def test_update_writes_audit_entry(self):
        resp = self._create_document()
        upd = self.client.patch(
            f"/api/registry/documents/{resp.data['id']}/",
            {"status": "PENDING"},
            format="json",
        )
        self.assertEqual(upd.status_code, status.HTTP_200_OK)
        self.assertTrue(
            DocumentAuditEntry.objects.filter(
                document_id=resp.data["id"], action="UPDATE"
            ).exists()
        )

    def test_follow_up_create_and_list(self):
        resp = self._create_document()
        doc_id = resp.data["id"]
        created = self.client.post(
            f"/api/registry/documents/{doc_id}/follow-ups/",
            {"assignee_id": self.other.id, "notes": "Follow up on report"},
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED, created.data)
        listing = self.client.get(f"/api/registry/documents/{doc_id}/follow-ups/")
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.assertEqual(len(listing.data["follow_ups"]), 1)

    def test_follow_up_requires_assignee(self):
        resp = self._create_document()
        created = self.client.post(
            f"/api/registry/documents/{resp.data['id']}/follow-ups/",
            {"notes": "No assignee"},
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_400_BAD_REQUEST)

    def test_export_csv(self):
        self._create_document()
        response = self.client.get("/api/registry/documents/export/?format=csv")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("registry_export.csv", response["Content-Disposition"])

    def test_export_xlsx(self):
        self._create_document()
        response = self.client.get("/api/registry/documents/export/?format=xlsx")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_export_unsupported_format_400(self):
        response = self.client.get("/api/registry/documents/export/?format=pdf")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_creates_workflow_task(self):
        resp = self._create_document(
            "Incoming letter about school transfer", "Staff transfer request letter"
        )
        doc_id = resp.data["id"]
        assigned = self.client.post(
            f"/api/registry/documents/{doc_id}/assign/",
            {"action_required": "Process letter"},
            format="json",
        )
        self.assertEqual(assigned.status_code, status.HTTP_200_OK, assigned.data)
        self.assertTrue(
            Task.objects.filter(workflow_instance__data__document_id=doc_id).exists()
        )

    def test_registry_auto_task_flag_off_by_default(self):
        self._create_correspondence()
        self.assertEqual(Task.objects.count(), 0)

    @override_settings(REGISTRY_AUTO_TASK=True)
    def test_registry_auto_task_flag_on_creates_task(self):
        self._create_correspondence()
        self.assertEqual(Task.objects.count(), 1)

    def _create_correspondence(self):
        doc_resp = self.client.post(
            "/api/registry/documents/",
            {
                "title": "Staff leave request",
                "document_type": "CORRESPONDENCE",
                "content": "Staff leave and human resource request",
                "status": "PENDING",
                "classification": "INTERNAL",
            },
            format="json",
        )
        doc_id = doc_resp.data["id"]
        return self.client.post(
            "/api/registry/correspondence/",
            {
                "document": doc_id,
                "direction": "INCOMING",
                "sender": "Ministry of Education",
                "recipient": "Education District IV",
                "date_received": "2026-09-22",
                "subject": "Staff leave request",
            },
            format="json",
        )
