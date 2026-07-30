from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.schools.models import School
from .models import Period, Timetable

User = get_user_model()


class PeriodModelTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.period = Period.objects.create(
            school=self.school, name='Period 1',
            start_time='08:00', end_time='08:40', period_number=1
        )

    def test_period_str(self):
        self.assertIn('Period 1', str(self.period))


class TimetableModelTest(TestCase):
    def setUp(self):
        from apps.academics.models import ClassLevel, Class
        self.school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.class_obj = Class.objects.create(
            school=self.school, name='JSS 1A',
            level=ClassLevel.JSS1, academic_year='2025/2026'
        )
        self.timetable = Timetable.objects.create(
            school=self.school, class_obj=self.class_obj,
            academic_year='2025/2026', term='FIRST'
        )

    def test_timetable_str(self):
        self.assertIn('JSS 1A', str(self.timetable))


class TimetableAPITest(APITestCase):
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

    def test_list_periods(self):
        response = self.client.get('/api/timetable/periods/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_period(self):
        response = self.client.post('/api/timetable/periods/', {
            'school': self.school.id, 'name': 'Period 1',
            'start_time': '08:00:00', 'end_time': '08:40:00',
            'period_number': 1
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_timetables(self):
        response = self.client.get('/api/timetable/timetables/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
