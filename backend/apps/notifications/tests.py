from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import NotificationTemplate, NotificationLog

User = get_user_model()


class NotificationTemplateModelTest(TestCase):
    def setUp(self):
        self.template = NotificationTemplate.objects.create(
            name='Welcome', subject='Welcome!',
            body='Hello {{name}}', channel='EMAIL'
        )

    def test_template_str(self):
        self.assertEqual(str(self.template), 'Welcome (EMAIL)')


class NotificationLogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com', password='TestPass123!',
            first_name='Test', last_name='User', role='TCH'
        )
        self.template = NotificationTemplate.objects.create(
            name='Alert', subject='Alert!', body='Alert body', channel='IN_APP'
        )
        self.log = NotificationLog.objects.create(
            template=self.template, recipient=self.user,
            channel='IN_APP', subject='Alert!', body='Alert body'
        )

    def test_log_str(self):
        self.assertIn('Alert!', str(self.log))


class NotificationAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com', password='TestPass123!',
            first_name='Test', last_name='User', role='SYSADMIN'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')
        self.template = NotificationTemplate.objects.create(
            name='Test', subject='Test', body='Body', channel='IN_APP'
        )

    def test_list_templates(self):
        response = self.client.get('/api/notifications/templates/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_template(self):
        response = self.client.post('/api/notifications/templates/', {
            'name': 'New', 'subject': 'New Subject', 'body': 'New Body', 'channel': 'EMAIL'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_logs(self):
        response = self.client.get('/api/notifications/logs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
