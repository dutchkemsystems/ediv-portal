from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import User
from apps.schools.models import School
from .models import Student, StudentMedicalRecord


class StudentModelTest(TestCase):
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
    
    def test_student_str(self):
        self.assertEqual(str(self.student), 'Jane Smith (ADM001)')
    
    def test_student_age(self):
        from datetime import date
        today = date.today()
        expected_age = today.year - 2005 - (
            (today.month, today.day) < (1, 15)
        )
        self.assertEqual(self.student.age, expected_age)


class StudentAPITest(APITestCase):
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
        self.student_user = User.objects.create_user(
            email='student@test.com',
            password='StudentPass123!@#',
            first_name='Jane',
            last_name='Smith',
            role='STD'
        )
        self.student = Student.objects.create(
            user=self.student_user,
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
    
    def test_list_students(self):
        response = self.client.get('/api/students/students/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_student(self):
        response = self.client.get(f'/api/students/students/{self.student.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_student(self):
        new_user = User.objects.create_user(
            email='newstudent@test.com',
            password='StudentPass123!@#',
            first_name='New',
            last_name='Student',
            role='STD'
        )
        data = {
            'user_id': new_user.id,
            'admission_number': 'ADM002',
            'school': self.school.id,
            'date_of_birth': '2006-05-20',
            'gender': 'M',
            'state_of_origin': 'Lagos',
            'lga_of_origin': 'Mainland',
            'residential_address': '456 Street',
            'parent_name': 'Mary Johnson',
            'parent_phone': '08098765432',
            'emergency_contact_name': 'Mary Johnson',
            'emergency_contact_phone': '08098765432',
            'admission_date': '2021-09-15'
        }
        response = self.client.post('/api/students/students/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
