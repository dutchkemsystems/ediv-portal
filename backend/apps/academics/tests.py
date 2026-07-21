from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import User
from apps.schools.models import School
from .models import Class, Subject, Exam, ExamResult, ReportCard


class ClassModelTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Test School',
            code='TS001',
            school_type='SENIOR',
            lga='APAPA',
            address='123 Street'
        )
        self.class_obj = Class.objects.create(
            school=self.school,
            name='SS1A',
            level='SS1',
            section='A',
            capacity=40,
            academic_year='2024/2025',
            term='FIRST'
        )
    
    def test_class_str(self):
        self.assertEqual(str(self.class_obj), 'Test School - SS1A')


class SubjectModelTest(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(
            name='Mathematics',
            code='MTH101',
            category='SCIENCE',
            is_compulsory=True
        )
    
    def test_subject_str(self):
        self.assertEqual(str(self.subject), 'Mathematics (MTH101)')


class ExamModelTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Test School',
            code='TS001',
            school_type='SENIOR',
            lga='APAPA',
            address='123 Street'
        )
        self.exam = Exam.objects.create(
            school=self.school,
            name='First Term Exam',
            exam_type='FINAL',
            academic_year='2024/2025',
            term='FIRST',
            start_date='2024-12-01',
            end_date='2024-12-15',
            total_marks=100,
            pass_marks=40
        )
    
    def test_exam_str(self):
        self.assertEqual(str(self.exam), 'Test School - First Term Exam')


class AcademicsAPITest(APITestCase):
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
        self.subject = Subject.objects.create(
            name='Mathematics',
            code='MTH101',
            category='SCIENCE'
        )
    
    def test_list_classes(self):
        response = self.client.get('/api/academics/classes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_subjects(self):
        response = self.client.get('/api/academics/subjects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_subject(self):
        data = {
            'name': 'English Language',
            'code': 'ENG101',
            'category': 'GENERAL'
        }
        response = self.client.post('/api/academics/subjects/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
