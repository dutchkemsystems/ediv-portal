from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import User
from apps.schools.models import School
from .models import FeeStructure, StudentFee, Payment, Budget


class FeeStructureModelTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Test School',
            code='TS001',
            school_type='SENIOR',
            lga='APAPA',
            address='123 Street'
        )
        self.fee = FeeStructure.objects.create(
            school=self.school,
            name='Tuition Fee',
            fee_type='TUITION',
            amount=50000,
            academic_year='2024/2025',
            term='FIRST'
        )
    
    def test_fee_str(self):
        self.assertEqual(str(self.fee), 'Test School - Tuition Fee (50000.00)')


class StudentFeeModelTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Test School',
            code='TS001',
            school_type='SENIOR',
            lga='APAPA',
            address='123 Street'
        )
        self.user = User.objects.create_user(
            email='student@test.com',
            password='TestPass123!@#',
            first_name='Jane',
            last_name='Smith',
            role='STD'
        )
        from apps.students.models import Student
        self.student = Student.objects.create(
            user=self.user,
            admission_number='ADM001',
            school=self.school,
            date_of_birth='2005-01-15',
            gender='F',
            state_of_origin='Lagos',
            lga_of_origin='Apapa',
            residential_address='123 Street',
            parent_name='John Smith',
            parent_phone='08012345678',
            emergency_contact_name='John Smith',
            emergency_contact_phone='08012345678',
            admission_date='2020-09-15'
        )
        self.fee_structure = FeeStructure.objects.create(
            school=self.school,
            name='Tuition Fee',
            fee_type='TUITION',
            amount=50000,
            academic_year='2024/2025',
            term='FIRST'
        )
        self.student_fee = StudentFee.objects.create(
            student=self.student,
            fee_structure=self.fee_structure,
            amount_due=50000
        )
    
    def test_student_fee_balance(self):
        self.assertEqual(self.student_fee.balance, 50000)
    
    def test_student_fee_status(self):
        self.assertEqual(self.student_fee.status, 'PENDING')


class FinanceAPITest(APITestCase):
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
        
        self.school = School.objects.create(
            name='Test School',
            code='TS001',
            school_type='SENIOR',
            lga='APAPA',
            address='123 Street'
        )
    
    def test_list_fee_structures(self):
        response = self.client.get('/api/finance/fee-structures/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_payments(self):
        response = self.client.get('/api/finance/payments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_budgets(self):
        response = self.client.get('/api/finance/budgets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
