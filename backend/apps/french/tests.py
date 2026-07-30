from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.schools.models import School
from .models import FrenchProgram, FrenchClub

User = get_user_model()


class FrenchProgramModelTest(TestCase):
    def setUp(self):
        self.program = FrenchProgram.objects.create(
            name='Beginner French', description='Intro to French',
            level='BEGINNER', duration_weeks=12
        )

    def test_program_str(self):
        self.assertEqual(str(self.program), 'Beginner French (BEGINNER)')


class FrenchClubModelTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.club = FrenchClub.objects.create(
            school=self.school, name='French Conversation Club'
        )

    def test_club_str(self):
        self.assertEqual(str(self.club), 'Test School - French Conversation Club')


class FrenchAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com', password='TestPass123!',
            first_name='Test', last_name='User', role='SYSADMIN'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

    def test_list_programs(self):
        response = self.client.get('/api/french/programs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_clubs(self):
        response = self.client.get('/api/french/clubs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
