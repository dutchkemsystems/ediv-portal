"""Tests for new API endpoints."""
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import User
from apps.files.models import File, FileMovement
from apps.files.services.file_movement_service import FileMovementService


class FileDashboardAPITest(APITestCase):
    """Tests for GET /api/files/dashboard/"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='dashboard@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Dashboard',
            last_name='User',
            role='SYSADMIN'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')
        self.file = File.objects.create(
            file_number='EDIV-2026-DASH-001',
            title='Dashboard Test',
            file_type='MEMO',
            file_category='ADMIN',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )

    def test_dashboard_returns_stats(self):
        """Dashboard should return status and priority counts."""
        response = self.client.get('/api/files/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status_counts', response.data)
        self.assertIn('priority_counts', response.data)
        self.assertIn('total_files', response.data)
        self.assertIn('recent_movements', response.data)

    def test_dashboard_unauthenticated(self):
        """Unauthenticated request should be rejected."""
        self.client.credentials()
        response = self.client.get('/api/files/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_dashboard_includes_recent_movements(self):
        """Dashboard should include recent movements."""
        response = self.client.get('/api/files/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['recent_movements'], list)


class WorkflowVisualizationAPITest(APITestCase):
    """Tests for GET /api/files/workflow/{id}/"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='workflow@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Workflow',
            last_name='User',
            role='SYSADMIN'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')
        self.file = File.objects.create(
            file_number='EDIV-2026-WF-001',
            title='Workflow Test',
            file_type='MEMO',
            file_category='ADMIN',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )

    def test_workflow_returns_journey(self):
        """Workflow endpoint should return file journey and steps."""
        response = self.client.get(f'/api/files/workflow/{self.file.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('file', response.data)
        self.assertIn('journey', response.data)
        self.assertIn('workflow_steps', response.data)

    def test_workflow_nonexistent_file(self):
        """Non-existent file should return 404."""
        response = self.client.get('/api/files/workflow/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_workflow_includes_file_details(self):
        """Workflow should include file details."""
        response = self.client.get(f'/api/files/workflow/{self.file.id}/')
        self.assertEqual(response.data['file']['file_number'], 'EDIV-2026-WF-001')
        self.assertEqual(response.data['file']['status'], 'ACTIVE')

    def test_workflow_includes_11_steps(self):
        """Incoming workflow should have 11 steps."""
        response = self.client.get(f'/api/files/workflow/{self.file.id}/')
        self.assertEqual(len(response.data['workflow_steps']), 11)


class FileBulkActionAPITest(APITestCase):
    """Tests for POST /api/files/bulk-action/"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='bulk@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Bulk',
            last_name='User',
            role='SYSADMIN'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')
        self.file1 = File.objects.create(
            file_number='EDIV-2026-BULK-001',
            title='Bulk File 1',
            file_type='MEMO',
            file_category='ADMIN',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
            classification='PUBLIC',
        )
        self.file2 = File.objects.create(
            file_number='EDIV-2026-BULK-002',
            title='Bulk File 2',
            file_type='MEMO',
            file_category='ADMIN',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
            classification='PUBLIC',
        )

    def test_bulk_archive(self):
        """Bulk archive should archive multiple files."""
        # First close the files (archive requires CLOSED or ARCHIVED status)
        self.file1.status = 'CLOSED'
        self.file1.save()
        self.file2.status = 'CLOSED'
        self.file2.save()

        response = self.client.post('/api/files/bulk-action/', {
            'action': 'archive',
            'file_ids': [self.file1.id, self.file2.id],
            'notes': 'Bulk archive test',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], 2)
        self.file1.refresh_from_db()
        self.file2.refresh_from_db()
        self.assertEqual(self.file1.status, 'ARCHIVED')
        self.assertEqual(self.file2.status, 'ARCHIVED')

    def test_bulk_action_no_files(self):
        """Bulk action with no file IDs should return error."""
        response = self.client.post('/api/files/bulk-action/', {
            'action': 'archive',
            'file_ids': [],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bulk_escalate(self):
        """Bulk escalate should escalate multiple files."""
        response = self.client.post('/api/files/bulk-action/', {
            'action': 'escalate',
            'file_ids': [self.file1.id, self.file2.id],
            'notes': 'Urgent escalation',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], 2)
        self.file1.refresh_from_db()
        self.file2.refresh_from_db()
        self.assertEqual(self.file1.priority, 'HIGH')
        self.assertEqual(self.file2.priority, 'HIGH')

    def test_bulk_action_unknown_action(self):
        """Bulk action with unknown action should fail gracefully."""
        response = self.client.post('/api/files/bulk-action/', {
            'action': 'unknown_action',
            'file_ids': [self.file1.id],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['failed'], 1)


class FileSearchAPITest(APITestCase):
    """Tests for GET /api/files/search/"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='searchapi@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Search',
            last_name='User',
            role='SYSADMIN'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')
        self.file = File.objects.create(
            file_number='EDIV-2026-SAPI-001',
            title='Search API Test',
            file_type='MEMO',
            file_category='ADMIN',
            description='Test search functionality',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )

    def test_search_endpoint(self):
        """Search endpoint should return results."""
        response = self.client.get('/api/files/search/?q=search')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('total', response.data)

    def test_search_with_filters(self):
        """Search with filters should work."""
        response = self.client.get('/api/files/search/?status=ACTIVE')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_suggestions_endpoint(self):
        """Search suggestions endpoint should return suggestions."""
        response = self.client.get('/api/files/search/suggestions/?q=EDIV')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)


class FileImportExportAPITest(APITestCase):
    """Tests for import/export endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='impexp@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='ImpExp',
            last_name='User',
            role='SYSADMIN'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

    def test_import_endpoint_no_file(self):
        """Import without file should return error."""
        response = self.client.post('/api/files/import/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_export_endpoint_no_ids(self):
        """Export without file IDs should return error."""
        response = self.client.post('/api/files/export/', {'file_ids': []}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
