"""Template service for reusable file templates."""
import datetime
from django.utils import timezone
from apps.files.models import File, FileMovement, FileTemplate


class TemplateService:
    """Service for managing file templates and generating files from templates."""

    @staticmethod
    def create_template(*, name, description, category, file_type, file_category,
                        default_department=None, default_classification='INTERNAL',
                        default_priority='NORMAL', template_content='',
                        template_fields=None, created_by) -> FileTemplate:
        """Create a new file template."""
        if template_fields is None:
            template_fields = {}
        template = FileTemplate.objects.create(
            name=name,
            description=description,
            category=category,
            file_type=file_type,
            file_category=file_category,
            default_department=default_department,
            default_classification=default_classification,
            default_priority=default_priority,
            template_content=template_content,
            template_fields=template_fields,
            created_by=created_by,
        )
        return template

    @staticmethod
    def update_template(*, template, **kwargs) -> FileTemplate:
        """Update an existing template."""
        for key, value in kwargs.items():
            setattr(template, key, value)
        template.save()
        return template

    @staticmethod
    def delete_template(*, template) -> bool:
        """Soft-delete (set is_active=False) a template."""
        template.is_active = False
        template.save()
        return True

    @staticmethod
    def get_templates(category=None, is_active=True) -> list:
        """Get all templates, optionally filtered by category."""
        qs = FileTemplate.objects.all()
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        if category:
            qs = qs.filter(category=category)
        return list(qs)

    @staticmethod
    def _generate_file_number(department=None):
        """Generate a unique file number: EDIV-{year}-{dept_code}-{seq}."""
        year = datetime.date.today().year
        dept_code = 'GEN'
        if department:
            dept_code = department.code[:3]
        seq = File.objects.filter(file_number__startswith=f'EDIV-{year}-{dept_code}').count() + 1
        return f'EDIV-{year}-{dept_code}-{seq:04d}'

    @staticmethod
    def generate_file_from_template(*, template, title, created_by,
                                     field_values=None, **overrides) -> File:
        """
        Generate a new File from a template.
        1. Create File with template defaults
        2. Apply field_values from template_fields schema
        3. Apply any overrides
        4. Increment template.usage_count
        5. Record CREATED movement
        6. Return the new File
        """
        if field_values is None:
            field_values = {}

        # Build description from template_content by substituting field values
        description = template.template_content
        if description and field_values:
            for field_key, field_val in field_values.items():
                description = description.replace('{{' + field_key + '}}', str(field_val))

        department = overrides.pop('department', template.default_department)

        file_number = TemplateService._generate_file_number(department=department)

        # Prepare file creation data from template defaults
        file_data = {
            'file_number': file_number,
            'title': title,
            'file_type': template.file_type,
            'file_category': template.file_category,
            'description': description,
            'created_by': created_by,
            'current_holder': created_by,
            'department': department,
            'classification': template.default_classification,
            'priority': template.default_priority,
            'status': 'DRAFT',
            'tags': [],
        }

        # Apply overrides
        file_data.update(overrides)

        file_obj = File.objects.create(**file_data)

        # Increment template usage count
        template.usage_count += 1
        template.save(update_fields=['usage_count'])

        # Record CREATED movement
        FileMovement.objects.create(
            file=file_obj,
            from_holder=created_by,
            action=FileMovement.Action.CREATED,
            remarks=f'File created from template: {template.name}',
        )

        return file_obj

    @staticmethod
    def get_template_usage_stats() -> list:
        """Return template usage statistics."""
        templates = FileTemplate.objects.filter(is_active=True)
        stats = []
        for t in templates:
            stats.append({
                'id': t.id,
                'name': t.name,
                'category': t.category,
                'usage_count': t.usage_count,
                'is_active': t.is_active,
            })
        return stats
