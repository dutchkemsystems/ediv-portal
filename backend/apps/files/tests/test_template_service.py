"""Tests for TemplateService."""
from django.test import TestCase
from apps.users.models import User
from apps.departments.models import Department
from apps.files.models import File, FileTemplate, FileMovement
from apps.files.services.template_service import TemplateService


class TemplateServiceCreateTest(TestCase):
    """Tests for TemplateService.create_template"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='creator@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Creator',
            last_name='User',
            role='SYSADMIN'
        )
        self.department = Department.objects.create(
            name='Admin',
            code='ADM',
            category='CORE'
        )

    def test_create_template_minimal(self):
        """Create template with required fields only."""
        template = TemplateService.create_template(
            name='Test Template',
            description='A test template',
            category='CORRESPONDENCE',
            file_type='CORRESPONDENCE',
            file_category='CORR',
            created_by=self.user,
        )
        self.assertIsNotNone(template.id)
        self.assertEqual(template.name, 'Test Template')
        self.assertEqual(template.category, 'CORRESPONDENCE')
        self.assertEqual(template.file_type, 'CORRESPONDENCE')
        self.assertEqual(template.file_category, 'CORR')
        self.assertEqual(template.default_classification, 'INTERNAL')
        self.assertEqual(template.default_priority, 'NORMAL')
        self.assertEqual(template.template_content, '')
        self.assertEqual(template.template_fields, {})
        self.assertTrue(template.is_active)
        self.assertEqual(template.usage_count, 0)
        self.assertEqual(template.created_by, self.user)

    def test_create_template_with_all_fields(self):
        """Create template with all optional fields specified."""
        fields_schema = {'recipient': {'type': 'text', 'required': True}, 'subject': {'type': 'text', 'required': True}}
        template = TemplateService.create_template(
            name='Full Template',
            description='Complete template',
            category='MEMO',
            file_type='MEMO',
            file_category='ADMIN',
            default_department=self.department,
            default_classification='CONFIDENTIAL',
            default_priority='HIGH',
            template_content='Default memo body',
            template_fields=fields_schema,
            created_by=self.user,
        )
        self.assertEqual(template.default_department, self.department)
        self.assertEqual(template.default_classification, 'CONFIDENTIAL')
        self.assertEqual(template.default_priority, 'HIGH')
        self.assertEqual(template.template_content, 'Default memo body')
        self.assertEqual(template.template_fields, fields_schema)

    def test_create_template_default_department_none(self):
        """Default department should be None when not specified."""
        template = TemplateService.create_template(
            name='No Dept Template',
            description='',
            category='OTHER',
            file_type='OTHER',
            file_category='ADMIN',
            created_by=self.user,
        )
        self.assertIsNone(template.default_department)

    def test_create_template_is_active_true(self):
        """New template should be active by default."""
        template = TemplateService.create_template(
            name='Active Template',
            description='',
            category='OTHER',
            file_type='OTHER',
            file_category='ADMIN',
            created_by=self.user,
        )
        self.assertTrue(template.is_active)

    def test_create_template_usage_count_zero(self):
        """New template should have zero usage count."""
        template = TemplateService.create_template(
            name='Unused Template',
            description='',
            category='OTHER',
            file_type='OTHER',
            file_category='ADMIN',
            created_by=self.user,
        )
        self.assertEqual(template.usage_count, 0)


class TemplateServiceUpdateTest(TestCase):
    """Tests for TemplateService.update_template"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='updater@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Updater',
            last_name='User',
            role='SYSADMIN'
        )
        self.template = FileTemplate.objects.create(
            name='Original Name',
            description='Original description',
            category='CORRESPONDENCE',
            file_type='CORRESPONDENCE',
            file_category='CORR',
            created_by=self.user,
        )

    def test_update_template_name(self):
        """Update template name."""
        updated = TemplateService.update_template(
            template=self.template,
            name='Updated Name'
        )
        self.assertEqual(updated.name, 'Updated Name')
        updated_from_db = FileTemplate.objects.get(id=self.template.id)
        self.assertEqual(updated_from_db.name, 'Updated Name')

    def test_update_template_description(self):
        """Update template description."""
        updated = TemplateService.update_template(
            template=self.template,
            description='Updated description'
        )
        self.assertEqual(updated.description, 'Updated description')

    def test_update_template_category(self):
        """Update template category."""
        updated = TemplateService.update_template(
            template=self.template,
            category='MEMO'
        )
        self.assertEqual(updated.category, 'MEMO')

    def test_update_template_multiple_fields(self):
        """Update multiple fields at once."""
        updated = TemplateService.update_template(
            template=self.template,
            name='Multi Update',
            description='Multi desc',
            category='POLICY',
            default_priority='URGENT',
        )
        self.assertEqual(updated.name, 'Multi Update')
        self.assertEqual(updated.description, 'Multi desc')
        self.assertEqual(updated.category, 'POLICY')
        self.assertEqual(updated.default_priority, 'URGENT')

    def test_update_template_returns_same_instance(self):
        """Update should return the same template instance."""
        updated = TemplateService.update_template(
            template=self.template,
            name='Same Instance'
        )
        self.assertEqual(updated.id, self.template.id)

    def test_update_template_no_changes(self):
        """Update with no kwargs should return unchanged template."""
        updated = TemplateService.update_template(template=self.template)
        self.assertEqual(updated.name, 'Original Name')
        self.assertEqual(updated.description, 'Original description')


