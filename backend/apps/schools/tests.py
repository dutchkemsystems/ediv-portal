from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import User
from .models import School, SchoolAcademicYear


class SchoolModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='principal@school.com',
            password='TestPass123!@#',
            first_name='John',
            last_name='Doe',
            role='PRI'
        )
        self.school = School.objects.create(
            name='Test Secondary School',
            code='TSS001',
            school_type='SENIOR',
            lga='APAPA',
            address='123 Test Street',
            principal=self.user,
            student_capacity=1000,
            current_enrollment=500
        )
    
    def test_school_str(self):
        self.assertEqual(str(self.school), 'Test Secondary School (TSS001)')
    
    def test_occupancy_rate(self):
        self.assertEqual(self.school.occupancy_rate, 50.0)
    
    def test_school_unique_code(self):
        with self.assertRaises(Exception):
            School.objects.create(
                name='Another School',
                code='TSS001',
                school_type='JUNIOR',
                lga='MAINLAND',
                address='456 Another Street'
            )


class SchoolAPITest(APITestCase):
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
        
        self.school = School.objects.create(
            name='Test Secondary School',
            code='TSS001',
            school_type='SENIOR',
            lga='APAPA',
            address='123 Test Street'
        )
    
    def test_list_schools(self):
        response = self.client.get('/api/schools/schools/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_school(self):
        data = {
            'name': 'New Secondary School',
            'code': 'NSS001',
            'school_type': 'JUNIOR',
            'lga': 'MAINLAND',
            'address': '456 New Street'
        }
        response = self.client.post('/api/schools/schools/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_get_school(self):
        response = self.client.get(f'/api/schools/schools/{self.school.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_update_school(self):
        data = {'name': 'Updated School Name'}
        response = self.client.patch(f'/api/schools/schools/{self.school.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delete_school(self):
        response = self.client.delete(f'/api/schools/schools/{self.school.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_unauthorized_access(self):
        self.client.credentials()
        response = self.client.get('/api/schools/schools/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
