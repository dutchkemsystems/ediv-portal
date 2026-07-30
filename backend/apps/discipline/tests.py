from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.schools.models import School
from apps.students.models import Student
from .models import DisciplinaryIncident, BehaviorPlan

User = get_user_model()


class DisciplinaryIncidentModelTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.user = User.objects.create_user(
            email='student@test.com', password='TestPass123!',
            first_name='Student', last_name='One', role='STD'
        )
        self.student = Student.objects.create(
            user=self.user, admission_number='ADM001',
            school=self.school, date_of_birth='2010-01-01',
            gender='M', state_of_origin='Lagos', lga_of_origin='Mainland',
            residential_address='123 Street', parent_name='Parent',
            parent_phone='08012345678', emergency_contact_name='Emergency',
            emergency_contact_phone='08012345678', admission_date='2024-09-01'
        )
        self.reporter = User.objects.create_user(
            email='teacher@test.com', password='TestPass123!',
            first_name='Teacher', last_name='One', role='TCH'
        )
        self.incident = DisciplinaryIncident.objects.create(
            student=self.student, reported_by=self.reporter,
            incident_type='LATE_COMING', severity='MINOR',
            title='Late to school', description='Student arrived 30 mins late',
            incident_date='2026-01-15'
        )

    def test_incident_str(self):
        self.assertIn('Late to school', str(self.incident))


class BehaviorPlanModelTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        user = User.objects.create_user(
            email='student@test.com', password='TestPass123!',
            first_name='Student', last_name='One', role='STD'
        )
        self.student = Student.objects.create(
            user=user, admission_number='ADM001',
            school=self.school, date_of_birth='2010-01-01',
            gender='M', state_of_origin='Lagos', lga_of_origin='Mainland',
            residential_address='123 Street', parent_name='Parent',
            parent_phone='08012345678', emergency_contact_name='Emergency',
            emergency_contact_phone='08012345678', admission_date='2024-09-01'
        )
        self.creator = User.objects.create_user(
            email='teacher@test.com', password='TestPass123!',
            first_name='Teacher', last_name='One', role='TCH'
        )
        self.plan = BehaviorPlan.objects.create(
            student=self.student, created_by=self.creator,
            title='Improve Punctuality', description='Plan to be on time',
            goals='Arrive before 8am', strategies='Set alarms, earlier bedtime',
            start_date='2026-01-15'
        )

    def test_plan_str(self):
        self.assertIn('Improve Punctuality', str(self.plan))


class DisciplineAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com', password='TestPass123!',
            first_name='Test', last_name='User', role='SYSADMIN'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

    def test_list_incidents(self):
        response = self.client.get('/api/discipline/incidents/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_behavior_plans(self):
        response = self.client.get('/api/discipline/behavior-plans/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
