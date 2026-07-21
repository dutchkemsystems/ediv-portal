from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!@#',
            first_name='Test',
            last_name='User',
            role='TCH'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'TCH')
        self.assertTrue(user.check_password('TestPass123!@#'))
    
    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='AdminPass123!@#'
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.role, 'SYSADMIN')
    
    def test_user_str(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!@#',
            first_name='Test',
            last_name='User',
            role='TCH'
        )
        self.assertEqual(str(user), 'Test User (TCH)')


class AuthViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!@#',
            first_name='Test',
            last_name='User',
            role='TCH'
        )
    
    def test_login_success(self):
        response = self.client.post('/api/users/auth/', {
            'email': 'test@example.com',
            'password': 'TestPass123!@#'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_invalid_credentials(self):
        response = self.client.post('/api/users/auth/', {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post('/api/users/auth/', {
            'email': 'test@example.com',
            'password': 'TestPass123!@#'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserViewSetTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='AdminPass123!@#',
            first_name='Admin',
            last_name='User',
            role='SYSADMIN'
        )
        self.teacher = User.objects.create_user(
            email='teacher@example.com',
            password='TeacherPass123!@#',
            first_name='Teacher',
            last_name='User',
            role='TCH'
        )
        self.admin_token = RefreshToken.for_user(self.admin)
        self.teacher_token = RefreshToken.for_user(self.teacher)
    
    def test_list_users_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token.access_token}')
        response = self.client.get('/api/users/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_users_teacher(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.teacher_token.access_token}')
        response = self.client.get('/api/users/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token.access_token}')
        response = self.client.post('/api/users/users/', {
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'TCH',
            'password': 'NewPass123!@#',
            'password_confirm': 'NewPass123!@#'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
