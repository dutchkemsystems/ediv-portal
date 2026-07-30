from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.schools.models import School
from decimal import Decimal
from .models import Book, BookLoan

User = get_user_model()


class BookModelTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.book = Book.objects.create(
            school=self.school, title='Things Fall Apart',
            author='Chinua Achebe', isbn='978-0435913502',
            category='LITERATURE', total_copies=5, available_copies=3
        )

    def test_book_str(self):
        self.assertEqual(str(self.book), 'Things Fall Apart by Chinua Achebe')

    def test_is_available(self):
        self.assertTrue(self.book.is_available)

    def test_not_available(self):
        self.book.available_copies = 0
        self.book.save()
        self.assertFalse(self.book.is_available)


class BookLoanModelTest(TestCase):
    def setUp(self):
        school = School.objects.create(
            name='Test School', code='TST', school_type='SENIOR',
            lga='APAPA', address='123 Street'
        )
        self.book = Book.objects.create(
            school=school, title='Test Book', author='Author',
            isbn='978-0000000001', category='FICTION'
        )
        self.user = User.objects.create_user(
            email='student@test.com', password='TestPass123!',
            first_name='Student', last_name='One', role='STD'
        )
        self.loan = BookLoan.objects.create(
            book=self.book, borrower=self.user,
            loan_date='2026-01-01', due_date='2026-01-15'
        )

    def test_loan_str(self):
        self.assertIn('Test Book', str(self.loan))


class LibraryAPITest(APITestCase):
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

    def test_list_books(self):
        response = self.client.get('/api/library/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_book(self):
        response = self.client.post('/api/library/books/', {
            'school': self.school.id, 'title': 'New Book',
            'author': 'Author', 'isbn': '978-0000000002',
            'category': 'TEXTBOOK', 'total_copies': 10,
            'available_copies': 10
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_loans(self):
        response = self.client.get('/api/library/loans/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
