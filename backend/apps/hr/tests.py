from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.schools.models import School
from apps.departments.models import Department
from apps.staff.models import Staff
from .models import JobPosting, JobApplication, PayrollPeriod, Payslip

User = get_user_model()


class JobPostingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='hr@test.com', password='TestPass123!',
            first_name='HR', last_name='Head', role='HR'
        )
        self.dept = Department.objects.create(name='HR', code='HR', category='CORE')
        self.posting = JobPosting.objects.create(
            title='Math Teacher', description='Teach mathematics',
            department=self.dept, created_by=self.user,
            closing_date='2026-12-31'
        )

    def test_posting_str(self):
        self.assertEqual(str(self.posting), 'Math Teacher')


class PayrollPeriodModelTest(TestCase):
    def setUp(self):
        self.period = PayrollPeriod.objects.create(
            name='January 2026', start_date='2026-01-01',
            end_date='2026-01-31', payment_date='2026-02-05'
        )

    def test_period_str(self):
        self.assertEqual(str(self.period), 'January 2026')


class PayslipModelTest(TestCase):
    def setUp(self):
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
        self.period = PayrollPeriod.objects.create(
            name='Jan 2026', start_date='2026-01-01',
            end_date='2026-01-31', payment_date='2026-02-05'
        )
        self.payslip = Payslip.objects.create(
            staff=self.staff, period=self.period,
            basic_salary=100000, allowances=20000,
            deductions=5000, tax=10000, pension=5000
        )

    def test_payslip_str(self):
        self.assertIn('Staff Member', str(self.payslip))

    def test_net_salary_calculation(self):
        self.assertEqual(self.payslip.net_salary, 100000)


class HRAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com', password='TestPass123!',
            first_name='Test', last_name='User', role='SYSADMIN'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')
        self.dept = Department.objects.create(name='HR', code='HR', category='CORE')
        self.posting = JobPosting.objects.create(
            title='Teacher', description='Teach', department=self.dept,
            created_by=self.user, closing_date='2026-12-31'
        )

    def test_list_job_postings(self):
        response = self.client.get('/api/hr/job-postings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_job_posting(self):
        response = self.client.post('/api/hr/job-postings/', {
            'title': 'Vice Principal', 'description': 'Lead school',
            'department': self.dept.id, 'closing_date': '2026-12-31',
            'created_by': self.user.id, 'requirements': 'Masters degree'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_payroll_periods(self):
        response = self.client.get('/api/hr/payroll-periods/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
