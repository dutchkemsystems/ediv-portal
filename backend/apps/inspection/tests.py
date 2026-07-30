from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.schools.models import School
from .models import Inspection, InspectionChecklist

User = get_user_model()


class InspectionModelTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.inspector = User.objects.create_user(
            email='inspector@test.com', password='TestPass123!',
            first_name='Inspector', last_name='One', role='QA'
        )
        self.inspection = Inspection.objects.create(
            school=self.school, title='Q1 Routine Inspection',
            inspection_type='ROUTINE', scheduled_date='2026-03-01',
            lead_inspector=self.inspector, objectives='Check facilities'
        )

    def test_inspection_str(self):
        self.assertEqual(str(self.inspection), 'Test School - Q1 Routine Inspection')


class InspectionChecklistModelTest(TestCase):
    def setUp(self):
        school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        inspector = User.objects.create_user(
            email='inspector@test.com', password='TestPass123!',
            first_name='Inspector', last_name='One', role='QA'
        )
        self.inspection = Inspection.objects.create(
            school=school, title='Routine', inspection_type='ROUTINE',
            scheduled_date='2026-03-01', lead_inspector=inspector,
            objectives='Check'
        )
        self.checklist = InspectionChecklist.objects.create(
            inspection=self.inspection, category='Infrastructure',
            item='Classroom condition', description='Check walls and roof'
        )

    def test_checklist_str(self):
        self.assertIn('Classroom condition', str(self.checklist))


class InspectionAPITest(APITestCase):
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

    def test_list_inspections(self):
        response = self.client.get('/api/inspection/inspections/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_inspection(self):
        inspector = User.objects.create_user(
            email='insp@test.com', password='TestPass123!',
            first_name='Insp', last_name='User', role='QA'
        )
        response = self.client.post('/api/inspection/inspections/', {
            'school': self.school.id, 'title': 'New Inspection',
            'inspection_type': 'ROUTINE', 'scheduled_date': '2026-06-01',
            'lead_inspector': inspector.id, 'objectives': 'Check',
            'team_members': [inspector.id]
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
