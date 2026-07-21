from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import User
from apps.schools.models import School
from .models import File, FileMovement, FileAttachment


class FileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Test',
            last_name='User',
            role='SYSADMIN'
        )
        self.file = File.objects.create(
            file_number='EDIV-2024-REG-001',
            title='Test Correspondence',
            file_type='CORRESPONDENCE',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
            classification='INTERNAL',
            priority='NORMAL'
        )
    
    def test_file_str(self):
        self.assertEqual(str(self.file), 'EDIV-2024-REG-001 - Test Correspondence')


class FilesAPITest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin@ediv.gov.ng',
            password='AdminPass123!@#',
            first_name='Admin',
            last_name='User',
            role='SYSADMIN'
        )
        self.token = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')
        
        self.file = File.objects.create(
            file_number='EDIV-2024-REG-001',
            title='Test Correspondence',
            file_type='CORRESPONDENCE',
            created_by=self.admin,
            current_holder=self.admin,
            status='ACTIVE'
        )
    
    def test_list_files(self):
        response = self.client.get('/api/files/files/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_file(self):
        response = self.client.get(f'/api/files/files/{self.file.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_file(self):
        data = {
            'file_number': 'EDIV-2024-REG-002',
            'title': 'New Memo',
            'file_type': 'MEMO',
            'status': 'ACTIVE',
            'classification': 'INTERNAL',
            'priority': 'HIGH'
        }
        response = self.client.post('/api/files/files/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
