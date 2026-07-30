from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.schools.models import School
from apps.academics.models import Subject
from .models import Course, CourseModule, Lesson

User = get_user_model()


class CourseModelTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.user = User.objects.create_user(
            email='teacher@test.com', password='TestPass123!',
            first_name='Teacher', last_name='One', role='TCH'
        )
        self.subject = Subject.objects.create(name='Mathematics', code='MATH')

    def test_course_str(self):
        course = Course.objects.create(
            school=self.school, title='Algebra 101', code='ALG101',
            description='Basic algebra', subject=self.subject,
            instructor=self.user
        )
        self.assertEqual(str(course), 'ALG101 - Algebra 101')


class CourseModuleModelTest(TestCase):
    def setUp(self):
        school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        user = User.objects.create_user(
            email='teacher@test.com', password='TestPass123!',
            first_name='Teacher', last_name='One', role='TCH'
        )
        subject = Subject.objects.create(name='Math', code='MATH')
        self.course = Course.objects.create(
            school=school, title='Algebra', code='ALG',
            description='Algebra course', subject=subject, instructor=user
        )
        self.module = CourseModule.objects.create(
            course=self.course, title='Introduction', order=1
        )

    def test_module_str(self):
        self.assertEqual(str(self.module), 'Algebra - Introduction')


class ELearningAPITest(APITestCase):
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

    def test_list_courses(self):
        response = self.client.get('/api/e-learning/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
