"""Tests for ClassificationService."""
from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.files.models import File, FileClassification
from apps.files.services.classification_service import ClassificationService

User = get_user_model()


class ClassificationServiceClassifyFileTest(TestCase):
    """Tests for ClassificationService.classify_file."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.gov.ng',
            password='TestPass123!@#',
            first_name='User',
            last_name='Test',
            role='SYSADMIN'
        )

    def test_classify_file_returns_file_classification(self):
        """classify_file should return a FileClassification instance."""
        file_obj = File.objects.create(
            file_number='FIL-2026-TEST-0001',
            title='Budget Report',
            file_type='REPORT',
            file_category='FIN',
            description='Annual budget report for the district',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        result = ClassificationService.classify_file(file_obj)
        self.assertIsInstance(result, FileClassification)

    def test_classify_finance_file(self):
        """Finance-related file should be classified as Finance department."""
        file_obj = File.objects.create(
            file_number='FIL-2026-TEST-0002',
            title='Budget Expenditure Report',
            file_type='REPORT',
            file_category='FIN',
            description='This is a financial expenditure report with payment details and invoices',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        result = ClassificationService.classify_file(file_obj)
        self.assertEqual(result.suggested_department, 'Finance')
        self.assertGreater(result.department_confidence, 0)

    def test_classify_academic_file(self):
        """Academic-related file should be classified as Academic department."""
        file_obj = File.objects.create(
            file_number='FIL-2026-TEST-0003',
            title='Exam Results Summary',
            file_type='REPORT',
            file_category='ACAD',
            description='Student exam results and grading for the academic session',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        result = ClassificationService.classify_file(file_obj)
        self.assertEqual(result.suggested_department, 'Academic')

    def test_classify_hr_file(self):
        """HR-related file should be classified as HR department."""
        file_obj = File.objects.create(
            file_number='FIL-2026-TEST-0004',
            title='Staff Appointment Letter',
            file_type='CORRESPONDENCE',
            file_category='ADMIN',
            description='Staff recruitment and appointment documentation',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        result = ClassificationService.classify_file(file_obj)
        self.assertEqual(result.suggested_department, 'HR')

    def test_classify_inspection_file(self):
        """Inspection-related file should be classified as Inspection department."""
        file_obj = File.objects.create(
            file_number='FIL-2026-TEST-0005',
            title='School Inspection Report',
            file_type='REPORT',
            file_category='INSP',
            description='Inspection monitoring and compliance verification',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        result = ClassificationService.classify_file(file_obj)
        self.assertEqual(result.suggested_department, 'Inspection')

    def test_classify_discipline_file(self):
        """Discipline-related file should be classified as Discipline department."""
        file_obj = File.objects.create(
            file_number='FIL-2026-TEST-0006',
            title='Disciplinary Complaint',
            file_type='CORRESPONDENCE',
            file_category='DISC',
            description='Misconduct complaint and disciplinary investigation',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        result = ClassificationService.classify_file(file_obj)
        self.assertEqual(result.suggested_department, 'Discipline')

    def test_classify_urgent_file(self):
        """File with urgent keywords should be classified as URGENT."""
        file_obj = File.objects.create(
            file_number='FIL-2026-TEST-0007',
            title='Urgent: Emergency Meeting',
            file_type='MEMO',
            file_category='ADMIN',
            description='This is an emergency and critical issue requiring immediate attention',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        result = ClassificationService.classify_file(file_obj)
        self.assertEqual(result.urgency, 'URGENT')

    def test_classify_high_priority_file(self):
        """File with important keywords should be classified as HIGH urgency."""
        file_obj = File.objects.create(
            file_number='FIL-2026-TEST-0008',
            title='Important Priority Review',
            file_type='MEMO',
            file_category='ADMIN',
            description='Important and priority document requiring time-sensitive action',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        result = ClassificationService.classify_file(file_obj)
        self.assertEqual(result.urgency, 'HIGH')

    def test_classify_low_priority_file(self):
        """File with FYI keywords should be classified as LOW urgency."""
        file_obj = File.objects.create(
            file_number='FIL-2026-TEST-0009',
            title='For Your Information Update',
            file_type='MEMO',
            file_category='ADMIN',
            description='General information update for your information',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        result = ClassificationService.classify_file(file_obj)
        self.assertEqual(result.urgency, 'LOW')

    def test_classify_restricted_file(self):
        """File with confidential keywords should be RESTRICTED sensitivity."""
        file_obj = File.objects.create(
            file_number='FIL-2026-TEST-0010',
            title='Confidential Staff Records',
            file_type='CORRESPONDENCE',
            file_category='ADMIN',
            description='This is a confidential and restricted document for private use',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        result = ClassificationService.classify_file(file_obj)
        self.assertEqual(result.sensitivity, 'RESTRICTED')

    def test_classify_public_file(self):
        """File with public keywords should be PUBLIC sensitivity."""
        file_obj = File.objects.create(
            file_number='FIL-2026-TEST-0011',
            title='Public Announcement Circular',
            file_type='CIRCULAR',
            file_category='ADMIN',
            description='General public announcement and circular for everyone',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        result = ClassificationService.classify_file(file_obj)
        self.assertEqual(result.sensitivity, 'PUBLIC')

    def test_classify_extracts_keywords(self):
        """classify_file should extract relevant keywords from the text."""
        file_obj = File.objects.create(
            file_number='FIL-2026-TEST-0012',
            title='Budget Invoice Payment',
            file_type='INVOICE',
            file_category='FIN',
            description='Payment invoice for budget expenditure and audit',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        result = ClassificationService.classify_file(file_obj)
        self.assertIsInstance(result.keywords, list)
        self.assertGreater(len(result.keywords), 0)
        # Should contain some of the finance keywords
        keyword_text = ' '.join(result.keywords).lower()
        self.assertTrue(
            any(kw in keyword_text for kw in ['budget', 'invoice', 'payment', 'expenditure', 'audit'])
        )

    def test_classify_saves_classification(self):
        """classify_file should persist the FileClassification."""
        file_obj = File.objects.create(
            file_number='FIL-2026-TEST-0013',
            title='Saved Classification File',
            file_type='MEMO',
            file_category='ADMIN',
            description='A file for testing persistence',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        ClassificationService.classify_file(file_obj)
        self.assertTrue(FileClassification.objects.filter(file=file_obj).exists())

    def test_classify_updates_existing(self):
        """Second classify_file call should update, not create duplicate."""
        file_obj = File.objects.create(
            file_number='FIL-2026-TEST-0014',
            title='Update Test File',
            file_type='MEMO',
            file_category='ADMIN',
            description='First description with budget',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        ClassificationService.classify_file(file_obj)
        count1 = FileClassification.objects.filter(file=file_obj).count()

        # Update and classify again
        file_obj.description = 'Updated with invoice and payment'
        file_obj.save()
        ClassificationService.classify_file(file_obj)
        count2 = FileClassification.objects.filter(file=file_obj).count()

        self.assertEqual(count1, 1)  # Still only one
        self.assertEqual(count2, 1)  # Still only one

    def test_classify_empty_file(self):
        """File with empty title and description should still classify without error."""
        file_obj = File.objects.create(
            file_number='FIL-2026-TEST-0015',
            title='',
            file_type='OTHER',
            file_category='ADMIN',
            description='',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        result = ClassificationService.classify_file(file_obj)
        self.assertIsInstance(result, FileClassification)
        self.assertEqual(result.overall_confidence, 0.0)

    def test_classify_confidence_range(self):
        """Confidence scores should be between 0 and 1."""
        file_obj = File.objects.create(
            file_number='FIL-2026-TEST-0016',
            title='Budget Report for Audit',
            file_type='REPORT',
            file_category='FIN',
            description='Financial audit report with budget and expenditure details',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        result = ClassificationService.classify_file(file_obj)
        self.assertGreaterEqual(result.department_confidence, 0.0)
        self.assertLessEqual(result.department_confidence, 1.0)
        self.assertGreaterEqual(result.overall_confidence, 0.0)
        self.assertLessEqual(result.overall_confidence, 1.0)

    def test_classify_with_tags(self):
        """Tags should be included in the classification text."""
        file_obj = File.objects.create(
            file_number='FIL-2026-TEST-0017',
            title='Tagged File',
            file_type='MEMO',
            file_category='ADMIN',
            description='A file with tags',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
            tags=['curriculum', 'exam', 'student'],
        )
        result = ClassificationService.classify_file(file_obj)
        self.assertEqual(result.suggested_department, 'Academic')

    def test_classify_file_type_suggestion(self):
        """file_type_suggestion should match the file's file_type."""
        file_obj = File.objects.create(
            file_number='FIL-2026-TEST-0018',
            title='Report File',
            file_type='REPORT',
            file_category='ADMIN',
            description='A report',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        result = ClassificationService.classify_file(file_obj)
        self.assertEqual(result.file_type_suggestion, 'REPORT')


class ClassificationServiceGetSuggestionsTest(TestCase):
    """Tests for ClassificationService.get_classification_suggestions."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.gov.ng',
            password='TestPass123!@#',
            first_name='User',
            last_name='Test',
            role='SYSADMIN'
        )

    def test_returns_dict(self):
        """get_classification_suggestions should return a dictionary."""
        file_obj = File.objects.create(
            file_number='FIL-2026-SUGG-0001',
            title='Budget Report',
            file_type='REPORT',
            file_category='FIN',
            description='Financial budget report',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        result = ClassificationService.get_classification_suggestions(file_obj)
        self.assertIsInstance(result, dict)

    def test_dict_has_expected_keys(self):
        """Suggestion dict should have expected keys."""
        file_obj = File.objects.create(
            file_number='FIL-2026-SUGG-0002',
            title='Staff Meeting',
            file_type='MINUTES',
            file_category='ADMIN',
            description='Meeting minutes',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        result = ClassificationService.get_classification_suggestions(file_obj)
        self.assertIn('suggested_department', result)
        self.assertIn('department_confidence', result)
        self.assertIn('urgency', result)
        self.assertIn('sensitivity', result)
        self.assertIn('keywords', result)
        self.assertIn('overall_confidence', result)

    def test_does_not_save(self):
        """get_classification_suggestions should not create a FileClassification."""
        file_obj = File.objects.create(
            file_number='FIL-2026-SUGG-0003',
            title='No Save File',
            file_type='MEMO',
            file_category='ADMIN',
            description='Should not be saved',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        ClassificationService.get_classification_suggestions(file_obj)
        self.assertFalse(FileClassification.objects.filter(file=file_obj).exists())


class ClassificationServiceBulkClassifyTest(TestCase):
    """Tests for ClassificationService.bulk_classify."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.gov.ng',
            password='TestPass123!@#',
            first_name='User',
            last_name='Test',
            role='SYSADMIN'
        )

    def test_bulk_classify_all(self):
        """bulk_classify without file_ids should classify all files."""
        File.objects.create(
            file_number='FIL-2026-BULK-0001',
            title='Budget File',
            file_type='REPORT',
            file_category='FIN',
            description='Budget report',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        File.objects.create(
            file_number='FIL-2026-BULK-0002',
            title='Exam Results',
            file_type='REPORT',
            file_category='ACAD',
            description='Student exam results',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        results = ClassificationService.bulk_classify()
        self.assertEqual(len(results), 2)

    def test_bulk_classify_specific_ids(self):
        """bulk_classify with file_ids should classify only those files."""
        f1 = File.objects.create(
            file_number='FIL-2026-BULK-0003',
            title='Budget Invoice',
            file_type='INVOICE',
            file_category='FIN',
            description='Budget invoice',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        File.objects.create(
            file_number='FIL-2026-BULK-0004',
            title='Exam Results',
            file_type='REPORT',
            file_category='ACAD',
            description='Exam results',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        results = ClassificationService.bulk_classify(file_ids=[f1.id])
        self.assertEqual(len(results), 1)

    def test_bulk_classify_empty(self):
        """bulk_classify on empty DB should return empty list."""
        results = ClassificationService.bulk_classify()
        self.assertEqual(results, [])

    def test_bulk_classify_saves_all(self):
        """bulk_classify should persist all classifications."""
        f1 = File.objects.create(
            file_number='FIL-2026-BULK-0005',
            title='Staff Transfer',
            file_type='CORRESPONDENCE',
            file_category='ADMIN',
            description='Staff transfer letter',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        f2 = File.objects.create(
            file_number='FIL-2026-BULK-0006',
            title='Vehicle Maintenance',
            file_type='REPORT',
            file_category='ADMIN',
            description='Bus vehicle transport maintenance',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        ClassificationService.bulk_classify()
        self.assertTrue(FileClassification.objects.filter(file=f1).exists())
        self.assertTrue(FileClassification.objects.filter(file=f2).exists())

    def test_bulk_classify_transport_file(self):
        """Transport-related file should be classified accordingly."""
        f = File.objects.create(
            file_number='FIL-2026-BULK-0007',
            title='Bus Route Maintenance',
            file_type='REPORT',
            file_category='ADMIN',
            description='Vehicle bus driver transport route maintenance',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )
        results = ClassificationService.bulk_classify(file_ids=[f.id])
        self.assertEqual(results[0].suggested_department, 'Transport')
