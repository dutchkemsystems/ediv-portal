from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import User
from .models import Message, UserNotification, Circular


class MessageModelTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            email='sender@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Sender',
            last_name='User',
            role='SYSADMIN'
        )
        self.receiver = User.objects.create_user(
            email='receiver@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Receiver',
            last_name='User',
            role='TCH'
        )
        self.message = Message.objects.create(
            sender=self.sender,
            subject='Test Message',
            body='This is a test message',
            message_type='INTERNAL',
            priority='NORMAL'
        )
        self.message.recipients.add(self.receiver)
    
    def test_message_str(self):
        self.assertEqual(str(self.message), 'Test Message - Sender User')


class NotificationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Test',
            last_name='User',
            role='TCH'
        )
        self.notification = UserNotification.objects.create(
            user=self.user,
            title='Test Notification',
            message='This is a test notification',
            notification_type='INFO'
        )
    
    def test_notification_str(self):
        self.assertEqual(str(self.notification), 'Test Notification - Test User')


class CommunicationAPITest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin@ediv.gov.ng',
            password='AdminPass123!@#',
            first_name='Admin',
            last_name='User',
            role='SYSADMIN'
        )
        self.token = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')
    
    def test_list_messages(self):
        response = self.client.get('/api/communication/messages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_notifications(self):
        response = self.client.get('/api/communication/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_circulars(self):
        response = self.client.get('/api/communication/circulars/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
