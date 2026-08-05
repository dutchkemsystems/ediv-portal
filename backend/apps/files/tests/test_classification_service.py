"""Tests for ClassificationService."""
from django.test import TestCase
from apps.users.models import User
from apps.files.models import File, FileClassification
from apps.files.services.classification_service import ClassificationService


class ClassificationServiceClassifyTest(TestCase):
    """Tests for ClassificationService.classify_file."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='class@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Class',
            last_name='User',
            role='SYSADMIN'
        )

    def test_classify_finance_file(self):
        """File with finance keywords should be classified as Finance."""
        file_obj = File.objects.create(
            file_number='EDIV-2026-CLS-001',
            title='Budget Payment Invoice',
            file_type='CORRESPONDENCE',
            file_category='FIN',
            description='Payment invoice for school supplies budget expenditure',
            created_by=self.user,
            current_holder=self.user,
        )
        classification = ClassificationService.classify_file(file=file_obj)
        self.assertIsInstance(classification, FileClassification)
        self.assertEqual(classification.suggested_department, 'Finance')
        self.assertIn('budget', classification.keywords)

    def test_classify_hr_file(self):
        """File with HR keywords should be classified as HR."""
        file_obj = File.objects.create(
            file_number='EDIV-2026-CLS-002',
            title='Staff Transfer Memo',
            file_type='MEMO',
            file_category='ADMIN',
            description='Staff appointment transfer promotion letter',
            created_by=self.user,
            current_holder=self.user,
        )
        classification = ClassificationService.classify_file(file=file_obj)
        self.assertEqual(classification.suggested_department, 'HR')

    def test_classify_urgent_file(self):
        """File with urgency keywords should be marked URGENT."""
        file_obj = File.objects.create(
            file_number='EDIV-2026-CLS-003',
            title='Emergency Meeting',
            file_type='MEMO',
            file_category='ADMIN',
            description='URGENT emergency meeting required immediately',
            created_by=self.user,
            current_holder=self.user,
        )
        classification = ClassificationService.classify_file(file=file_obj)
        self.assertEqual(classification.urgency, 'URGENT')

    def test_classify_confidential_file(self):
        """File with sensitivity keywords should be RESTRICTED."""
        file_obj = File.objects.create(
            file_number='EDIV-2026-CLS-004',
            title='Confidential Report',
            file_type='REPORT',
            file_category='ADMIN',
            description='This is confidential restricted information',
            created_by=self.user,
            current_holder=self.user,
        )
        classification = ClassificationService.classify_file(file=file_obj)
        self.assertEqual(classification.sensitivity, 'RESTRICTED')

    def test_classify_generic_file(self):
        """Generic file should have default classification."""
        file_obj = File.objects.create(
            file_number='EDIV-2026-CLS-005',
            title='General Note',
            file_type='OTHER',
            file_category='ADMIN',
            description='A simple note',
            created_by=self.user,
            current_holder=self.user,
        )
        classification = ClassificationService.classify_file(file=file_obj)
        self.assertEqual(classification.urgency, 'MEDIUM')
        self.assertEqual(classification.sensitivity, 'PUBLIC')

    def test_get_classification_suggestions(self):
        """get_classification_suggestions should return dict without saving."""
        file_obj = File.objects.create(
            file_number='EDIV-2026-CLS-006',
            title='Inspection Report',
            file_type='REPORT',
            file_category='ADMIN',
            description='Inspection monitoring compliance assessment',
            created_by=self.user,
            current_holder=self.user,
        )
        suggestions = ClassificationService.get_classification_suggestions(file_obj)
        self.assertIsInstance(suggestions, dict)
        self.assertIn('suggested_department', suggestions)
        self.assertIn('urgency', suggestions)

    def test_bulk_classify(self):
        """bulk_classify should classify multiple files."""
        files = []
        for i in range(3):
            f = File.objects.create(
                file_number=f'EDIV-2026-BULK-{i:03d}',
                title=f'Budget Report {i}',
                file_type='REPORT',
                file_category='FIN',
                description='Financial budget expenditure report',
                created_by=self.user,
                current_holder=self.user,
            )
            files.append(f)
        results = ClassificationService.bulk_classify(file_ids=[f.id for f in files])
        self.assertEqual(len(results), 3)

    def test_classify_inspection_file(self):
        """File with inspection keywords should be classified as Inspection."""
        file_obj = File.objects.create(
            file_number='EDIV-2026-CLS-007',
            title='Inspection Assessment Report',
            file_type='REPORT',
            file_category='ADMIN',
            description='School inspection monitoring compliance verification',
            created_by=self.user,
            current_holder=self.user,
        )
        classification = ClassificationService.classify_file(file=file_obj)
        self.assertEqual(classification.suggested_department, 'Inspection')

    def test_classify_transport_file(self):
        """File with transport keywords should be classified as Transport."""
        file_obj = File.objects.create(
            file_number='EDIV-2026-CLS-008',
            title='Bus Route Maintenance',
            file_type='MEMO',
            file_category='ADMIN',
            description='Vehicle bus driver route maintenance schedule',
            created_by=self.user,
            current_holder=self.user,
        )
        classification = ClassificationService.classify_file(file=file_obj)
        self.assertEqual(classification.suggested_department, 'Transport')

    def test_classify_discipline_file(self):
        """File with discipline keywords should be classified as Discipline."""
        file_obj = File.objects.create(
            file_number='EDIV-2026-CLS-009',
            title='Misconduct Investigation',
            file_type='MEMO',
            file_category='ADMIN',
            description='Complaint disciplinary investigation misconduct',
            created_by=self.user,
            current_holder=self.user,
        )
        classification = ClassificationService.classify_file(file=file_obj)
        self.assertEqual(classification.suggested_department, 'Discipline')
