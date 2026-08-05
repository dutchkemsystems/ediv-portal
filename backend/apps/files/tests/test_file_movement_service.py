"""Tests for enhanced FileMovementService."""
from django.test import TestCase
from django.core.cache import cache
from django.utils import timezone
from apps.users.models import User
from apps.departments.models import Department
from apps.files.models import File, FileMovement, WorkflowConfig
from apps.files.services.file_movement_service import FileMovementService


class FileMovementServiceCreateFileTest(TestCase):
    """Tests for enhanced create_file with auto-classification."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='creator@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Creator',
            last_name='User',
            role='SYSADMIN'
        )
        self.department = Department.objects.create(
            name='Finance',
            code='FIN',
            category='CORE'
        )
        cache.clear()

    def test_create_file_auto_generates_number(self):
        """create_file should auto-generate a unique file number."""
        file_obj = FileMovementService.create_file(
            title='Test Finance File',
            file_type='CORRESPONDENCE',
            file_category='CORR',
            description='Budget report for 2026',
            classification='CONFIDENTIAL',
            priority='HIGH',
            created_by=self.user,
            department=self.department,
        )
        self.assertIsNotNone(file_obj.file_number)
        self.assertTrue(file_obj.file_number.startswith('FIL-'))
        self.assertEqual(file_obj.created_by, self.user)
        self.assertEqual(file_obj.current_holder, self.user)

    def test_create_file_records_created_movement(self):
        """create_file should record a CREATED movement."""
        file_obj = FileMovementService.create_file(
            title='Movement Test',
            file_type='MEMO',
            file_category='ADMIN',
            description='Test memo',
            classification='INTERNAL',
            priority='NORMAL',
            created_by=self.user,
        )
        movement = FileMovement.objects.get(file=file_obj, action='CREATED')
        self.assertIsNotNone(movement)
        self.assertEqual(movement.from_holder, self.user)

    def test_create_file_adds_timeline_entry(self):
        """create_file should add entry to status_timeline."""
        file_obj = FileMovementService.create_file(
            title='Timeline Test',
            file_type='MEMO',
            file_category='ADMIN',
            description='Test',
            classification='INTERNAL',
            priority='NORMAL',
            created_by=self.user,
        )
        self.assertIsNotNone(file_obj.status_timeline)
        self.assertGreaterEqual(len(file_obj.status_timeline), 1)
        self.assertEqual(file_obj.status_timeline[0]['action'], 'CREATED')

    def test_create_file_with_template(self):
        """create_file with template should apply template defaults."""
        from apps.files.models import FileTemplate
        template = FileTemplate.objects.create(
            name='Test Template',
            category='MEMO',
            file_type='MEMO',
            file_category='ADMIN',
            default_classification='CONFIDENTIAL',
            default_priority='HIGH',
            created_by=self.user,
        )
        file_obj = FileMovementService.create_file(
            title='Template File',
            file_type='CORRESPONDENCE',
            file_category='CORR',
            description='Test',
            classification='INTERNAL',
            priority='NORMAL',
            created_by=self.user,
            template=template,
        )
        # Template defaults should override
        self.assertEqual(file_obj.classification, 'CONFIDENTIAL')
        self.assertEqual(file_obj.priority, 'HIGH')
        template.refresh_from_db()
        self.assertEqual(template.usage_count, 1)


class FileMovementServiceMoveFileTest(TestCase):
    """Tests for enhanced move_file with validation."""

    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@ediv.gov.ng', password='TestPass123!@#',
            first_name='User', last_name='One', role='SYSADMIN'
        )
        self.user2 = User.objects.create_user(
            email='user2@ediv.gov.ng', password='TestPass123!@#',
            first_name='User', last_name='Two', role='TCH'
        )
        self.file = File.objects.create(
            file_number='EDIV-2026-MOV-001',
            title='File to Move',
            file_type='MEMO',
            file_category='ADMIN',
            created_by=self.user1,
            current_holder=self.user1,
            status='ACTIVE',
        )
        cache.clear()

    def test_move_file_success(self):
        """Valid move should update current_holder and create movement."""
        movement = FileMovementService.move_file(
            file=self.file,
            from_holder=self.user1,
            to_holder=self.user2,
            action='FORWARDED',
            remarks='Please review',
        )
        self.file.refresh_from_db()
        self.assertEqual(self.file.current_holder, self.user2)
        self.assertEqual(self.file.status, 'IN_TRANSIT')
        self.assertEqual(movement.from_holder, self.user1)
        self.assertEqual(movement.to_holder, self.user2)

    def test_move_file_wrong_holder_fails(self):
        """Move from wrong holder should raise ValueError."""
        with self.assertRaises(ValueError):
            FileMovementService.move_file(
                file=self.file,
                from_holder=self.user2,
                to_holder=self.user1,
                action='FORWARDED',
            )

    def test_move_file_escalation_increments_priority(self):
        """ESCALATED action should increment file priority."""
        self.file.priority = 'NORMAL'
        self.file.save()
        FileMovementService.move_file(
            file=self.file,
            from_holder=self.user1,
            to_holder=self.user2,
            action='ESCALATED',
            remarks='Urgent review needed',
        )
        self.file.refresh_from_db()
        self.assertEqual(self.file.priority, 'HIGH')

    def test_move_file_returns_movement(self):
        """move_file should return a FileMovement instance."""
        movement = FileMovementService.move_file(
            file=self.file,
            from_holder=self.user1,
            to_holder=self.user2,
            action='FORWARDED',
        )
        self.assertIsInstance(movement, FileMovement)

    def test_move_file_adds_timeline(self):
        """move_file should add timeline entry."""
        FileMovementService.move_file(
            file=self.file,
            from_holder=self.user1,
            to_holder=self.user2,
            action='FORWARDED',
        )
        self.file.refresh_from_db()
        self.assertIsNotNone(self.file.status_timeline)
        self.assertGreaterEqual(len(self.file.status_timeline), 1)


class FileMovementServiceWorkflowTest(TestCase):
    """Tests for workflow steps and deadlines."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='workflow@ediv.gov.ng', password='TestPass123!@#',
            first_name='Workflow', last_name='User', role='SYSADMIN'
        )
        cache.clear()

    def test_get_incoming_workflow_steps(self):
        """Should return 11 incoming workflow steps."""
        steps = FileMovementService.get_incoming_workflow()
        self.assertEqual(len(steps), 11)

    def test_get_outgoing_workflow_steps(self):
        """Should return 7 outgoing workflow steps."""
        steps = FileMovementService.get_outgoing_workflow()
        self.assertEqual(len(steps), 7)

    def test_workflow_config_overrides_default(self):
        """WorkflowConfig should override default deadline."""
        WorkflowConfig.objects.create(
            step_name='REGISTRY',
            direction='INCOMING',
            default_deadline_hours=4,
            is_active=True,
        )
        deadline = FileMovementService.get_deadline_for_step('REGISTRY', 'INCOMING')
        self.assertEqual(deadline, 4)

    def test_workflow_config_returns_default_when_not_configured(self):
        """Should return default deadline when no config exists."""
        deadline = FileMovementService.get_deadline_for_step('REGISTRY', 'INCOMING')
        self.assertEqual(deadline, 2)

    def test_outgoing_workflow_deadline(self):
        """Should return correct deadline for outgoing workflow."""
        deadline = FileMovementService.get_deadline_for_step('DESK_OFFICER', 'OUTGOING')
        self.assertEqual(deadline, 24)


