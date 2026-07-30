from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.schools.models import School
from decimal import Decimal
from .models import Asset, AssetMaintenance, AssetTransfer

User = get_user_model()


class AssetModelTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.asset = Asset.objects.create(
            school=self.school, asset_code='AST-001',
            name='Desktop Computer', category='ELECTRONICS',
            purchase_date='2024-01-15', purchase_price=Decimal('250000.00'),
            current_value=Decimal('200000.00'), location='Computer Lab'
        )

    def test_asset_str(self):
        self.assertEqual(str(self.asset), 'AST-001 - Desktop Computer')


class AssetMaintenanceModelTest(TestCase):
    def setUp(self):
        school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.asset = Asset.objects.create(
            school=school, asset_code='AST-001', name='Desktop',
            category='ELECTRONICS', purchase_date='2024-01-15',
            purchase_price=Decimal('250000.00'),
            current_value=Decimal('200000.00'), location='Lab'
        )
        self.maintenance = AssetMaintenance.objects.create(
            asset=self.asset, maintenance_date='2026-01-15',
            description='RAM upgrade', cost=Decimal('15000.00'),
            performed_by='Tech Solutions'
        )

    def test_maintenance_str(self):
        self.assertIn('Desktop', str(self.maintenance))


class AssetAPITest(APITestCase):
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

    def test_list_assets(self):
        response = self.client.get('/api/assets/assets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_asset(self):
        response = self.client.post('/api/assets/assets/', {
            'school': self.school.id, 'asset_code': 'AST-002',
            'name': 'Projector', 'category': 'ELECTRONICS',
            'purchase_date': '2026-01-15', 'purchase_price': '500000.00',
            'current_value': '450000.00', 'location': 'Hall'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
