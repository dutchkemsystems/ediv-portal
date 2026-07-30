from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import IncomingMail, OutgoingMail, MailCorrespondence

User = get_user_model()


class IncomingMailModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='reg@test.com', password='TestPass123!',
            first_name='Registry', last_name='Officer', role='REG_OFF'
        )
        self.mail = IncomingMail.objects.create(
            mail_number='IM-2026-001', sender_name='Ministry of Education',
            subject='Annual Report Submission', date_received='2026-01-15',
            received_by=self.user
        )

    def test_mail_str(self):
        self.assertEqual(str(self.mail), 'IM-2026-001 - Annual Report Submission')


class OutgoingMailModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='reg@test.com', password='TestPass123!',
            first_name='Registry', last_name='Officer', role='REG_OFF'
        )
        self.mail = OutgoingMail.objects.create(
            mail_number='OM-2026-001', subject='Response to Ministry',
            recipient_name='Ministry of Education', created_by=self.user
        )

    def test_mail_str(self):
        self.assertEqual(str(self.mail), 'OM-2026-001 - Response to Ministry')


class MailCorrespondenceModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='reg@test.com', password='TestPass123!',
            first_name='Registry', last_name='Officer', role='REG_OFF'
        )
        self.correspondence = MailCorrespondence.objects.create(
            reference_number='MC-2026-001', correspondence_type='INTERNAL',
            subject='Staff Meeting Minutes', sender=self.user
        )

    def test_correspondence_str(self):
        self.assertEqual(str(self.correspondence), 'MC-2026-001 - Staff Meeting Minutes')


class MailWorkflowAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com', password='TestPass123!',
            first_name='Test', last_name='User', role='SYSADMIN'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

    def test_list_incoming_mail(self):
        response = self.client.get('/api/mail-workflow/incoming-mail/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_outgoing_mail(self):
        response = self.client.get('/api/mail-workflow/outgoing-mail/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_correspondences(self):
        response = self.client.get('/api/mail-workflow/correspondences/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
