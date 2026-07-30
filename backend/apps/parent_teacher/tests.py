from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.schools.models import School
from .models import PTAMeeting, ParentTeacherMessage

User = get_user_model()


class PTAMeetingModelTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.user = User.objects.create_user(
            email='principal@test.com', password='TestPass123!',
            first_name='Principal', last_name='One', role='PRI'
        )
        self.meeting = PTAMeeting.objects.create(
            title='Q1 PTA Meeting', meeting_type='PARENT_TEACHER',
            school=self.school, scheduled_date='2026-03-15',
            scheduled_time='10:00', venue='School Hall',
            organized_by=self.user
        )

    def test_meeting_str(self):
        self.assertIn('Q1 PTA Meeting', str(self.meeting))


class ParentTeacherMessageModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            email='teacher@test.com', password='TestPass123!',
            first_name='Teacher', last_name='One', role='TCH'
        )
        self.parent = User.objects.create_user(
            email='parent@test.com', password='TestPass123!',
            first_name='Parent', last_name='One', role='PAR'
        )
        from apps.schools.models import School
        from apps.students.models import Student
        school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.student = Student.objects.create(
            user=User.objects.create_user(
                email='student@test.com', password='TestPass123!',
                first_name='Student', last_name='One', role='STD'
            ), admission_number='ADM001', school=school,
            date_of_birth='2010-01-01', gender='M',
            state_of_origin='Lagos', lga_of_origin='Mainland',
            residential_address='123 Street', parent_name='Parent',
            parent_phone='08012345678', emergency_contact_name='Emergency',
            emergency_contact_phone='08012345678', admission_date='2024-09-01'
        )
        self.message = ParentTeacherMessage.objects.create(
            sender=self.teacher, recipient=self.parent,
            student=self.student, subject='Progress Update',
            body='Your child is doing well in class.'
        )

    def test_message_str(self):
        self.assertIn('Progress Update', str(self.message))


class ParentTeacherAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com', password='TestPass123!',
            first_name='Test', last_name='User', role='SYSADMIN'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

    def test_list_meetings(self):
        response = self.client.get('/api/parent-teacher/meetings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_messages(self):
        response = self.client.get('/api/parent-teacher/messages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
