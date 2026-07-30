from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.schools.models import School
from .models import AuditLog, ComplianceItem, ComplianceRecord, Violation

User = get_user_model()


class AuditLogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='auditor@test.com', password='TestPass123!',
            first_name='Auditor', last_name='One', role='SYSADMIN'
        )
        self.log = AuditLog.objects.create(
            user=self.user, action='CREATE', module='students',
            object_type='Student', object_id='1',
            object_repr='Test Student', description='Created student record',
            ip_address='127.0.0.1'
        )

    def test_log_str(self):
        self.assertIn('CREATE', str(self.log))


class ComplianceItemModelTest(TestCase):
    def setUp(self):
        self.item = ComplianceItem.objects.create(
            category='FINANCIAL', title='Annual Budget Approval',
            description='Budget must be approved by board',
            frequency='Annual', is_mandatory=True
        )

    def test_item_str(self):
        self.assertIn('Annual Budget Approval', str(self.item))


class ComplianceRecordModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com', password='TestPass123!',
            first_name='User', last_name='One', role='SYSADMIN'
        )
        self.school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.item = ComplianceItem.objects.create(
            category='FINANCIAL', title='Budget Report',
            description='Submit annual budget', frequency='Annual'
        )
        self.record = ComplianceRecord.objects.create(
            item=self.item, school=self.school,
            academic_year='2025/2026', due_date='2026-06-30',
            created_by=self.user
        )

    def test_record_str(self):
        self.assertIn('Budget Report', str(self.record))


class ViolationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='reporter@test.com', password='TestPass123!',
            first_name='Reporter', last_name='One', role='SYSADMIN'
        )
        self.school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.violation = Violation.objects.create(
            title='Late Fee Submission', description='Fees submitted past deadline',
            severity='MEDIUM', category='FINANCIAL', school=self.school,
            reported_by=self.user, incident_date='2026-01-15'
        )

    def test_violation_str(self):
        self.assertIn('Late Fee Submission', str(self.violation))


class AuditAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com', password='TestPass123!',
            first_name='Test', last_name='User', role='SYSADMIN'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

    def test_list_audit_logs(self):
        response = self.client.get('/api/audit/logs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_compliance_items(self):
        response = self.client.get('/api/audit/compliance-items/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_violations(self):
        response = self.client.get('/api/audit/violations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
