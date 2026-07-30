from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.schools.models import School
from .models import Facility, MaintenanceRequest, Project

User = get_user_model()


class FacilityModelTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.facility = Facility.objects.create(
            school=self.school, name='Main Hall',
            facility_type='HALL', capacity=500, condition='GOOD'
        )

    def test_facility_str(self):
        self.assertEqual(str(self.facility), 'Test School - Main Hall')


class MaintenanceRequestModelTest(TestCase):
    def setUp(self):
        school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.facility = Facility.objects.create(
            school=school, name='Lab', facility_type='LABORATORY'
        )
        self.user = User.objects.create_user(
            email='test@test.com', password='TestPass123!',
            first_name='Test', last_name='User', role='TCH'
        )
        self.request = MaintenanceRequest.objects.create(
            facility=self.facility, title='AC Repair',
            description='AC not working', priority='HIGH',
            requested_by=self.user
        )

    def test_request_str(self):
        self.assertEqual(str(self.request), 'Lab - AC Repair')


class ProjectModelTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.project = Project.objects.create(
            school=self.school, name='New Block',
            description='Construct new classroom block',
            start_date='2026-01-01', budget=5000000
        )

    def test_project_str(self):
        self.assertEqual(str(self.project), 'Test School - New Block')

    def test_remaining_budget(self):
        self.assertEqual(self.project.remaining_budget, 5000000)


class InfrastructureAPITest(APITestCase):
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

    def test_list_facilities(self):
        response = self.client.get('/api/infrastructure/facilities/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_facility(self):
        response = self.client.post('/api/infrastructure/facilities/', {
            'school': self.school.id, 'name': 'New Lab',
            'facility_type': 'LABORATORY', 'capacity': 40
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_projects(self):
        response = self.client.get('/api/infrastructure/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_maintenance_requests(self):
        response = self.client.get('/api/infrastructure/maintenance-requests/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