class TemplateServiceDeleteTest(TestCase):
    """Tests for TemplateService.delete_template (soft delete)"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='deleter@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Deleter',
            last_name='User',
            role='SYSADMIN'
        )
        self.template = FileTemplate.objects.create(
            name='To Delete',
            description='Will be soft deleted',
            category='OTHER',
            created_by=self.user,
        )

    def test_delete_sets_inactive(self):
        """Soft delete should set is_active to False."""
        result = TemplateService.delete_template(template=self.template)
        self.assertTrue(result)
        self.template.refresh_from_db()
        self.assertFalse(self.template.is_active)

    def test_delete_returns_true(self):
        """Soft delete should return True on success."""
        result = TemplateService.delete_template(template=self.template)
        self.assertTrue(result)

    def test_template_still_exists_after_delete(self):
        """Template should still exist in database after soft delete."""
        TemplateService.delete_template(template=self.template)
        self.assertTrue(FileTemplate.objects.filter(id=self.template.id).exists())

    def test_double_delete_is_idempotent(self):
        """Deleting an already deleted template should still succeed."""
        TemplateService.delete_template(template=self.template)
        result = TemplateService.delete_template(template=self.template)
        self.assertTrue(result)
        self.template.refresh_from_db()
        self.assertFalse(self.template.is_active)


class TemplateServiceGetTemplatesTest(TestCase):
    """Tests for TemplateService.get_templates"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='getter@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Getter',
            last_name='User',
            role='SYSADMIN'
        )
        self.active_memo = FileTemplate.objects.create(
            name='Active Memo', category='MEMO', is_active=True, created_by=self.user,
        )
        self.active_corr = FileTemplate.objects.create(
            name='Active Correspondence', category='CORRESPONDENCE', is_active=True, created_by=self.user,
        )
        self.inactive = FileTemplate.objects.create(
            name='Inactive Template', category='OTHER', is_active=False, created_by=self.user,
        )

    def test_get_all_active_templates(self):
        """Get all active templates by default."""
        templates = TemplateService.get_templates()
        self.assertEqual(len(templates), 2)
        names = [t.name for t in templates]
        self.assertIn('Active Memo', names)
        self.assertIn('Active Correspondence', names)
        self.assertNotIn('Inactive Template', names)

    def test_get_templates_filter_by_category(self):
        """Filter templates by category."""
        templates = TemplateService.get_templates(category='MEMO')
        self.assertEqual(len(templates), 1)
        self.assertEqual(templates[0].name, 'Active Memo')

    def test_get_templates_include_inactive(self):
        """Include inactive templates when is_active=False."""
        templates = TemplateService.get_templates(is_active=False)
        self.assertEqual(len(templates), 1)
        self.assertEqual(templates[0].name, 'Inactive Template')

    def test_get_templates_empty_category(self):
        """Return empty list for category with no templates."""
        templates = TemplateService.get_templates(category='CONTRACT')
        self.assertEqual(len(templates), 0)

    def test_get_templates_all_active_ordered_by_usage(self):
        """Active templates should be returned ordered by usage_count descending."""
        self.active_memo.usage_count = 10
        self.active_memo.save()
        self.active_corr.usage_count = 5
        self.active_corr.save()
        templates = TemplateService.get_templates()
        self.assertEqual(templates[0], self.active_memo)
        self.assertEqual(templates[1], self.active_corr)


