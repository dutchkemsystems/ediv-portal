"""Tests for FileMovementService."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta

from apps.files.models import File, FileMovement, FileClassification
from apps.files.services.file_movement_service import FileMovementService

User = get_user_model()


class FileMovementServiceCreateFileTest(TestCase):
    """Tests for FileMovementService.create_file."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='creator@test.gov.ng',
            password='TestPass123!@#',
            first_name='Creator',
            last_name='User',
            role='SYSADMIN'
        )

    def test_create_file_returns_file_instance(self):
        """create_file should return a File instance."""
        file_obj = FileMovementService.create_file(
            title='Test Correspondence',
            file_type='CORRESPONDENCE',
            file_category='CORR',
            description='A test file',
            classification='CONFIDENTIAL',
            priority='NORMAL',
            created_by=self.user,
        )
        self.assertIsInstance(file_obj, File)

    def test_create_file_generates_file_number(self):
        """File number should be auto-generated with FIL prefix."""
        file_obj = FileMovementService.create_file(
            title='Test File',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='LOW',
            created_by=self.user,
        )
        self.assertTrue(file_obj.file_number.startswith('FIL-'))
        self.assertIn(str(date.today().year), file_obj.file_number)

    def test_create_file_with_department(self):
        """File number should include department code when department provided."""
        from apps.departments.models import Department
        dept = Department.objects.create(name='Finance', code='FIN', category='CORE')
        file_obj = FileMovementService.create_file(
            title='Budget File',
            file_type='INVOICE',
            file_category='FIN',
            description='Budget document',
            classification='CONFIDENTIAL',
            priority='HIGH',
            created_by=self.user,
            department=dept,
        )
        self.assertIn('FIN', file_obj.file_number)
        self.assertTrue(file_obj.file_number.startswith(f'FIL-FIN-{date.today().year}'))

    def test_create_file_auto_increments_sequence(self):
        """Successive files should have incrementing sequence numbers."""
        file1 = FileMovementService.create_file(
            title='File 1',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.user,
        )
        file2 = FileMovementService.create_file(
            title='File 2',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.user,
        )
        # Both should have valid file numbers and be different
        self.assertNotEqual(file1.file_number, file2.file_number)
        # Extract sequence numbers
        seq1 = int(file1.file_number.split('-')[-1])
        seq2 = int(file2.file_number.split('-')[-1])
        self.assertEqual(seq2, seq1 + 1)

    def test_create_file_sets_created_by(self):
        """File's created_by should be set to the provided user."""
        file_obj = FileMovementService.create_file(
            title='My File',
            file_type='CORRESPONDENCE',
            file_category='CORR',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.user,
        )
        self.assertEqual(file_obj.created_by, self.user)

    def test_create_file_sets_current_holder(self):
        """File's current_holder should be set to created_by."""
        file_obj = FileMovementService.create_file(
            title='My File',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.user,
        )
        self.assertEqual(file_obj.current_holder, self.user)

    def test_create_file_sets_status_draft(self):
        """New file should have DRAFT status."""
        file_obj = FileMovementService.create_file(
            title='Draft File',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.user,
        )
        self.assertEqual(file_obj.status, 'DRAFT')

    def test_create_file_records_created_movement(self):
        """Creating a file should record a CREATED movement."""
        file_obj = FileMovementService.create_file(
            title='With Movement',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.user,
        )
        movement = FileMovement.objects.filter(file=file_obj).first()
        self.assertIsNotNone(movement)
        self.assertEqual(movement.action, 'CREATED')
        self.assertEqual(movement.from_holder, self.user)

    def test_create_file_adds_to_status_timeline(self):
        """Creating a file should add an entry to status_timeline."""
        file_obj = FileMovementService.create_file(
            title='Timeline File',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.user,
        )
        self.assertGreaterEqual(len(file_obj.status_timeline), 1)
        entry = file_obj.status_timeline[0]
        self.assertEqual(entry['status'], 'DRAFT')
        self.assertIn('timestamp', entry)
        self.assertEqual(entry['changed_by_id'], self.user.id)

    def test_create_file_with_template(self):
        """If template provided, defaults should be applied."""
        from apps.files.models import FileTemplate
        template = FileTemplate.objects.create(
            name='Correspondence Template',
            category='CORRESPONDENCE',
            file_type='CORRESPONDENCE',
            file_category='CORR',
            default_classification='INTERNAL',
            default_priority='HIGH',
            created_by=self.user,
        )
        file_obj = FileMovementService.create_file(
            title='From Template',
            file_type='CORRESPONDENCE',
            file_category='CORR',
            description='',
            classification='INTERNAL',
            priority='HIGH',
            created_by=self.user,
            template=template,
        )
        self.assertIsNotNone(file_obj)
        self.assertEqual(file_obj.file_type, 'CORRESPONDENCE')

    def test_create_file_with_tags(self):
        """Tags should be saved on the file."""
        file_obj = FileMovementService.create_file(
            title='Tagged File',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.user,
            tags=['important', 'review'],
        )
        self.assertEqual(file_obj.tags, ['important', 'review'])

    def test_create_file_with_due_date(self):
        """Due date should be saved on the file."""
        due = date.today() + timedelta(days=7)
        file_obj = FileMovementService.create_file(
            title='Due File',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='URGENT',
            created_by=self.user,
            due_date=due,
        )
        self.assertEqual(file_obj.due_date, due)

    def test_create_file_with_school(self):
        """School should be saved on the file."""
        from apps.schools.models import School
        school = School.objects.create(name='Test School', code='TSC01')
        file_obj = FileMovementService.create_file(
            title='School File',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.user,
            school=school,
        )
        self.assertEqual(file_obj.school, school)


