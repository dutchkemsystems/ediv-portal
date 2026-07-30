from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal
from .models import CPDActivity, CPDEnrollment, CPDRecord

User = get_user_model()


class CPDActivityModelTest(TestCase):
    def setUp(self):
        self.activity = CPDActivity.objects.create(
            title='Teaching Methods Workshop', training_type='WORKSHOP',
            description='Modern teaching methods', provider='Lagos Education Board',
            start_date='2026-03-01', end_date='2026-03-03',
            duration_hours=Decimal('24.00'), cost=Decimal('50000.00')
        )

    def test_activity_str(self):
        self.assertEqual(str(self.activity), 'Teaching Methods Workshop')


class CPDRecordModelTest(TestCase):
    def setUp(self):
        from apps.schools.models import School
        from apps.staff.models import Staff
        self.user = User.objects.create_user(
            email='staff@test.com', password='TestPass123!',
            first_name='Staff', last_name='Member', role='TCH'
        )
        school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.staff = Staff.objects.create(
            user=self.user, staff_id='STF001', employee_number='EMP001',
            school=school, category='TEACHING', designation='TEACHER',
            employment_type='PERMANENT', qualification='Bachelors',
            date_of_birth='1990-01-01', gender='M', marital_status='SINGLE',
            state_of_origin='Lagos', lga_of_origin='Mainland',
            residential_address='123 Street', emergency_contact_name='Emergency',
            emergency_contact_phone='08012345678', bank_name='GTBank',
            bank_account_number='0123456789', bank_account_name='Staff Member',
            date_joined='2020-01-01'
        )
        self.record = CPDRecord.objects.create(
            staff=self.staff, academic_year='2025/2026',
            total_hours_required=Decimal('40.00'),
            total_hours_completed=Decimal('30.00'),
            activities_completed=3, certificates_earned=2
        )

    def test_record_str(self):
        self.assertIn('Staff Member', str(self.record))

    def test_completion_percentage(self):
        self.assertEqual(self.record.completion_percentage, 75.0)


class CPDAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com', password='TestPass123!',
            first_name='Test', last_name='User', role='SYSADMIN'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

    def test_list_activities(self):
        response = self.client.get('/api/cpd/activities/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_activity(self):
        response = self.client.post('/api/cpd/activities/', {
            'title': 'New Workshop', 'training_type': 'SEMINAR',
            'description': 'Test', 'provider': 'Test Provider',
            'start_date': '2026-04-01', 'end_date': '2026-04-02',
            'duration_hours': '8.00'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
