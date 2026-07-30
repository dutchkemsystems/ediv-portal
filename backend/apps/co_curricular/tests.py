from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.schools.models import School
from .models import Activity, Competition

User = get_user_model()


class ActivityModelTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.activity = Activity.objects.create(
            school=self.school, name='Football Club',
            activity_type='SPORTS', description='School football team'
        )

    def test_activity_str(self):
        self.assertEqual(str(self.activity), 'Test School - Football Club')


class CompetitionModelTest(TestCase):
    def setUp(self):
        self.competition = Competition.objects.create(
            name='Inter-School Debate', competition_type='DEBATE',
            description='Annual debate competition',
            organizer='Lagos State', venue='Convention Hall',
            start_date='2026-03-01', end_date='2026-03-03',
            registration_deadline='2026-02-25'
        )

    def test_competition_str(self):
        self.assertEqual(str(self.competition), 'Inter-School Debate')


class CoCurricularAPITest(APITestCase):
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

    def test_list_activities(self):
        response = self.client.get('/api/co-curricular/activities/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_activity(self):
        response = self.client.post('/api/co-curricular/activities/', {
            'school': self.school.id, 'name': 'Chess Club',
            'activity_type': 'CLUB', 'description': 'Chess club'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_competitions(self):
        response = self.client.get('/api/co-curricular/competitions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