class FileMovementServiceMoveFileTest(TestCase):
    """Tests for FileMovementService.move_file."""

    def setUp(self):
        self.sender = User.objects.create_user(
            email='sender@test.gov.ng',
            password='TestPass123!@#',
            first_name='Sender',
            last_name='User',
            role='SYSADMIN'
        )
        self.receiver = User.objects.create_user(
            email='receiver@test.gov.ng',
            password='TestPass123!@#',
            first_name='Receiver',
            last_name='User',
            role='TCH'
        )
        self.file = FileMovementService.create_file(
            title='Test File',
            file_type='CORRESPONDENCE',
            file_category='CORR',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.sender,
        )

    def test_move_file_returns_movement(self):
        """move_file should return a FileMovement instance."""
        movement = FileMovementService.move_file(
            file=self.file,
            from_holder=self.sender,
            to_holder=self.receiver,
            action='FORWARDED',
            remarks='Please review',
        )
        self.assertIsInstance(movement, FileMovement)

    def test_move_file_updates_current_holder(self):
        """move_file should update file.current_holder."""
        FileMovementService.move_file(
            file=self.file,
            from_holder=self.sender,
            to_holder=self.receiver,
            action='FORWARDED',
        )
        self.file.refresh_from_db()
        self.assertEqual(self.file.current_holder, self.receiver)

    def test_move_file_sets_status_in_transit(self):
        """move_file should set status to IN_TRANSIT."""
        FileMovementService.move_file(
            file=self.file,
            from_holder=self.sender,
            to_holder=self.receiver,
            action='FORWARDED',
        )
        self.file.refresh_from_db()
        self.assertEqual(self.file.status, 'IN_TRANSIT')

    def test_move_file_records_movement(self):
        """move_file should create a FileMovement record with correct fields."""
        movement = FileMovementService.move_file(
            file=self.file,
            from_holder=self.sender,
            to_holder=self.receiver,
            action='FORWARDED',
            remarks='Review please',
        )
        self.assertEqual(movement.file, self.file)
        self.assertEqual(movement.from_holder, self.sender)
        self.assertEqual(movement.to_holder, self.receiver)
        self.assertEqual(movement.action, 'FORWARDED')
        self.assertEqual(movement.remarks, 'Review please')

    def test_move_file_adds_to_timeline(self):
        """move_file should add entry to status_timeline."""
        FileMovementService.move_file(
            file=self.file,
            from_holder=self.sender,
            to_holder=self.receiver,
            action='FORWARDED',
        )
        self.file.refresh_from_db()
        # At least the CREATED entry from create_file + the move entry
        self.assertGreaterEqual(len(self.file.status_timeline), 2)

    def test_move_file_validates_from_holder(self):
        """move_file should raise ValueError if from_holder is not current_holder."""
        stranger = User.objects.create_user(
            email='stranger@test.gov.ng',
            password='TestPass123!@#',
            first_name='Stranger',
            last_name='User',
            role='TCH'
        )
        with self.assertRaises(ValueError):
            FileMovementService.move_file(
                file=self.file,
                from_holder=stranger,
                to_holder=self.receiver,
                action='FORWARDED',
            )

    def test_move_file_with_expected_return_date(self):
        """move_file should record expected_return_date."""
        return_date = date.today() + timedelta(days=5)
        movement = FileMovementService.move_file(
            file=self.file,
            from_holder=self.sender,
            to_holder=self.receiver,
            action='FORWARDED',
            expected_return_date=return_date,
        )
        self.assertEqual(movement.expected_return_date, return_date)

    def test_move_file_returned_sets_is_returned(self):
        """When action is RETURNED, is_returned=True and actual_return_date set."""
        # First move file to receiver
        FileMovementService.move_file(
            file=self.file,
            from_holder=self.sender,
            to_holder=self.receiver,
            action='FORWARDED',
        )
        # Now receiver returns it
        movement = FileMovementService.move_file(
            file=self.file,
            from_holder=self.receiver,
            to_holder=self.sender,
            action='RETURNED',
        )
        self.assertTrue(movement.is_returned)
        self.assertIsNotNone(movement.actual_return_date)

    def test_move_file_escalated_increments_priority(self):
        """When action is ESCALATED, priority should be incremented."""
        FileMovementService.move_file(
            file=self.file,
            from_holder=self.sender,
            to_holder=self.receiver,
            action='ESCALATED',
        )
        self.file.refresh_from_db()
        # NORMAL -> HIGH
        self.assertEqual(self.file.priority, 'HIGH')

    def test_move_file_escalated_high_to_urgent(self):
        """When ESCALATED and priority is HIGH, it should become URGENT."""
        self.file.priority = 'HIGH'
        self.file.save()
        FileMovementService.move_file(
            file=self.file,
            from_holder=self.sender,
            to_holder=self.receiver,
            action='ESCALATED',
        )
        self.file.refresh_from_db()
        self.assertEqual(self.file.priority, 'URGENT')

    def test_move_file_escalated_urgent_stays_urgent(self):
        """When ESCALATED and already URGENT, should stay URGENT."""
        self.file.priority = 'URGENT'
        self.file.save()
        FileMovementService.move_file(
            file=self.file,
            from_holder=self.sender,
            to_holder=self.receiver,
            action='ESCALATED',
        )
        self.file.refresh_from_db()
        self.assertEqual(self.file.priority, 'URGENT')


