from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.schools.models import School
from apps.students.models import Student
from decimal import Decimal
from .models import CounselingSession, WellnessCheckIn, WellnessResource

User = get_user_model()


class CounselingSessionModelTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        student_user = User.objects.create_user(
            email='student@test.com', password='TestPass123!',
            first_name='Student', last_name='One', role='STD'
        )
        self.student = Student.objects.create(
            user=student_user, admission_number='ADM001',
            school=self.school, date_of_birth='2010-01-01',
            gender='M', state_of_origin='Lagos', lga_of_origin='Mainland',
            residential_address='123 Street', parent_name='Parent',
            parent_phone='08012345678', emergency_contact_name='Emergency',
            emergency_contact_phone='08012345678', admission_date='2024-09-01'
        )
        self.counselor = User.objects.create_user(
            email='counselor@test.com', password='TestPass123!',
            first_name='Counselor', last_name='One', role='TCH'
        )
        self.session = CounselingSession.objects.create(
            student=self.student, counselor=self.counselor,
            counseling_type='ACADEMIC', session_date='2026-01-15',
            session_time='10:00', notes='Discussed study habits'
        )

    def test_session_str(self):
        self.assertIn('ACADEMIC', str(self.session))


class WellnessCheckInModelTest(TestCase):
    def setUp(self):
        school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        student_user = User.objects.create_user(
            email='student@test.com', password='TestPass123!',
            first_name='Student', last_name='One', role='STD'
        )
        self.student = Student.objects.create(
            user=student_user, admission_number='ADM001',
            school=school, date_of_birth='2010-01-01',
            gender='M', state_of_origin='Lagos', lga_of_origin='Mainland',
            residential_address='123 Street', parent_name='Parent',
            parent_phone='08012345678', emergency_contact_name='Emergency',
            emergency_contact_phone='08012345678', admission_date='2024-09-01'
        )
        self.checkin = WellnessCheckIn.objects.create(
            student=self.student, date='2026-01-15',
            mood='GOOD', stress_level=3, sleep_hours=Decimal('8.0'),
            exercise_minutes=30
        )

    def test_checkin_str(self):
        self.assertIn('GOOD', str(self.checkin))


class WellnessResourceModelTest(TestCase):
    def setUp(self):
        self.resource = WellnessResource.objects.create(
            name='Crisis Helpline', resource_type='CONTACT',
            description='24/7 crisis support', contact_phone='0800-123-4567',
            is_emergency=True
        )

    def test_resource_str(self):
        self.assertEqual(str(self.resource), 'Crisis Helpline')


class WellnessAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com', password='TestPass123!',
            first_name='Test', last_name='User', role='SYSADMIN'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

    def test_list_sessions(self):
        response = self.client.get('/api/wellness/counseling-sessions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_checkins(self):
        response = self.client.get('/api/wellness/check-ins/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_resources(self):
        response = self.client.get('/api/wellness/resources/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
