from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.schools.models import School
from apps.staff.models import Staff

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
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


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


class CreateSchoolStaffTest(APITestCase):
    """Tests for POST /api/users/users/create-school-staff/"""

    def setUp(self):
        self.school = School.objects.create(
            name='Test School',
            code='TST001',
            school_type='SENIOR',
            lga='APAPA',
            address='123 Street'
        )
        self.admin = User.objects.create_user(
            email='admin@ediv.gov.ng',
            password='AdminPass123!@#',
            first_name='Admin',
            last_name='User',
            role='SYSADMIN'
        )
        self.principal = User.objects.create_user(
            email='principal@ediv.gov.ng',
            password='PrincipalPass123!@#',
            first_name='Principal',
            last_name='User',
            role='PRI'
        )
        self.school.principal = self.principal
        self.school.save()

        self.teacher = User.objects.create_user(
            email='teacher@ediv.gov.ng',
            password='TeacherPass123!@#',
            first_name='Teacher',
            last_name='User',
            role='TCH'
        )

        self.admin_token = RefreshToken.for_user(self.admin)
        self.principal_token = RefreshToken.for_user(self.principal)
        self.teacher_token = RefreshToken.for_user(self.teacher)

    # --- SYSADMIN can create any role ---

    def test_admin_creates_teacher(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token.access_token}')
        response = self.client.post('/api/users/users/create-school-staff/', {
            'first_name': 'New',
            'last_name': 'Teacher',
            'email': 'newteacher@ediv.gov.ng',
            'role': 'TCH',
            'school_id': self.school.id,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('temp_password', response.data['user'])
        self.assertEqual(response.data['user']['role'], 'TCH')
        # Verify Staff record was created
        self.assertTrue(Staff.objects.filter(user__email='newteacher@ediv.gov.ng').exists())

    def test_admin_creates_principal(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token.access_token}')
        response = self.client.post('/api/users/users/create-school-staff/', {
            'first_name': 'New',
            'last_name': 'Principal',
            'email': 'newprincipal@ediv.gov.ng',
            'role': 'PRI',
            'school_id': self.school.id,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['role'], 'PRI')

    def test_admin_creates_vp(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token.access_token}')
        response = self.client.post('/api/users/users/create-school-staff/', {
            'first_name': 'New',
            'last_name': 'VP',
            'email': 'newvp@ediv.gov.ng',
            'role': 'VP',
            'school_id': self.school.id,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['role'], 'VP')

    def test_admin_creates_non_teaching(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token.access_token}')
        response = self.client.post('/api/users/users/create-school-staff/', {
            'first_name': 'New',
            'last_name': 'Staff',
            'email': 'newstaff@ediv.gov.ng',
            'role': 'SA_OFF',
            'school_id': self.school.id,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['role'], 'SA_OFF')

    def test_admin_without_school_id_fails(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token.access_token}')
        response = self.client.post('/api/users/users/create-school-staff/', {
            'first_name': 'New',
            'last_name': 'Teacher',
            'email': 'newteacher@ediv.gov.ng',
            'role': 'TCH',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Principal can only create TCH/SA_OFF for own school ---

    def test_principal_creates_teacher(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.principal_token.access_token}')
        response = self.client.post('/api/users/users/create-school-staff/', {
            'first_name': 'New',
            'last_name': 'Teacher',
            'email': 'newteacher@ediv.gov.ng',
            'role': 'TCH',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['role'], 'TCH')

    def test_principal_creates_non_teaching(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.principal_token.access_token}')
        response = self.client.post('/api/users/users/create-school-staff/', {
            'first_name': 'New',
            'last_name': 'Staff',
            'email': 'newstaff@ediv.gov.ng',
            'role': 'SA_OFF',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_principal_cannot_create_principal(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.principal_token.access_token}')
        response = self.client.post('/api/users/users/create-school-staff/', {
            'first_name': 'New',
            'last_name': 'Principal',
            'email': 'newprincipal@ediv.gov.ng',
            'role': 'PRI',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_principal_cannot_create_vp(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.principal_token.access_token}')
        response = self.client.post('/api/users/users/create-school-staff/', {
            'first_name': 'New',
            'last_name': 'VP',
            'email': 'newvp@ediv.gov.ng',
            'role': 'VP',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Teacher cannot create staff ---

    def test_teacher_cannot_create_staff(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.teacher_token.access_token}')
        response = self.client.post('/api/users/users/create-school-staff/', {
            'first_name': 'New',
            'last_name': 'Teacher',
            'email': 'newteacher@ediv.gov.ng',
            'role': 'TCH',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Duplicate email ---

    def test_duplicate_email_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token.access_token}')
        response = self.client.post('/api/users/users/create-school-staff/', {
            'first_name': 'Dup',
            'last_name': 'Teacher',
            'email': 'teacher@ediv.gov.ng',  # already exists
            'role': 'TCH',
            'school_id': self.school.id,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Initial password ---

    def test_custom_initial_password(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token.access_token}')
        response = self.client.post('/api/users/users/create-school-staff/', {
            'first_name': 'Custom',
            'last_name': 'Pass',
            'email': 'custompass@ediv.gov.ng',
            'role': 'TCH',
            'school_id': self.school.id,
            'initial_password': 'MySecret99!',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['temp_password'], 'MySecret99!')
        # Verify the user can login with that password
        login_resp = self.client.post('/api/users/auth/', {
            'email': 'custompass@ediv.gov.ng',
            'password': 'MySecret99!',
        })
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)

    # --- Audit log created ---

    def test_audit_log_created_on_create(self):
        from apps.audit.models import AuditLog
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token.access_token}')
        before = AuditLog.objects.count()
        self.client.post('/api/users/users/create-school-staff/', {
            'first_name': 'Audit',
            'last_name': 'Test',
            'email': 'audit@ediv.gov.ng',
            'role': 'TCH',
            'school_id': self.school.id,
        })
        self.assertEqual(AuditLog.objects.count(), before + 1)


class DeleteSchoolStaffTest(APITestCase):
    """Tests for POST /api/users/users/delete-school-staff/"""

    def setUp(self):
        self.school = School.objects.create(
            name='Test School',
            code='TST001',
            school_type='SENIOR',
            lga='APAPA',
            address='123 Street'
        )
        self.admin = User.objects.create_user(
            email='admin@ediv.gov.ng',
            password='AdminPass123!@#',
            first_name='Admin',
            last_name='User',
            role='SYSADMIN'
        )
        self.target_teacher = User.objects.create_user(
            email='teacher@ediv.gov.ng',
            password='TeacherPass123!@#',
            first_name='Teacher',
            last_name='Target',
            role='TCH'
        )
        self.principal = User.objects.create_user(
            email='principal@ediv.gov.ng',
            password='PrincipalPass123!@#',
            first_name='Principal',
            last_name='User',
            role='PRI'
        )

        self.admin_token = RefreshToken.for_user(self.admin)
        self.principal_token = RefreshToken.for_user(self.principal)

    def test_admin_deactivates_teacher(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token.access_token}')
        response = self.client.post('/api/users/users/delete-school-staff/', {
            'user_id': self.target_teacher.id,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.target_teacher.refresh_from_db()
        self.assertFalse(self.target_teacher.is_active)

    def test_cannot_delete_self(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token.access_token}')
        response = self.client.post('/api/users/users/delete-school-staff/', {
            'user_id': self.admin.id,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_delete_admin_account(self):
        other_admin = User.objects.create_user(
            email='otheradmin@ediv.gov.ng',
            password='AdminPass123!@#',
            first_name='Other',
            last_name='Admin',
            role='TG'
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token.access_token}')
        response = self.client.post('/api/users/users/delete-school-staff/', {
            'user_id': other_admin.id,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_principal_cannot_delete(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.principal_token.access_token}')
        response = self.client.post('/api/users/users/delete-school-staff/', {
            'user_id': self.target_teacher.id,
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_nonexistent_user_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token.access_token}')
        response = self.client.post('/api/users/users/delete-school-staff/', {
            'user_id': 99999,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_audit_log_created_on_delete(self):
        from apps.audit.models import AuditLog
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token.access_token}')
        before = AuditLog.objects.count()
        self.client.post('/api/users/users/delete-school-staff/', {
            'user_id': self.target_teacher.id,
        })
        self.assertEqual(AuditLog.objects.count(), before + 1)


class ListSchoolStaffTest(APITestCase):
    """Tests for GET /api/users/users/school-staff/"""

    def setUp(self):
        self.school = School.objects.create(
            name='Test School',
            code='TST001',
            school_type='SENIOR',
            lga='APAPA',
            address='123 Street'
        )
        self.principal = User.objects.create_user(
            email='principal@ediv.gov.ng',
            password='PrincipalPass123!@#',
            first_name='Principal',
            last_name='User',
            role='PRI'
        )
        self.school.principal = self.principal
        self.school.save()

        self.teacher = User.objects.create_user(
            email='teacher@ediv.gov.ng',
            password='TeacherPass123!@#',
            first_name='Teacher',
            last_name='User',
            role='TCH'
        )
        Staff.objects.create(
            user=self.teacher,
            staff_id='TST/STF/0001',
            employee_number='EDIV/TST/0001',
            school=self.school,
            category='TEACHING',
            designation='TEACHER',
            employment_type='PERMANENT',
            qualification='Bachelors',
            date_of_birth='1990-01-01',
            gender='M',
            marital_status='SINGLE',
            state_of_origin='Lagos',
            lga_of_origin='Lagos Island',
            residential_address='Lagos',
            emergency_contact_name='N/A',
            emergency_contact_phone='N/A',
            bank_name='N/A',
            bank_account_number='N/A',
            bank_account_name='N/A',
            date_joined='2024-01-01',
        )

        self.principal_token = RefreshToken.for_user(self.principal)

    def test_principal_lists_own_school_staff(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.principal_token.access_token}')
        response = self.client.get('/api/users/users/school-staff/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['school']['code'], 'TST001')
        self.assertEqual(len(response.data['staff']), 1)
        self.assertEqual(response.data['staff'][0]['email'], 'teacher@ediv.gov.ng')