class FileMovementServiceReceiveFileTest(TestCase):
    """Tests for FileMovementService.receive_file."""

    def setUp(self):
        self.sender = User.objects.create_user(
            email='sender@test.gov.ng',
            password='TestPass123!@#',
            first_name='Sender',
            last_name='User',
            role='SYSADMIN'
        )
        self.receiver = User.objects.create_user(
            email='receiver@test.gov.ng',
            password='TestPass123!@#',
            first_name='Receiver',
            last_name='User',
            role='TCH'
        )
        self.file = FileMovementService.create_file(
            title='Test File',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.sender,
        )
        FileMovementService.move_file(
            file=self.file,
            from_holder=self.sender,
            to_holder=self.receiver,
            action='FORWARDED',
        )

    def test_receive_file_returns_movement(self):
        """receive_file should return a FileMovement instance."""
        movement = FileMovementService.receive_file(
            file=self.file,
            received_by=self.receiver,
        )
        self.assertIsInstance(movement, FileMovement)

    def test_receive_file_validates_holder(self):
        """receive_file should raise ValueError if received_by != current_holder."""
        with self.assertRaises(ValueError):
            FileMovementService.receive_file(
                file=self.file,
                received_by=self.sender,
            )

    def test_receive_file_sets_status_active(self):
        """receive_file should set status to ACTIVE."""
        FileMovementService.receive_file(
            file=self.file,
            received_by=self.receiver,
        )
        self.file.refresh_from_db()
        self.assertEqual(self.file.status, 'ACTIVE')

    def test_receive_file_marks_movement_returned(self):
        """receive_file should mark the last movement as returned."""
        movement = FileMovementService.receive_file(
            file=self.file,
            received_by=self.receiver,
        )
        # The latest movement (the receive one) or the forwarded one should be marked
        last_movement = FileMovement.objects.filter(file=self.file).order_by('-movement_date').first()
        self.assertTrue(last_movement.is_returned)

    def test_receive_file_sets_actual_return_date(self):
        """receive_file should set actual_return_date."""
        FileMovementService.receive_file(
            file=self.file,
            received_by=self.receiver,
        )
        last_movement = FileMovement.objects.filter(file=self.file).order_by('-movement_date').first()
        self.assertIsNotNone(last_movement.actual_return_date)


