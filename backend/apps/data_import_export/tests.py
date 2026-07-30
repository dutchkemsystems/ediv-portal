from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import ImportJob, ImportError

User = get_user_model()


class ImportJobModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com', password='TestPass123!',
            first_name='Test', last_name='User', role='SYSADMIN'
        )
        self.job = ImportJob.objects.create(
            file_name='students.csv', file_type='CSV',
            target_model='students.Student', created_by=self.user,
            total_rows=100
        )

    def test_job_str(self):
        self.assertEqual(str(self.job), 'students.csv (PENDING)')


class ImportErrorModelTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            email='test@test.com', password='TestPass123!',
            first_name='Test', last_name='User', role='SYSADMIN'
        )
        self.job = ImportJob.objects.create(
            file_name='test.csv', file_type='CSV',
            target_model='students.Student', created_by=user
        )
        self.error = ImportError.objects.create(
            job=self.job, row_number=5,
            field_name='email', error_message='Invalid email format'
        )

    def test_error_str(self):
        self.assertEqual(str(self.error), 'Row 5: Invalid email format')


class DataImportExportAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com', password='TestPass123!',
            first_name='Test', last_name='User', role='SYSADMIN'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

    def test_list_import_jobs(self):
        response = self.client.get('/api/data-import-export/jobs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
