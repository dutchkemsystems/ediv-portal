from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import User
from apps.schools.models import School
from apps.files.models import File, FileMovement, FileAttachment, WorkflowConfig, FileTemplate, OfflineQueue, FileClassification
from django.utils import timezone


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
            file_category='CORR',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
            classification='CONFIDENTIAL',
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
            file_category='CORR',
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
            'file_category': 'ADMIN',
            'status': 'ACTIVE',
            'classification': 'CONFIDENTIAL',
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
            'file_category': 'ADMIN',
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
            file_category='CORR',
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
            file_category='ADMIN',
            created_by=self.sender,
            current_holder=self.receiver,
            status='IN_TRANSIT'
        )
        self.movement = FileMovement.objects.create(
            file=self.file,
            from_holder=self.sender,
            to_holder=self.receiver,
            action='FORWARDED',
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
            file_category='ADMIN',
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
            file_type='REPORT', file_category='ADMIN',
            created_by=self.user, current_holder=self.user,
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
            {'to_holder_id': self.other.id, 'action': 'FORWARDED', 'remarks': 'Please review'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.file.refresh_from_db()
        self.assertGreaterEqual(len(self.file.status_timeline), 1)
        self.assertEqual(self.file.status_timeline[0]['status'], 'IN_TRANSIT')


class WorkflowConfigModelTest(TestCase):
    def test_create_workflow_config(self):
        config = WorkflowConfig.objects.create(
            step_name='Initial Review',
            direction='INCOMING',
            default_deadline_hours=24,
            escalation_level=1,
            notification_enabled=True,
            notification_reminder_hours=4,
        )
        self.assertIsNotNone(config.id)
        self.assertEqual(config.step_name, 'Initial Review')
        self.assertEqual(config.direction, 'INCOMING')
        self.assertEqual(config.default_deadline_hours, 24)
        self.assertTrue(config.is_active)
        self.assertTrue(config.notification_enabled)

    def test_str_representation(self):
        config = WorkflowConfig.objects.create(
            step_name='Approval',
            direction='OUTGOING',
            default_deadline_hours=48,
        )
        self.assertEqual(str(config), 'Approval (OUTGOING) - 48h')

    def test_unique_step_direction_constraint(self):
        WorkflowConfig.objects.create(step_name='Review', direction='INCOMING')
        with self.assertRaises(Exception):
            WorkflowConfig.objects.create(step_name='Review', direction='INCOMING')

    def test_different_directions_allowed(self):
        WorkflowConfig.objects.create(step_name='Review', direction='INCOMING')
        config2 = WorkflowConfig.objects.create(step_name='Review', direction='OUTGOING')
        self.assertIsNotNone(config2.id)

    def test_default_values(self):
        config = WorkflowConfig.objects.create(step_name='Step', direction='INTERNAL')
        self.assertEqual(config.default_deadline_hours, 24)
        self.assertEqual(config.escalation_level, 1)
        self.assertTrue(config.is_active)
        self.assertTrue(config.notification_enabled)
        self.assertEqual(config.notification_reminder_hours, 4)


class FileTemplateModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='templateuser@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Template',
            last_name='User',
            role='SYSADMIN'
        )

    def test_create_file_template(self):
        template = FileTemplate.objects.create(
            name='Standard Correspondence',
            description='Default template for correspondence',
            category='CORRESPONDENCE',
            file_type='CORRESPONDENCE',
            file_category='CORR',
            default_classification='INTERNAL',
            default_priority='NORMAL',
            template_content='Default body',
            template_fields={'subject': 'required', 'recipient': 'required'},
            created_by=self.user,
        )
        self.assertIsNotNone(template.id)
        self.assertEqual(template.name, 'Standard Correspondence')
        self.assertEqual(template.category, 'CORRESPONDENCE')
        self.assertEqual(template.usage_count, 0)
        self.assertTrue(template.is_active)

    def test_str_representation(self):
        template = FileTemplate.objects.create(
            name='Memo Template',
            category='MEMO',
            created_by=self.user,
        )
        self.assertEqual(str(template), 'Memo Template (MEMO)')

    def test_ordering_by_usage_count(self):
        t1 = FileTemplate.objects.create(name='A', category='OTHER', created_by=self.user, usage_count=5)
        t2 = FileTemplate.objects.create(name='B', category='OTHER', created_by=self.user, usage_count=10)
        templates = list(FileTemplate.objects.all())
        self.assertEqual(templates[0], t2)
        self.assertEqual(templates[1], t1)

    def test_optional_fields(self):
        template = FileTemplate.objects.create(
            name='Minimal Template',
            created_by=self.user,
        )
        self.assertEqual(template.category, 'OTHER')
        self.assertEqual(template.default_classification, 'INTERNAL')
        self.assertEqual(template.default_priority, 'NORMAL')
        self.assertEqual(template.template_content, '')
        self.assertEqual(template.template_fields, {})


class OfflineQueueModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='offlineuser@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Offline',
            last_name='User',
            role='TCH'
        )

    def test_create_offline_queue_entry(self):
        entry = OfflineQueue.objects.create(
            object_id='file-123',
            action_type='CREATE',
            user=self.user,
            data={'title': 'New File', 'file_type': 'MEMO'},
            status='PENDING',
        )
        self.assertIsNotNone(entry.id)
        self.assertEqual(entry.object_id, 'file-123')
        self.assertEqual(entry.action_type, 'CREATE')
        self.assertEqual(entry.status, 'PENDING')
        self.assertEqual(entry.attempt_count, 0)

    def test_str_representation(self):
        entry = OfflineQueue.objects.create(
            object_id='file-456',
            action_type='UPDATE',
            user=self.user,
        )
        self.assertEqual(str(entry), 'UPDATE - file-456 (PENDING)')

    def test_default_status(self):
        entry = OfflineQueue.objects.create(
            object_id='obj-1',
            action_type='MOVE',
            user=self.user,
        )
        self.assertEqual(entry.status, 'PENDING')
        self.assertEqual(entry.attempt_count, 0)
        self.assertEqual(entry.error_message, '')

    def test_index_fields(self):
        """Test that indexed fields exist by querying them."""
        OfflineQueue.objects.create(object_id='a', action_type='CREATE', user=self.user, status='PENDING')
        OfflineQueue.objects.create(object_id='b', action_type='UPDATE', user=self.user, status='COMPLETED')
        # Querying indexed fields should work
        self.assertEqual(OfflineQueue.objects.filter(status='PENDING').count(), 1)
        self.assertEqual(OfflineQueue.objects.filter(user=self.user, status='COMPLETED').count(), 1)

    def test_ordering(self):
        e1 = OfflineQueue.objects.create(object_id='a', action_type='CREATE', user=self.user)
        e2 = OfflineQueue.objects.create(object_id='b', action_type='UPDATE', user=self.user)
        entries = list(OfflineQueue.objects.all())
        self.assertEqual(entries[0], e2)
        self.assertEqual(entries[1], e1)


class FileClassificationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='classuser@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Classify',
            last_name='User',
            role='SYSADMIN'
        )
        self.file = File.objects.create(
            file_number='EDIV-2024-CLASS-001',
            title='File for Classification',
            file_type='CORRESPONDENCE',
            file_category='CORR',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )

    def test_create_file_classification(self):
        classification = FileClassification.objects.create(
            file=self.file,
            suggested_department='Finance',
            department_confidence=0.85,
            urgency='HIGH',
            sensitivity='RESTRICTED',
            file_type_suggestion='Invoice',
            keywords=['finance', 'invoice', 'payment'],
            overall_confidence=0.78,
        )
        self.assertIsNotNone(classification.id)
        self.assertEqual(classification.file, self.file)
        self.assertEqual(classification.suggested_department, 'Finance')
        self.assertAlmostEqual(classification.department_confidence, 0.85)
        self.assertEqual(classification.urgency, 'HIGH')
        self.assertEqual(classification.sensitivity, 'RESTRICTED')
        self.assertEqual(classification.file_type_suggestion, 'Invoice')
        self.assertEqual(classification.keywords, ['finance', 'invoice', 'payment'])
        self.assertAlmostEqual(classification.overall_confidence, 0.78)

    def test_str_representation(self):
        classification = FileClassification.objects.create(
            file=self.file,
            suggested_department='HR',
        )
        self.assertEqual(str(classification), f'Classification for {self.file.file_number}')

    def test_one_to_one_constraint(self):
        FileClassification.objects.create(file=self.file, suggested_department='Admin')
        with self.assertRaises(Exception):
            FileClassification.objects.create(file=self.file, suggested_department='Another')

    def test_default_values(self):
        classification = FileClassification.objects.create(file=self.file)
        self.assertEqual(classification.suggested_department, '')
        self.assertAlmostEqual(classification.department_confidence, 0)
        self.assertEqual(classification.urgency, 'MEDIUM')
        self.assertEqual(classification.sensitivity, 'PUBLIC')
        self.assertEqual(classification.file_type_suggestion, '')
        self.assertEqual(classification.keywords, [])
        self.assertAlmostEqual(classification.overall_confidence, 0)


class FileAttachmentFieldsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='attachuser@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Attach',
            last_name='User',
            role='SYSADMIN'
        )
        self.file = File.objects.create(
            file_number='EDIV-2024-ATT-001',
            title='File for Attachment Test',
            file_type='MEMO',
            file_category='ADMIN',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )

    def test_mime_type_field(self):
        attachment = FileAttachment.objects.create(
            file=self.file,
            document='files/attachments/test.pdf',
            original_filename='test.pdf',
            file_size=1024,
            uploaded_by=self.user,
            mime_type='application/pdf',
        )
        self.assertEqual(attachment.mime_type, 'application/pdf')

    def test_file_format_field(self):
        attachment = FileAttachment.objects.create(
            file=self.file,
            document='files/attachments/test.pdf',
            original_filename='test.pdf',
            file_size=1024,
            uploaded_by=self.user,
            mime_type='application/pdf',
            file_format='pdf',
        )
        self.assertEqual(attachment.file_format, 'pdf')

    def test_file_format_choices(self):
        attachment = FileAttachment.objects.create(
            file=self.file,
            document='files/attachments/test.docx',
            original_filename='test.docx',
            file_size=2048,
            uploaded_by=self.user,
            mime_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            file_format='docx',
        )
        self.assertEqual(attachment.file_format, 'docx')
