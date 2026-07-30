from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.schools.models import School
from decimal import Decimal
from .models import AlumniMember, AlumniEvent, AlumniDonation

User = get_user_model()


class AlumniMemberModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='alumni@test.com', password='TestPass123!',
            first_name='Alumni', last_name='Member', role='STD'
        )
        self.school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.alumni = AlumniMember.objects.create(
            user=self.user, school=self.school, graduation_year=2020,
            current_occupation='Engineer', company='Tech Corp'
        )

    def test_alumni_str(self):
        self.assertEqual(str(self.alumni), 'Alumni Member (2020)')


class AlumniEventModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='organizer@test.com', password='TestPass123!',
            first_name='Organizer', last_name='User', role='SYSADMIN'
        )
        self.event = AlumniEvent.objects.create(
            name='Reunion 2026', description='Annual reunion',
            event_date='2026-12-25', venue='School Hall',
            organizer=self.user, registration_deadline='2026-12-20'
        )

    def test_event_str(self):
        self.assertEqual(str(self.event), 'Reunion 2026')


class AlumniDonationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='donor@test.com', password='TestPass123!',
            first_name='Donor', last_name='User', role='STD'
        )
        school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.alumni = AlumniMember.objects.create(
            user=self.user, school=school, graduation_year=2020
        )
        self.donation = AlumniDonation.objects.create(
            donor=self.alumni, amount=Decimal('50000.00'),
            purpose='Library Fund', donation_date='2026-01-15',
            receipt_number='DON-001'
        )

    def test_donation_str(self):
        self.assertIn('50000', str(self.donation))


class AlumniAPITest(APITestCase):
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

    def test_list_alumni(self):
        response = self.client.get('/api/alumni/members/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_events(self):
        response = self.client.get('/api/alumni/events/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