class TemplateServiceGenerateFileTest(TestCase):
    """Tests for TemplateService.generate_file_from_template"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='genuser@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Gen',
            last_name='User',
            role='SYSADMIN'
        )
        self.department = Department.objects.create(
            name='Academics',
            code='ACD',
            category='CORE'
        )
        self.template = FileTemplate.objects.create(
            name='Correspondence Template',
            description='Standard correspondence',
            category='CORRESPONDENCE',
            file_type='CORRESPONDENCE',
            file_category='CORR',
            default_department=self.department,
            default_classification='CONFIDENTIAL',
            default_priority='HIGH',
            template_content='Dear {{recipient}},\n\nThis is regarding {{subject}}.',
            template_fields={
                'recipient': {'type': 'text', 'required': True},
                'subject': {'type': 'text', 'required': True},
            },
            created_by=self.user,
        )

    def test_generate_file_from_template(self):
        """Generate a file from template with field values."""
        file = TemplateService.generate_file_from_template(
            template=self.template,
            title='Generated Correspondence',
            created_by=self.user,
            field_values={
                'recipient': 'Mr. Smith',
                'subject': 'Annual Report',
            },
        )
        self.assertIsNotNone(file.id)
        self.assertEqual(file.title, 'Generated Correspondence')
        self.assertEqual(file.file_type, 'CORRESPONDENCE')
        self.assertEqual(file.file_category, 'CORR')
        self.assertEqual(file.department, self.department)
        self.assertEqual(file.classification, 'CONFIDENTIAL')
        self.assertEqual(file.priority, 'HIGH')
        self.assertEqual(file.description, 'Dear Mr. Smith,\n\nThis is regarding Annual Report.')
        self.assertEqual(file.created_by, self.user)
        self.assertEqual(file.current_holder, self.user)

    def test_generate_file_increments_usage_count(self):
        """Generating a file should increment template usage_count."""
        initial_count = self.template.usage_count
        TemplateService.generate_file_from_template(
            template=self.template,
            title='Test',
            created_by=self.user,
        )
        self.template.refresh_from_db()
        self.assertEqual(self.template.usage_count, initial_count + 1)

    def test_generate_file_creates_movement(self):
        """Generating a file should record a CREATED movement."""
        file = TemplateService.generate_file_from_template(
            template=self.template,
            title='Movement Test',
            created_by=self.user,
        )
        movement = FileMovement.objects.get(file=file)
        self.assertEqual(movement.action, FileMovement.Action.CREATED)
        self.assertEqual(movement.from_holder, self.user)

    def test_generate_file_with_overrides(self):
        """Overrides should take precedence over template defaults."""
        file = TemplateService.generate_file_from_template(
            template=self.template,
            title='Override Test',
            created_by=self.user,
            classification='PUBLIC',
            priority='LOW',
        )
        self.assertEqual(file.classification, 'PUBLIC')
        self.assertEqual(file.priority, 'LOW')

    def test_generate_file_no_field_values(self):
        """Generate file without field_values should work (description empty or template content)."""
        file = TemplateService.generate_file_from_template(
            template=self.template,
            title='No Fields Test',
            created_by=self.user,
        )
        self.assertIsNotNone(file.id)
        self.assertEqual(file.file_type, 'CORRESPONDENCE')

    def test_generate_file_returns_file_instance(self):
        """Should return a File instance."""
        file = TemplateService.generate_file_from_template(
            template=self.template,
            title='Instance Test',
            created_by=self.user,
        )
        self.assertIsInstance(file, File)

    def test_generate_file_sets_status_draft(self):
        """Generated file should default to DRAFT status."""
        file = TemplateService.generate_file_from_template(
            template=self.template,
            title='Status Test',
            created_by=self.user,
        )
        self.assertEqual(file.status, 'DRAFT')

    def test_generate_file_multiple_generations(self):
        """Multiple files can be generated from same template."""
        f1 = TemplateService.generate_file_from_template(
            template=self.template, title='File 1', created_by=self.user,
        )
        f2 = TemplateService.generate_file_from_template(
            template=self.template, title='File 2', created_by=self.user,
        )
        self.assertNotEqual(f1.file_number, f2.file_number)
        self.template.refresh_from_db()
        self.assertEqual(self.template.usage_count, 2)

    def test_generate_file_with_empty_template_fields(self):
        """Template with no fields schema should still generate file."""
        simple_template = FileTemplate.objects.create(
            name='Simple Template',
            category='OTHER',
            file_type='OTHER',
            file_category='ADMIN',
            template_content='Plain content',
            template_fields={},
            created_by=self.user,
        )
        file = TemplateService.generate_file_from_template(
            template=simple_template,
            title='Simple File',
            created_by=self.user,
        )
        self.assertIsNotNone(file.id)
        self.assertEqual(file.description, 'Plain content')


class TemplateServiceUsageStatsTest(TestCase):
    """Tests for TemplateService.get_template_usage_stats"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='statsuser@ediv.gov.ng',
            password='TestPass123!@#',
            first_name='Stats',
            last_name='User',
            role='SYSADMIN'
        )
        self.t1 = FileTemplate.objects.create(
            name='Popular', category='MEMO', usage_count=15, is_active=True, created_by=self.user,
        )
        self.t2 = FileTemplate.objects.create(
            name='Less Popular', category='CORRESPONDENCE', usage_count=3, is_active=True, created_by=self.user,
        )
        self.t3 = FileTemplate.objects.create(
            name='Unused', category='OTHER', usage_count=0, is_active=True, created_by=self.user,
        )
        self.inactive = FileTemplate.objects.create(
            name='Inactive', category='OTHER', usage_count=20, is_active=False, created_by=self.user,
        )

    def test_usage_stats_returns_all_active(self):
        """Stats should include all active templates."""
        stats = TemplateService.get_template_usage_stats()
        names = [s['name'] for s in stats]
        self.assertIn('Popular', names)
        self.assertIn('Less Popular', names)
        self.assertIn('Unused', names)
        self.assertNotIn('Inactive', names)

    def test_usage_stats_ordered_by_usage(self):
        """Stats should be ordered by usage_count descending."""
        stats = TemplateService.get_template_usage_stats()
        self.assertEqual(stats[0]['name'], 'Popular')
        self.assertEqual(stats[0]['usage_count'], 15)
        self.assertEqual(stats[1]['name'], 'Less Popular')
        self.assertEqual(stats[1]['usage_count'], 3)

    def test_usage_stats_structure(self):
        """Each stat entry should have required keys."""
        stats = TemplateService.get_template_usage_stats()
        for stat in stats:
            self.assertIn('id', stat)
            self.assertIn('name', stat)
            self.assertIn('category', stat)
            self.assertIn('usage_count', stat)
            self.assertIn('is_active', stat)

    def test_usage_stats_empty_when_no_active(self):
        """Empty list when no active templates."""
        FileTemplate.objects.update(is_active=False)
        stats = TemplateService.get_template_usage_stats()
        self.assertEqual(len(stats), 0)
