from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import User
from .models import Workflow, WorkflowStep, WorkflowInstance, Task


class WorkflowModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Test',
            last_name='User',
            role='SYSADMIN'
        )
        self.workflow = Workflow.objects.create(
            name='File Approval Workflow',
            description='Standard file approval process',
            created_by=self.user,
            status='ACTIVE'
        )
        self.step = WorkflowStep.objects.create(
            workflow=self.workflow,
            name='Manager Approval',
            step_type='APPROVAL',
            order=1,
            is_required=True
        )
    
    def test_workflow_str(self):
        self.assertEqual(str(self.workflow), 'File Approval Workflow')
    
    def test_step_str(self):
        self.assertEqual(str(self.step), 'File Approval Workflow - Step 1: Manager Approval')


class WorkflowAPITest(APITestCase):
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
        
        self.workflow = Workflow.objects.create(
            name='Test Workflow',
            description='Test workflow',
            created_by=self.admin,
            status='ACTIVE'
        )
    
    def test_list_workflows(self):
        response = self.client.get('/api/workflows/workflows/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_workflow(self):
        data = {
            'name': 'New Workflow',
            'description': 'New workflow description',
            'created_by': self.admin.id,
            'status': 'DRAFT'
        }
        response = self.client.post('/api/workflows/workflows/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
