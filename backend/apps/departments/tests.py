from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Department, Unit

User = get_user_model()


class DepartmentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='head@test.com', password='TestPass123!',
            first_name='Head', last_name='User', role='HR'
        )
        self.dept = Department.objects.create(
            name='Human Resources', code='HR',
            category='CORE', head=self.user
        )

    def test_department_str(self):
        self.assertEqual(str(self.dept), 'Human Resources (HR)')

    def test_department_hierarchy(self):
        sub = Department.objects.create(
            name='Recruitment', code='HR-REC',
            category='SUPPORT', parent=self.dept
        )
        self.assertEqual(sub.parent, self.dept)
        self.assertIn(sub, self.dept.sub_departments.all())


class UnitModelTest(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(
            name='Finance', code='FIN', category='CORE'
        )
        self.unit = Unit.objects.create(
            name='Accounts', code='FIN-ACC',
            department=self.dept
        )

    def test_unit_str(self):
        self.assertEqual(str(self.unit), 'Finance - Accounts')


class DepartmentAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com', password='TestPass123!',
            first_name='Test', last_name='User', role='SYSADMIN'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')
        self.dept = Department.objects.create(
            name='QA', code='QA', category='CORE'
        )

    def test_list_departments(self):
        response = self.client.get('/api/departments/departments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_department(self):
        response = self.client.post('/api/departments/departments/', {
            'name': 'New Dept', 'code': 'NEW', 'category': 'SUPPORT'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_department(self):
        response = self.client.get(f'/api/departments/departments/{self.dept.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_department(self):
        response = self.client.patch(f'/api/departments/departments/{self.dept.id}/', {
            'description': 'Updated'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_units(self):
        Unit.objects.create(name='Test Unit', code='TST', department=self.dept)
        response = self.client.get('/api/departments/units/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_unit(self):
        response = self.client.post('/api/departments/units/', {
            'name': 'New Unit', 'code': 'NU', 'department': self.dept.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
