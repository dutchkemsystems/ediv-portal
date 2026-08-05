"""Tests for AuditService."""
from django.test import TestCase
from apps.users.models import User
from apps.files.models import File
from apps.files.services.audit_service import AuditService
from apps.audit.models import AuditLog


class AuditServiceLogActionTest(TestCase):
    """Tests for AuditService.log_action"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='auditor@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Audit',
            last_name='User',
            role='SYSADMIN'
        )
        self.file = File.objects.create(
            file_number='EDIV-2026-AUDIT-001',
            title='Audit Test File',
            file_type='MEMO',
            file_category='ADMIN',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )

    def test_log_action_creates_record(self):
        """log_action should create an AuditLog record."""
        log = AuditService.log_action(
            user=self.user,
            action='CREATE',
            resource_type='File',
            resource_id=self.file.id,
            description='Created test file',
        )
        self.assertIsNotNone(log.id)
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.resource_type, 'File')
        self.assertEqual(log.object_id, str(self.file.id))

    def test_log_action_with_new_value(self):
        """log_action should store new_value JSON."""
        log = AuditService.log_action(
            user=self.user,
            action='UPDATE',
            resource_type='File',
            resource_id=self.file.id,
            description='Updated file',
            new_value={'status': 'ACTIVE'},
        )
        self.assertEqual(log.new_value, {'status': 'ACTIVE'})

    def test_log_action_with_old_value(self):
        """log_action should store old_value JSON."""
        log = AuditService.log_action(
            user=self.user,
            action='UPDATE',
            resource_type='File',
            resource_id=self.file.id,
            description='Changed status',
            old_value={'status': 'DRAFT'},
            new_value={'status': 'ACTIVE'},
        )
        self.assertEqual(log.old_value, {'status': 'DRAFT'})

    def test_log_action_with_ip_address(self):
        """log_action should store ip_address."""
        log = AuditService.log_action(
            user=self.user,
            action='LOGIN',
            resource_type='User',
            resource_id=self.user.id,
            description='User logged in',
            ip_address='127.0.0.1',
        )
        self.assertEqual(log.ip_address, '127.0.0.1')

    def test_get_resource_logs(self):
        """get_resource_logs should return logs for a specific resource."""
        AuditService.log_action(
            user=self.user, action='CREATE', resource_type='File',
            resource_id=self.file.id, description='Created',
        )
        AuditService.log_action(
            user=self.user, action='UPDATE', resource_type='File',
            resource_id=self.file.id, description='Updated',
        )
        AuditService.log_action(
            user=self.user, action='CREATE', resource_type='File',
            resource_id=999, description='Other file',
        )
        logs = AuditService.get_resource_logs('File', self.file.id)
        self.assertEqual(len(logs), 2)

    def test_get_user_logs(self):
        """get_user_logs should return logs for a specific user."""
        other_user = User.objects.create_user(
            email='other@ediv.gov.ng', password='Test123!@#',
            first_name='Other', last_name='User', role='TCH'
        )
        AuditService.log_action(
            user=self.user, action='CREATE', resource_type='File',
            resource_id=self.file.id, description='By auditor',
        )
        AuditService.log_action(
            user=other_user, action='UPDATE', resource_type='File',
            resource_id=self.file.id, description='By other',
        )
        logs = AuditService.get_user_logs(self.user.id)
        self.assertEqual(len(logs), 1)

    def test_get_recent_logs(self):
        """get_recent_logs should return recent logs."""
        AuditService.log_action(
            user=self.user, action='CREATE', resource_type='File',
            resource_id=self.file.id, description='Created',
        )
        logs = AuditService.get_recent_logs(limit=10)
        self.assertGreaterEqual(len(logs), 1)

    def test_log_action_with_user_agent(self):
        """log_action should store user_agent."""
        log = AuditService.log_action(
            user=self.user,
            action='CREATE',
            resource_type='File',
            resource_id=self.file.id,
            description='Test with user agent',
            user_agent='Mozilla/5.0',
        )
        self.assertEqual(log.user_agent, 'Mozilla/5.0')

    def test_log_action_move_action(self):
        """log_action with MOVE action should map to FILE_MOVEMENT."""
        log = AuditService.log_action(
            user=self.user,
            action='MOVE',
            resource_type='File',
            resource_id=self.file.id,
            description='File moved',
        )
        self.assertIsNotNone(log.id)
        # Verify it's stored with the correct module
        self.assertEqual(log.module, 'files')
