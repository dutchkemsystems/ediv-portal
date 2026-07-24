from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import User
from apps.schools.models import School
from .models import File, FileMovement, FileAttachment


class FileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Test',
            last_name='User',
            role='SYSADMIN'
        )
        self.file = File.objects.create(
            file_number='EDIV-2024-REG-001',
            title='Test Correspondence',
            file_type='CORRESPONDENCE',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
            classification='INTERNAL',
            priority='NORMAL'
        )

    def test_file_str(self):
        self.assertEqual(str(self.file), 'EDIV-2024-REG-001 - Test Correspondence')


class FilesAPITest(APITestCase):
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

        self.file = File.objects.create(
            file_number='EDIV-2024-REG-001',
            title='Test Correspondence',
            file_type='CORRESPONDENCE',
            created_by=self.admin,
            current_holder=self.admin,
            status='ACTIVE'
        )

    def test_list_files(self):
        response = self.client.get('/api/files/files/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_file(self):
        response = self.client.get(f'/api/files/files/{self.file.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_file(self):
        data = {
            'title': 'New Memo',
            'file_type': 'MEMO',
            'status': 'ACTIVE',
            'classification': 'INTERNAL',
            'priority': 'HIGH'
        }
        response = self.client.post('/api/files/files/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Verify auto-generated file number
        self.assertTrue(response.data['file_number'].startswith('EDIV-'))

    def test_auto_sets_created_by(self):
        data = {
            'title': 'Auto Created By',
            'file_type': 'MEMO',
        }
        response = self.client.post('/api/files/files/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['created_by'], self.admin.id)


class MoveFileTest(APITestCase):
    """Tests for POST /api/files/files/{id}/move/"""

    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin@ediv.gov.ng',
            password='AdminPass123!@#',
            first_name='Admin',
            last_name='User',
            role='SYSADMIN'
        )
        self.receiver = User.objects.create_user(
            email='receiver@ediv.gov.ng',
            password='ReceiverPass123!@#',
            first_name='Receiver',
            last_name='User',
            role='TCH'
        )
        self.file = File.objects.create(
            file_number='EDIV-2024-REG-001',
            title='Test File',
            file_type='CORRESPONDENCE',
            created_by=self.admin,
            current_holder=self.admin,
            status='ACTIVE'
        )
        self.token = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

    def test_move_file(self):
        response = self.client.post(f'/api/files/files/{self.file.id}/move/', {
            'to_holder_id': self.receiver.id,
            'action': 'Forwarded for review',
            'remarks': 'Please review this document',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('movement', response.data)

        # Verify file updated
        self.file.refresh_from_db()
        self.assertEqual(self.file.current_holder, self.receiver)
        self.assertEqual(self.file.status, 'IN_TRANSIT')

        # Verify movement record created
        movement = FileMovement.objects.get(file=self.file)
        self.assertEqual(movement.from_holder, self.admin)
        self.assertEqual(movement.to_holder, self.receiver)
        self.assertEqual(movement.action, 'Forwarded for review')
        self.assertFalse(movement.is_returned)

    def test_move_without_to_holder_fails(self):
        response = self.client.post(f'/api/files/files/{self.file.id}/move/', {
            'action': 'Forwarded',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_move_to_nonexistent_user_fails(self):
        response = self.client.post(f'/api/files/files/{self.file.id}/move/', {
            'to_holder_id': 99999,
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_move_with_expected_return_date(self):
        response = self.client.post(f'/api/files/files/{self.file.id}/move/', {
            'to_holder_id': self.receiver.id,
            'expected_return_date': '2026-08-15',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        movement = FileMovement.objects.get(file=self.file)
        self.assertIsNotNone(movement.expected_return_date)


class ReceiveFileTest(APITestCase):
    """Tests for POST /api/files/files/{id}/receive/"""

    def setUp(self):
        self.sender = User.objects.create_user(
            email='sender@ediv.gov.ng',
            password='SenderPass123!@#',
            first_name='Sender',
            last_name='User',
            role='SYSADMIN'
        )
        self.receiver = User.objects.create_user(
            email='receiver@ediv.gov.ng',
            password='ReceiverPass123!@#',
            first_name='Receiver',
            last_name='User',
            role='TCH'
        )
        self.file = File.objects.create(
            file_number='EDIV-2024-REG-002',
            title='File to Receive',
            file_type='MEMO',
            created_by=self.sender,
            current_holder=self.receiver,
            status='IN_TRANSIT'
        )
        self.movement = FileMovement.objects.create(
            file=self.file,
            from_holder=self.sender,
            to_holder=self.receiver,
            action='Forwarded',
        )
        self.receiver_token = RefreshToken.for_user(self.receiver)
        self.sender_token = RefreshToken.for_user(self.sender)

    def test_receiver_marks_received(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.receiver_token.access_token}')
        response = self.client.post(f'/api/files/files/{self.file.id}/receive/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # File status should be ACTIVE again
        self.file.refresh_from_db()
        self.assertEqual(self.file.status, 'ACTIVE')

        # Movement should be marked as returned
        self.movement.refresh_from_db()
        self.assertTrue(self.movement.is_returned)
        self.assertIsNotNone(self.movement.actual_return_date)

    def test_non_holder_cannot_receive(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.sender_token.access_token}')
        response = self.client.post(f'/api/files/files/{self.file.id}/receive/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CloseFileTest(APITestCase):
    """Tests for POST /api/files/files/{id}/close/"""

    def setUp(self):
        self.creator = User.objects.create_user(
            email='creator@ediv.gov.ng',
            password='CreatorPass123!@#',
            first_name='Creator',
            last_name='User',
            role='PRI'
        )
        self.other = User.objects.create_user(
            email='other@ediv.gov.ng',
            password='OtherPass123!@#',
            first_name='Other',
            last_name='User',
            role='TCH'
        )
        self.admin = User.objects.create_user(
            email='admin@ediv.gov.ng',
            password='AdminPass123!@#',
            first_name='Admin',
            last_name='User',
            role='TG'
        )
        self.file = File.objects.create(
            file_number='EDIV-2024-REG-003',
            title='File to Close',
            file_type='REPORT',
            created_by=self.creator,
            current_holder=self.creator,
            status='ACTIVE',
            classification='PUBLIC',  # Visible to all so permission check is reached
        )
        self.creator_token = RefreshToken.for_user(self.creator)
        self.other_token = RefreshToken.for_user(self.other)
        self.admin_token = RefreshToken.for_user(self.admin)

    def test_creator_can_close(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.creator_token.access_token}')
        response = self.client.post(f'/api/files/files/{self.file.id}/close/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.file.refresh_from_db()
        self.assertEqual(self.file.status, 'ARCHIVED')

    def test_admin_can_close(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token.access_token}')
        response = self.client.post(f'/api/files/files/{self.file.id}/close/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.file.refresh_from_db()
        self.assertEqual(self.file.status, 'ARCHIVED')

    def test_other_user_cannot_close(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.other_token.access_token}')
        response = self.client.post(f'/api/files/files/{self.file.id}/close/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_close_logs_status_timeline(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.creator_token.access_token}')
        self.client.post(f'/api/files/files/{self.file.id}/close/')
        self.file.refresh_from_db()
        self.assertEqual(len(self.file.status_timeline), 1)
        self.assertEqual(self.file.status_timeline[0]['status'], 'ARCHIVED')


class LogStatusChangeTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='holder@ediv.gov.ng', password='Test123!@#',
            first_name='Holder', last_name='User', role='TCH'
        )
        self.other = User.objects.create_user(
            email='other@ediv.gov.ng', password='Test123!@#',
            first_name='Other', last_name='User', role='TCH'
        )
        self.file = File.objects.create(
            file_number='EDIV-2024-GEN-001', title='Timeline File',
            file_type='REPORT', created_by=self.user, current_holder=self.user,
            status='ACTIVE', classification='PUBLIC',
        )
        self.user_token = RefreshToken.for_user(self.user)
        self.other_token = RefreshToken.for_user(self.other)

    def test_current_holder_can_log_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token.access_token}')
        response = self.client.post(
            f'/api/files/files/{self.file.id}/log-status/',
            {'status': 'PENDING', 'notes': 'Awaiting review'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.file.refresh_from_db()
        self.assertEqual(self.file.status, 'PENDING')
        self.assertEqual(len(self.file.status_timeline), 1)
        self.assertEqual(self.file.status_timeline[0]['status'], 'PENDING')
        self.assertEqual(self.file.status_timeline[0]['notes'], 'Awaiting review')

    def test_other_user_cannot_log_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.other_token.access_token}')
        response = self.client.post(
            f'/api/files/files/{self.file.id}/log-status/',
            {'status': 'PENDING', 'notes': 'test'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_status_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token.access_token}')
        response = self.client.post(
            f'/api/files/files/{self.file.id}/log-status/',
            {'status': 'INVALID_STATUS'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_multiple_timeline_entries(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token.access_token}')
        self.client.post(
            f'/api/files/files/{self.file.id}/log-status/',
            {'status': 'PENDING', 'notes': 'step 1'}, format='json'
        )
        self.client.post(
            f'/api/files/files/{self.file.id}/log-status/',
            {'status': 'IN_TRANSIT', 'notes': 'step 2'}, format='json'
        )
        self.file.refresh_from_db()
        self.assertEqual(len(self.file.status_timeline), 2)
        self.assertEqual(self.file.status_timeline[0]['status'], 'PENDING')
        self.assertEqual(self.file.status_timeline[1]['status'], 'IN_TRANSIT')

    def test_move_logs_status_timeline(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token.access_token}')
        response = self.client.post(
            f'/api/files/files/{self.file.id}/move/',
            {'to_holder_id': self.other.id, 'action': 'Forwarded', 'remarks': 'Please review'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.file.refresh_from_db()
        self.assertGreaterEqual(len(self.file.status_timeline), 1)
        self.assertEqual(self.file.status_timeline[0]['status'], 'IN_TRANSIT')