class FileMovementServiceRecallFileTest(TestCase):
    """Tests for FileMovementService.recall_file."""

    def setUp(self):
        self.sender = User.objects.create_user(
            email='sender@test.gov.ng',
            password='TestPass123!@#',
            first_name='Sender',
            last_name='User',
            role='SYSADMIN'
        )
        self.receiver = User.objects.create_user(
            email='receiver@test.gov.ng',
            password='TestPass123!@#',
            first_name='Receiver',
            last_name='User',
            role='TCH'
        )
        self.file = FileMovementService.create_file(
            title='Recall File',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.sender,
        )
        FileMovementService.move_file(
            file=self.file,
            from_holder=self.sender,
            to_holder=self.receiver,
            action='FORWARDED',
        )

    def test_recall_file_returns_movement(self):
        """recall_file should return a FileMovement instance."""
        movement = FileMovementService.recall_file(
            file=self.file,
            recalled_by=self.sender,
            reason='Need it back',
        )
        self.assertIsInstance(movement, FileMovement)

    def test_recall_file_sets_current_holder(self):
        """recall_file should set current_holder to recalled_by."""
        FileMovementService.recall_file(
            file=self.file,
            recalled_by=self.sender,
        )
        self.file.refresh_from_db()
        self.assertEqual(self.file.current_holder, self.sender)

    def test_recall_file_records_returned_movement(self):
        """recall_file should record a RETURNED movement."""
        movement = FileMovementService.recall_file(
            file=self.file,
            recalled_by=self.sender,
            reason='Urgent need',
        )
        self.assertEqual(movement.action, 'RETURNED')

    def test_recall_file_validates_recalled_by(self):
        """recall_file should raise ValueError if recalled_by is not the previous sender."""
        stranger = User.objects.create_user(
            email='stranger@test.gov.ng',
            password='TestPass123!@#',
            first_name='Stranger',
            last_name='User',
            role='TCH'
        )
        with self.assertRaises(ValueError):
            FileMovementService.recall_file(
                file=self.file,
                recalled_by=stranger,
            )


class FileMovementServiceEscalateFileTest(TestCase):
    """Tests for FileMovementService.escalate_file."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.gov.ng',
            password='TestPass123!@#',
            first_name='User',
            last_name='Test',
            role='SYSADMIN'
        )
        self.file = FileMovementService.create_file(
            title='Escalate File',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.user,
        )

    def test_escalate_file_returns_movement(self):
        """escalate_file should return a FileMovement instance."""
        movement = FileMovementService.escalate_file(
            file=self.file,
            escalated_by=self.user,
            reason='Needs attention',
        )
        self.assertIsInstance(movement, FileMovement)

    def test_escalate_file_increments_priority_normal_to_high(self):
        """Escalating NORMAL priority should make it HIGH."""
        FileMovementService.escalate_file(
            file=self.file,
            escalated_by=self.user,
        )
        self.file.refresh_from_db()
        self.assertEqual(self.file.priority, 'HIGH')

    def test_escalate_file_increments_priority_high_to_urgent(self):
        """Escalating HIGH priority should make it URGENT."""
        self.file.priority = 'HIGH'
        self.file.save()
        FileMovementService.escalate_file(
            file=self.file,
            escalated_by=self.user,
        )
        self.file.refresh_from_db()
        self.assertEqual(self.file.priority, 'URGENT')

    def test_escalate_file_records_escalated_movement(self):
        """escalate_file should record ESCALATED movement."""
        movement = FileMovementService.escalate_file(
            file=self.file,
            escalated_by=self.user,
            reason='Critical issue',
        )
        self.assertEqual(movement.action, 'ESCALATED')
        self.assertEqual(movement.remarks, 'Critical issue')

    def test_escalate_file_adds_to_timeline(self):
        """escalate_file should add entry to status_timeline."""
        FileMovementService.escalate_file(
            file=self.file,
            escalated_by=self.user,
        )
        self.file.refresh_from_db()
        self.assertGreaterEqual(len(self.file.status_timeline), 1)


class FileMovementServiceArchiveFileTest(TestCase):
    """Tests for FileMovementService.archive_file."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.gov.ng',
            password='TestPass123!@#',
            first_name='User',
            last_name='Test',
            role='SYSADMIN'
        )

    def test_archive_closed_file(self):
        """Archiving a CLOSED file should work."""
        file_obj = FileMovementService.create_file(
            title='Archive File',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.user,
        )
        file_obj.status = 'CLOSED'
        file_obj.save()
        movement = FileMovementService.archive_file(
            file=file_obj,
            archived_by=self.user,
        )
        file_obj.refresh_from_db()
        self.assertEqual(file_obj.status, 'ARCHIVED')
        self.assertEqual(movement.action, 'ARCHIVED')

    def test_archive_rejects_non_closed_file(self):
        """Archiving a non-CLOSED file should raise ValueError."""
        file_obj = FileMovementService.create_file(
            title='Active File',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.user,
        )
        with self.assertRaises(ValueError):
            FileMovementService.archive_file(
                file=file_obj,
                archived_by=self.user,
            )

    def test_archive_records_movement(self):
        """archive_file should record ARCHIVED movement."""
        file_obj = FileMovementService.create_file(
            title='Archive Movement',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.user,
        )
        file_obj.status = 'CLOSED'
        file_obj.save()
        movement = FileMovementService.archive_file(
            file=file_obj,
            archived_by=self.user,
            notes='Archived per policy',
        )
        self.assertEqual(movement.action, 'ARCHIVED')
        self.assertEqual(movement.remarks, 'Archived per policy')


