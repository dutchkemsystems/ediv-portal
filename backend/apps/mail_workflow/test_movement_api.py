import datetime

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.mail_workflow.models import (
    IncomingMail,
    MailCorrespondence,
    MailCorrespondenceMovement,
    MailMovement,
    OutgoingMail,
    OutgoingMailMovement,
)

User = get_user_model()


class MailMovementAPITest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@ediv.gov.ng",
            password="AdminPass123!@#",
            first_name="Admin",
            last_name="User",
            role="SYSADMIN",
        )
        self.officer = User.objects.create_user(
            email="officer@ediv.gov.ng",
            password="OfficerPass123!@#",
            first_name="Reg",
            last_name="Officer",
            role="REG_OFF",
        )
        self.other = User.objects.create_user(
            email="other@ediv.gov.ng",
            password="OtherPass123!@#",
            first_name="Other",
            last_name="User",
            role="SA_OFF",
        )
        self.incoming = IncomingMail.objects.create(
            mail_number="EDIV/MAIL/2026/0001",
            sender_name="Ministry of Education",
            subject="Annual Report Submission",
            date_received=datetime.date(2026, 1, 15),
            received_by=self.admin,
        )
        self.outgoing = OutgoingMail.objects.create(
            mail_number="EDIV/OUT/2026/0001",
            subject="Response to Ministry",
            recipient_name="Ministry of Education",
            created_by=self.admin,
        )
        self.correspondence = MailCorrespondence.objects.create(
            reference_number="EDIV/CORR/INT/2026/0001",
            correspondence_type="INTERNAL",
            subject="Staff Meeting Minutes",
            sender=self.admin,
        )
        self.token = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token.access_token}")

    def test_incoming_forward_creates_movement(self):
        response = self.client.post(
            f"/api/mail-workflow/incoming-mail/{self.incoming.id}/forward/",
            {"to_person_id": self.officer.id, "action": "Forwarded", "remarks": "Please review"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(MailMovement.objects.filter(mail=self.incoming).count(), 1)

    def test_incoming_movements_list_endpoint(self):
        MailMovement.objects.create(
            mail=self.incoming,
            from_person=self.admin,
            to_person=self.officer,
            action="Forwarded",
            remarks="Please review",
        )
        response = self.client.get("/api/mail-workflow/incoming-movements/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["action"], "Forwarded")
        self.assertEqual(response.data["results"][0]["to_person_name"], "Reg Officer")

        filtered = self.client.get(f"/api/mail-workflow/incoming-movements/?mail={self.incoming.id}")
        self.assertEqual(filtered.data["count"], 1)
        filtered = self.client.get("/api/mail-workflow/incoming-movements/?action=Dispatch")
        self.assertEqual(filtered.data["count"], 0)

    def test_outgoing_movements_list_endpoint(self):
        OutgoingMailMovement.objects.create(
            outgoing_mail=self.outgoing,
            from_person=self.admin,
            to_person=None,
            action="Dispatched",
            remarks="Sent via courier",
        )
        response = self.client.get("/api/mail-workflow/outgoing-movements/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["action"], "Dispatched")

    def test_correspondence_movements_list_endpoint(self):
        MailCorrespondenceMovement.objects.create(
            correspondence=self.correspondence,
            from_person=self.admin,
            to_person=self.officer,
            action="Routed",
        )
        response = self.client.get("/api/mail-workflow/correspondence-movements/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["action"], "Routed")

    def test_movements_are_role_scoped(self):
        MailMovement.objects.create(
            mail=self.incoming,
            from_person=self.admin,
            to_person=self.officer,
            action="Forwarded",
        )
        other_token = RefreshToken.for_user(self.other)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {other_token.access_token}")
        response = self.client.get("/api/mail-workflow/incoming-movements/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

        officer_token = RefreshToken.for_user(self.officer)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {officer_token.access_token}")
        response = self.client.get("/api/mail-workflow/incoming-movements/")
        self.assertEqual(response.data["count"], 1)

    def test_movement_write_is_not_allowed(self):
        response = self.client.post(
            "/api/mail-workflow/incoming-movements/",
            {
                "mail": self.incoming.id,
                "from_person": self.admin.id,
                "to_person": self.officer.id,
                "action": "Forwarded",
            },
        )
        self.assertIn(response.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_405_METHOD_NOT_ALLOWED))
