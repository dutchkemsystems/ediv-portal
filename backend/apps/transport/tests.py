from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.schools.models import School
from decimal import Decimal
from .models import Vehicle, BusRoute

User = get_user_model()


class VehicleModelTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.vehicle = Vehicle.objects.create(
            school=self.school, registration_number='LAG-123-ABC',
            vehicle_type='BUS', capacity=45,
            insurance_expiry='2027-01-01'
        )

    def test_vehicle_str(self):
        self.assertEqual(str(self.vehicle), 'LAG-123-ABC (BUS)')


class BusRouteModelTest(TestCase):
    def setUp(self):
        school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.vehicle = Vehicle.objects.create(
            school=school, registration_number='LAG-123-ABC',
            vehicle_type='BUS', capacity=45, insurance_expiry='2027-01-01'
        )
        self.route = BusRoute.objects.create(
            name='Route A - Mainland', school=school,
            vehicle=self.vehicle, departure_time='07:00',
            arrival_time='07:45', fare=Decimal('500.00')
        )

    def test_route_str(self):
        self.assertEqual(str(self.route), 'Route A - Mainland')


class TransportAPITest(APITestCase):
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

    def test_list_vehicles(self):
        response = self.client.get('/api/transport/vehicles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_vehicle(self):
        response = self.client.post('/api/transport/vehicles/', {
            'school': self.school.id, 'registration_number': 'LAG-456-DEF',
            'vehicle_type': 'VAN', 'capacity': 15,
            'insurance_expiry': '2027-06-01'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_routes(self):
        response = self.client.get('/api/transport/routes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
