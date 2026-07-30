from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Report, Dashboard, Widget

User = get_user_model()


class ReportModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com', password='TestPass123!',
            first_name='Test', last_name='User', role='SYSADMIN'
        )
        self.report = Report.objects.create(
            title='Monthly Report', report_type='ACADEMIC',
            generated_by=self.user
        )

    def test_report_str(self):
        self.assertEqual(str(self.report), 'Monthly Report (ACADEMIC)')


class DashboardModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com', password='TestPass123!',
            first_name='Test', last_name='User', role='SYSADMIN'
        )
        self.dashboard = Dashboard.objects.create(
            name='Main Dashboard', owner=self.user, is_default=True
        )

    def test_dashboard_str(self):
        self.assertEqual(str(self.dashboard), 'Main Dashboard')


class WidgetModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com', password='TestPass123!',
            first_name='Test', last_name='User', role='SYSADMIN'
        )
        self.dashboard = Dashboard.objects.create(
            name='Test', owner=self.user
        )
        self.widget = Widget.objects.create(
            dashboard=self.dashboard, title='Stats',
            widget_type='STAT_CARD', data_source='analytics.overview'
        )

    def test_widget_str(self):
        self.assertEqual(str(self.widget), 'Test - Stats')


class ReportAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com', password='TestPass123!',
            first_name='Test', last_name='User', role='SYSADMIN'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')
        self.report = Report.objects.create(
            title='Test Report', report_type='FINANCIAL',
            generated_by=self.user
        )

    def test_list_reports(self):
        response = self.client.get('/api/reports/reports/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_report(self):
        response = self.client.post('/api/reports/reports/', {
            'title': 'New Report', 'report_type': 'ATTENDANCE',
            'generated_by': self.user.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_report(self):
        response = self.client.get(f'/api/reports/reports/{self.report.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
