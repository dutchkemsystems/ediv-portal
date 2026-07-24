from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import User
from .models import Document, Filing


class DocumentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Test',
            last_name='User',
            role='REG'
        )
        self.doc = Document.objects.create(
            reference_number='EDIV/2024/REG/0001',
            title='Test Document',
            document_type='CORRESPONDENCE',
            created_by=self.user,
            status='DRAFT'
        )

    def test_document_str(self):
        self.assertEqual(str(self.doc), 'EDIV/2024/REG/0001 - Test Document')


class DocumentCreateTest(APITestCase):
    """Tests for POST /api/registry/documents/ with auto reference number."""

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

    def test_create_document_generates_reference_number(self):
        response = self.client.post('/api/registry/documents/', {
            'title': 'New Document',
            'document_type': 'MEMO',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['reference_number'].startswith('EDIV/'))
        self.assertEqual(response.data['created_by'], self.admin.id)

    def test_sequential_reference_numbers(self):
        self.client.post('/api/registry/documents/', {
            'title': 'Doc 1',
            'document_type': 'MEMO',
        })
        self.client.post('/api/registry/documents/', {
            'title': 'Doc 2',
            'document_type': 'MEMO',
        })
        response = self.client.post('/api/registry/documents/', {
            'title': 'Doc 3',
            'document_type': 'MEMO',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('/0003', response.data['reference_number'])

    def test_list_documents(self):
        self.client.post('/api/registry/documents/', {
            'title': 'List Me',
            'document_type': 'CIRCULAR',
        })
        response = self.client.get('/api/registry/documents/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class ApproveDocumentTest(APITestCase):
    """Tests for POST /api/registry/documents/{id}/approve/"""

    def setUp(self):
        self.reg_user = User.objects.create_user(
            email='reg@ediv.gov.ng',
            password='RegPass123!@#',
            first_name='Reg',
            last_name='Officer',
            role='REG'
        )
        self.tg = User.objects.create_user(
            email='tg@ediv.gov.ng',
            password='TgPass123!@#',
            first_name='Tutor',
            last_name='General',
            role='TG'
        )
        self.teacher = User.objects.create_user(
            email='teacher@ediv.gov.ng',
            password='TeacherPass123!@#',
            first_name='Teacher',
            last_name='User',
            role='TCH'
        )
        self.doc = Document.objects.create(
            reference_number='EDIV/2024/REG/0010',
            title='Document to Approve',
            document_type='POLICY',
            created_by=self.reg_user,
            status='PENDING'
        )
        self.reg_token = RefreshToken.for_user(self.reg_user)
        self.tg_token = RefreshToken.for_user(self.tg)
        self.teacher_token = RefreshToken.for_user(self.teacher)

    def test_reg_officer_can_approve(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.reg_token.access_token}')
        response = self.client.post(f'/api/registry/documents/{self.doc.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.doc.refresh_from_db()
        self.assertEqual(self.doc.status, 'APPROVED')

    def test_tg_can_approve(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.tg_token.access_token}')
        response = self.client.post(f'/api/registry/documents/{self.doc.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.doc.refresh_from_db()
        self.assertEqual(self.doc.status, 'APPROVED')

    def test_teacher_cannot_approve(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.teacher_token.access_token}')
        response = self.client.post(f'/api/registry/documents/{self.doc.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RejectDocumentTest(APITestCase):
    """Tests for POST /api/registry/documents/{id}/reject/"""

    def setUp(self):
        self.reg_user = User.objects.create_user(
            email='reg@ediv.gov.ng',
            password='RegPass123!@#',
            first_name='Reg',
            last_name='Officer',
            role='REG'
        )
        self.teacher = User.objects.create_user(
            email='teacher@ediv.gov.ng',
            password='TeacherPass123!@#',
            first_name='Teacher',
            last_name='User',
            role='TCH'
        )
        self.doc = Document.objects.create(
            reference_number='EDIV/2024/REG/0020',
            title='Document to Reject',
            document_type='CONTRACT',
            created_by=self.reg_user,
            status='PENDING'
        )
        self.reg_token = RefreshToken.for_user(self.reg_user)
        self.teacher_token = RefreshToken.for_user(self.teacher)

    def test_reg_officer_can_reject(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.reg_token.access_token}')
        response = self.client.post(f'/api/registry/documents/{self.doc.id}/reject/', {
            'reason': 'Missing required sections',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.doc.refresh_from_db()
        self.assertEqual(self.doc.status, 'REJECTED')

    def test_teacher_cannot_reject(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.teacher_token.access_token}')
        response = self.client.post(f'/api/registry/documents/{self.doc.id}/reject/', {
            'reason': 'Incomplete',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class FilingViewSetTest(APITestCase):
    """Tests for FilingViewSet — auto sets filed_by."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='filer@ediv.gov.ng',
            password='FilerPass123!@#',
            first_name='Filer',
            last_name='User',
            role='REG'
        )
        self.doc = Document.objects.create(
            reference_number='EDIV/2024/REG/0030',
            title='Document to File',
            document_type='CORRESPONDENCE',
            created_by=self.user,
            status='APPROVED'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

    def test_filing_auto_sets_filed_by(self):
        response = self.client.post('/api/registry/filings/', {
            'document': self.doc.id,
            'file_code': 'FIL/2024/001',
            'filed_date': '2026-07-24',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        filing = Filing.objects.get(id=response.data['id'])
        self.assertEqual(filing.filed_by, self.user)