class FileMovementServiceGetFileTimelineTest(TestCase):
    """Tests for FileMovementService.get_file_timeline."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.gov.ng',
            password='TestPass123!@#',
            first_name='User',
            last_name='Test',
            role='SYSADMIN'
        )
        self.receiver = User.objects.create_user(
            email='receiver@test.gov.ng',
            password='TestPass123!@#',
            first_name='Receiver',
            last_name='User',
            role='TCH'
        )

    def test_get_timeline_empty(self):
        """Timeline for newly created file should have at least the CREATED entry."""
        file_obj = FileMovementService.create_file(
            title='Timeline File',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.user,
        )
        timeline = FileMovementService.get_file_timeline(file_obj)
        self.assertIsInstance(timeline, list)
        self.assertGreaterEqual(len(timeline), 1)

    def test_get_timeline_chronological(self):
        """Timeline entries should be in chronological order."""
        file_obj = FileMovementService.create_file(
            title='Timeline File 2',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.user,
        )
        FileMovementService.move_file(
            file=file_obj,
            from_holder=self.user,
            to_holder=self.receiver,
            action='FORWARDED',
        )
        timeline = FileMovementService.get_file_timeline(file_obj)
        self.assertGreaterEqual(len(timeline), 2)
        # Check chronological order
        for i in range(len(timeline) - 1):
            self.assertLessEqual(
                timeline[i]['timestamp'],
                timeline[i + 1]['timestamp']
            )


class FileMovementServiceGetUserPendingFilesTest(TestCase):
    """Tests for FileMovementService.get_user_pending_files."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.gov.ng',
            password='TestPass123!@#',
            first_name='User',
            last_name='Test',
            role='SYSADMIN'
        )
        self.other = User.objects.create_user(
            email='other@test.gov.ng',
            password='TestPass123!@#',
            first_name='Other',
            last_name='User',
            role='TCH'
        )

    def test_returns_active_files_held_by_user(self):
        """Should return files where user is current_holder with ACTIVE status."""
        file_obj = FileMovementService.create_file(
            title='Active File',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.user,
        )
        file_obj.status = 'ACTIVE'
        file_obj.save()
        files = FileMovementService.get_user_pending_files(self.user)
        self.assertIn(file_obj, files)

    def test_returns_pending_files_held_by_user(self):
        """Should return files with PENDING status held by user."""
        file_obj = FileMovementService.create_file(
            title='Pending File',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.user,
        )
        file_obj.status = 'PENDING'
        file_obj.save()
        files = FileMovementService.get_user_pending_files(self.user)
        self.assertIn(file_obj, files)

    def test_excludes_draft_files(self):
        """Should not return DRAFT files."""
        file_obj = FileMovementService.create_file(
            title='Draft File',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.user,
        )
        files = FileMovementService.get_user_pending_files(self.user)
        self.assertNotIn(file_obj, files)

    def test_excludes_other_users_files(self):
        """Should not return files held by other users."""
        file_obj = FileMovementService.create_file(
            title='Other File',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.user,
        )
        file_obj.status = 'ACTIVE'
        file_obj.current_holder = self.other
        file_obj.save()
        files = FileMovementService.get_user_pending_files(self.user)
        self.assertNotIn(file_obj, files)


