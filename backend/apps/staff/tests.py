import datetime
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.schools.models import School
from apps.departments.models import Department
from .models import Staff, StaffLeave, StaffPerformance

User = get_user_model()


def _create_staff_user(email='staff@test.com', **overrides):
    """Helper to create a staff object with proper date objects."""
    defaults = dict(
        email=email, password='TestPass123!',
        first_name='John', last_name='Doe', role='TCH'
    )
    defaults.update(overrides)
    user = User.objects.create_user(**defaults)
    return user


class StaffModelTest(TestCase):
    def setUp(self):
        self.user = _create_staff_user()
        self.school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.staff = Staff.objects.create(
            user=self.user, staff_id='STF001', employee_number='EMP001',
            school=self.school, category='TEACHING', designation='TEACHER',
            employment_type='PERMANENT', qualification='Bachelors',
            date_of_birth=datetime.date(1990, 1, 1), gender='M',
            marital_status='SINGLE', state_of_origin='Lagos',
            lga_of_origin='Mainland', residential_address='123 Street',
            emergency_contact_name='Emergency',
            emergency_contact_phone='08012345678', bank_name='GTBank',
            bank_account_number='0123456789', bank_account_name='John Doe',
            date_joined=datetime.date(2020, 1, 1)
        )

    def test_staff_str(self):
        self.assertIn('John Doe', str(self.staff))

    def test_years_of_service(self):
        self.assertGreaterEqual(self.staff.years_of_service, 0)


class StaffLeaveModelTest(TestCase):
    def setUp(self):
        self.user = _create_staff_user()
        school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.staff = Staff.objects.create(
            user=self.user, staff_id='STF001', employee_number='EMP001',
            school=school, category='TEACHING', designation='TEACHER',
            employment_type='PERMANENT', qualification='Bachelors',
            date_of_birth=datetime.date(1990, 1, 1), gender='M',
            marital_status='SINGLE', state_of_origin='Lagos',
            lga_of_origin='Mainland', residential_address='123 Street',
            emergency_contact_name='Emergency',
            emergency_contact_phone='08012345678', bank_name='GTBank',
            bank_account_number='0123456789', bank_account_name='John Doe',
            date_joined=datetime.date(2020, 1, 1)
        )
        self.leave = StaffLeave.objects.create(
            staff=self.staff, leave_type='ANNUAL',
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2026, 1, 5),
            reason='Vacation'
        )

    def test_leave_str(self):
        self.assertIn('ANNUAL', str(self.leave))

    def test_duration_days(self):
        self.assertEqual(self.leave.duration_days, 5)


class StaffAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com', password='TestPass123!',
            first_name='Test', last_name='User', role='SYSADMIN'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')
        self.school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.staff_user = User.objects.create_user(
            email='staff@test.com', password='TestPass123!',
            first_name='Staff', last_name='Member', role='TCH'
        )
        self.staff = Staff.objects.create(
            user=self.staff_user, staff_id='STF001', employee_number='EMP001',
            school=self.school, category='TEACHING', designation='TEACHER',
            employment_type='PERMANENT', qualification='Bachelors',
            date_of_birth=datetime.date(1990, 1, 1), gender='M',
            marital_status='SINGLE', state_of_origin='Lagos',
            lga_of_origin='Mainland', residential_address='123 Street',
            emergency_contact_name='Emergency',
            emergency_contact_phone='08012345678', bank_name='GTBank',
            bank_account_number='0123456789', bank_account_name='Staff Member',
            date_joined=datetime.date(2020, 1, 1)
        )

    def test_list_staff(self):
        response = self.client.get('/api/staff/staff/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_staff(self):
        new_user = User.objects.create_user(
            email='new@test.com', password='TestPass123!',
            first_name='New', last_name='Staff', role='TCH'
        )
        response = self.client.post('/api/staff/staff/', {
            'user_id': new_user.id, 'staff_id': 'STF002',
            'employee_number': 'EMP002', 'school': self.school.id,
            'category': 'TEACHING', 'designation': 'TEACHER',
            'employment_type': 'PERMANENT', 'qualification': 'Bachelors',
            'date_of_birth': '1995-01-01', 'gender': 'M',
            'marital_status': 'SINGLE', 'state_of_origin': 'Lagos',
            'lga_of_origin': 'Mainland', 'residential_address': '123 Street',
            'emergency_contact_name': 'Emergency',
            'emergency_contact_phone': '08012345678', 'bank_name': 'GTBank',
            'bank_account_number': '0123456790', 'bank_account_name': 'New Staff',
            'date_joined': '2024-01-01'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_staff(self):
        response = self.client.get(f'/api/staff/staff/{self.staff.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
