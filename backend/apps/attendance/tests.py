from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import User
from apps.schools.models import School
from .models import StudentAttendance, StaffAttendance


class StudentAttendanceModelTest(TestCase):
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
        self.attendance = StudentAttendance.objects.create(
            student=self.student,
            date='2024-12-01',
            status='PRESENT',
            recorded_by=self.user
        )
    
    def test_attendance_str(self):
        self.assertEqual(str(self.attendance), 'Jane Smith - 2024-12-01 (PRESENT)')


class AttendanceAPITest(APITestCase):
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
    
    def test_list_student_attendance(self):
        response = self.client.get('/api/attendance/student-attendance/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_staff_attendance(self):
        response = self.client.get('/api/attendance/staff-attendance/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