class FileMovementServiceCacheTest(TestCase):
    """Tests for caching integration."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='cache@ediv.gov.ng', password='TestPass123!@#',
            first_name='Cache', last_name='User', role='SYSADMIN'
        )
        self.file = File.objects.create(
            file_number='EDIV-2026-CACHE-001',
            title='Cache Test File',
            file_type='MEMO',
            file_category='ADMIN',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        cache.clear()

    def test_get_file_status_caches_result(self):
        """get_file_status should cache the result."""
        result1 = FileMovementService.get_file_status(self.file.id)
        cache_key = f'file_status_{self.file.id}'
        cached = cache.get(cache_key)
        self.assertIsNotNone(cached)

    def test_get_file_status_returns_correct_data(self):
        """get_file_status should return correct file data."""
        result = FileMovementService.get_file_status(self.file.id)
        self.assertEqual(result['file_number'], 'EDIV-2026-CACHE-001')
        self.assertEqual(result['title'], 'Cache Test File')
        self.assertEqual(result['status'], 'ACTIVE')

    def test_get_file_status_nonexistent(self):
        """get_file_status should return None for non-existent file."""
        result = FileMovementService.get_file_status(99999)
        self.assertIsNone(result)

    def test_move_file_invalidates_cache(self):
        """move_file should invalidate the file status cache."""
        FileMovementService.get_file_status(self.file.id)
        cache_key = f'file_status_{self.file.id}'
        self.assertIsNotNone(cache.get(cache_key))

        other_user = User.objects.create_user(
            email='other@ediv.gov.ng', password='Test123!@#',
            first_name='Other', last_name='User', role='TCH'
        )
        FileMovementService.move_file(
            file=self.file,
            from_holder=self.user,
            to_holder=other_user,
            action='FORWARDED',
        )
        self.assertIsNone(cache.get(cache_key))

    def test_invalidate_cache_method(self):
        """_invalidate_cache should remove cached status."""
        FileMovementService.get_file_status(self.file.id)
        cache_key = f'file_status_{self.file.id}'
        self.assertIsNotNone(cache.get(cache_key))
        FileMovementService._invalidate_cache(self.file.id)
        self.assertIsNone(cache.get(cache_key))
