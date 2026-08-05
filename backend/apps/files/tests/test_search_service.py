"""Tests for enhanced SearchService."""
from django.test import TestCase
from apps.users.models import User
from apps.departments.models import Department
from apps.files.models import File
from apps.files.services.search_service import SearchService


class SearchServiceDatabaseSearchTest(TestCase):
    """Tests for database search fallback."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='searcher@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Search',
            last_name='User',
            role='SYSADMIN'
        )
        self.dept = Department.objects.create(name='Finance', code='FIN', category='CORE')
        self.file1 = File.objects.create(
            file_number='EDIV-2026-SRC-001',
            title='Budget Report 2026',
            file_type='REPORT',
            file_category='FIN',
            description='Annual budget report for all schools',
            created_by=self.user,
            current_holder=self.user,
            department=self.dept,
            status='ACTIVE',
            priority='HIGH',
        )
        self.file2 = File.objects.create(
            file_number='EDIV-2026-SRC-002',
            title='Student Enrollment',
            file_type='CORRESPONDENCE',
            file_category='ACAD',
            description='Student enrollment statistics',
            created_by=self.user,
            current_holder=self.user,
            status='ACTIVE',
        )

    def test_search_by_query(self):
        """Search by text query should find matching files."""
        results = SearchService.search_files(query='budget')
        self.assertEqual(results['total'], 1)
        self.assertEqual(results['results'][0]['title'], 'Budget Report 2026')

    def test_search_by_file_number(self):
        """Search by file number should find matching file."""
        results = SearchService.search_files(query='EDIV-2026-SRC-002')
        self.assertEqual(results['total'], 1)

    def test_search_by_status(self):
        """Filter by status."""
        self.file1.status = 'DRAFT'
        self.file1.save()
        results = SearchService.search_files(status='DRAFT')
        self.assertEqual(results['total'], 1)

    def test_search_by_priority(self):
        """Filter by priority."""
        results = SearchService.search_files(priority='HIGH')
        self.assertEqual(results['total'], 1)
        self.assertEqual(results['results'][0]['title'], 'Budget Report 2026')

    def test_search_by_department(self):
        """Filter by department."""
        results = SearchService.search_files(department=self.dept.id)
        self.assertEqual(results['total'], 1)

    def test_search_combined_filters(self):
        """Combined query and filters."""
        results = SearchService.search_files(query='budget', priority='HIGH')
        self.assertEqual(results['total'], 1)

    def test_search_no_results(self):
        """Search with no matches returns empty."""
        results = SearchService.search_files(query='nonexistent')
        self.assertEqual(results['total'], 0)

    def test_search_pagination(self):
        """Search respects limit and offset."""
        results = SearchService.search_files(limit=1, offset=0)
        self.assertEqual(len(results['results']), 1)
        self.assertEqual(results['total'], 2)

    def test_search_suggestions(self):
        """Search suggestions should return matching file numbers."""
        suggestions = SearchService.get_search_suggestions('EDIV')
        self.assertEqual(len(suggestions), 2)

    def test_search_suggestions_min_length(self):
        """Short queries should return empty suggestions."""
        suggestions = SearchService.get_search_suggestions('E')
        self.assertEqual(len(suggestions), 0)

    def test_search_all_files(self):
        """Search with no query should return all files."""
        results = SearchService.search_files()
        self.assertEqual(results['total'], 2)

    def test_search_by_created_by(self):
        """Filter by created_by."""
        results = SearchService.search_files(created_by=self.user.id)
        self.assertEqual(results['total'], 2)

    def test_search_by_current_holder(self):
        """Filter by current_holder."""
        results = SearchService.search_files(current_holder=self.user.id)
        self.assertEqual(results['total'], 2)

    def test_search_movements(self):
        """Search movements should work."""
        from apps.files.models import FileMovement
        FileMovement.objects.create(
            file=self.file1,
            from_holder=self.user,
            action='CREATED',
        )
        results = SearchService.search_movements(file_id=self.file1.id)
        self.assertEqual(results['total'], 1)

    def test_search_with_tags(self):
        """Search with tags filter."""
        self.file1.tags = ['budget', 'finance']
        self.file1.save()
        results = SearchService.search_files(tags=['budget'])
        self.assertEqual(results['total'], 1)