class FileMovementServiceGetDepartmentFilesTest(TestCase):
    """Tests for FileMovementService.get_department_files."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.gov.ng',
            password='TestPass123!@#',
            first_name='User',
            last_name='Test',
            role='SYSADMIN'
        )
        from apps.departments.models import Department
        self.dept = Department.objects.create(name='Finance', code='FIN', category='CORE')
        self.other_dept = Department.objects.create(name='HR', code='HR', category='SUPPORT')

    def test_returns_department_files(self):
        """Should return files belonging to the department."""
        file_obj = FileMovementService.create_file(
            title='Dept File',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.user,
            department=self.dept,
        )
        files = FileMovementService.get_department_files(self.dept)
        self.assertIn(file_obj, files)

    def test_filters_by_status(self):
        """Should filter by status when provided."""
        file_obj = FileMovementService.create_file(
            title='Active Dept File',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.user,
            department=self.dept,
        )
        file_obj.status = 'ACTIVE'
        file_obj.save()

        draft_file = FileMovementService.create_file(
            title='Draft Dept File',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.user,
            department=self.dept,
        )
        files = FileMovementService.get_department_files(self.dept, status='ACTIVE')
        self.assertIn(file_obj, files)
        self.assertNotIn(draft_file, files)

    def test_excludes_other_departments(self):
        """Should not return files from other departments."""
        file_obj = FileMovementService.create_file(
            title='Finance File',
            file_type='MEMO',
            file_category='ADMIN',
            description='',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.user,
            department=self.dept,
        )
        files = FileMovementService.get_department_files(self.other_dept)
        self.assertNotIn(file_obj, files)


class FileMovementServiceSearchFilesTest(TestCase):
    """Tests for FileMovementService.search_files."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.gov.ng',
            password='TestPass123!@#',
            first_name='User',
            last_name='Test',
            role='SYSADMIN'
        )
        self.file1 = FileMovementService.create_file(
            title='Budget Report',
            file_type='REPORT',
            file_category='FIN',
            description='Annual budget report',
            classification='CONFIDENTIAL',
            priority='HIGH',
            created_by=self.user,
            tags=['budget', 'annual'],
        )
        self.file2 = FileMovementService.create_file(
            title='Staff Meeting Minutes',
            file_type='MINUTES',
            file_category='ADMIN',
            description='Minutes from staff meeting',
            classification='PUBLIC',
            priority='NORMAL',
            created_by=self.user,
        )

    def test_search_no_filters(self):
        """Without filters, should return all files."""
        results = FileMovementService.search_files()
        self.assertIn(self.file1, results)
        self.assertIn(self.file2, results)

    def test_search_by_query(self):
        """Query should search title and description."""
        results = FileMovementService.search_files(query='budget')
        self.assertIn(self.file1, results)

    def test_search_by_file_type(self):
        """Should filter by file_type."""
        results = FileMovementService.search_files(file_type='REPORT')
        self.assertIn(self.file1, results)
        self.assertNotIn(self.file2, results)

    def test_search_by_status(self):
        """Should filter by status."""
        self.file1.status = 'ACTIVE'
        self.file1.save()
        results = FileMovementService.search_files(status='ACTIVE')
        self.assertIn(self.file1, results)

    def test_search_by_classification(self):
        """Should filter by classification."""
        results = FileMovementService.search_files(classification='CONFIDENTIAL')
        self.assertIn(self.file1, results)
        self.assertNotIn(self.file2, results)

    def test_search_by_priority(self):
        """Should filter by priority."""
        results = FileMovementService.search_files(priority='HIGH')
        self.assertIn(self.file1, results)
        self.assertNotIn(self.file2, results)

    def test_search_by_created_by(self):
        """Should filter by created_by."""
        results = FileMovementService.search_files(created_by=self.user.id)
        self.assertIn(self.file1, results)

    def test_search_by_current_holder(self):
        """Should filter by current_holder."""
        results = FileMovementService.search_files(current_holder=self.user.id)
        self.assertIn(self.file1, results)

    def test_search_by_date_range(self):
        """Should filter by date range."""
        today = date.today()
        results = FileMovementService.search_files(date_from=today, date_to=today)
        self.assertIn(self.file1, results)

    def test_search_by_department(self):
        """Should filter by department."""
        from apps.departments.models import Department
        dept = Department.objects.create(name='Finance', code='FIN', category='CORE')
        self.file1.department = dept
        self.file1.save()
        results = FileMovementService.search_files(department=dept.id)
        self.assertIn(self.file1, results)
        self.assertNotIn(self.file2, results)
