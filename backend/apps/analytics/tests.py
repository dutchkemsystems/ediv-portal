from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal
from .models import AnalyticsReport, KPI

User = get_user_model()


class AnalyticsReportModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com', password='TestPass123!',
            first_name='Test', last_name='User', role='SYSADMIN'
        )
        self.report = AnalyticsReport.objects.create(
            title='Enrollment Stats', report_type='ENROLLMENT',
            generated_by=self.user
        )

    def test_report_str(self):
        self.assertEqual(str(self.report), 'Enrollment Stats (ENROLLMENT)')


class KPIModelTest(TestCase):
    def setUp(self):
        self.kpi = KPI.objects.create(
            name='Pass Rate', metric_type='PERCENTAGE',
            target_value=Decimal('80.00'), current_value=Decimal('75.00'),
            academic_year='2024/2025'
        )

    def test_kpi_str(self):
        self.assertEqual(str(self.kpi), 'Pass Rate (75.00/80.00)')

    def test_achievement_percentage(self):
        self.assertEqual(self.kpi.achievement_percentage, 93.75)


class AnalyticsAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com', password='TestPass123!',
            first_name='Test', last_name='User', role='SYSADMIN'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

    def test_list_reports(self):
        response = self.client.get('/api/analytics/reports/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_report(self):
        response = self.client.post('/api/analytics/reports/', {
            'title': 'Test Report', 'report_type': 'ATTENDANCE',
            'generated_by': self.user.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_overview_stats(self):
        response = self.client.get('/api/analytics/stats/overview/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
