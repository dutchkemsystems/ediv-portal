"""Search service with Elasticsearch fallback to database search."""
import logging
from django.db.models import Q
from django.utils import timezone

logger = logging.getLogger(__name__)


class SearchService:
    """Service for searching files with multiple criteria."""

    # Elasticsearch availability flag
    ES_AVAILABLE = False

    try:
        from elasticsearch import Elasticsearch
        ES_AVAILABLE = True
    except ImportError:
        pass

    @staticmethod
    def search_files(*, query=None, file_type=None, status=None, classification=None,
                     priority=None, department=None, school=None,
                     created_by=None, current_holder=None,
                     date_from=None, date_to=None,
                     tags=None, sort_by='-created_at', limit=50, offset=0) -> dict:
        """
        Search files with multiple filters.

        Returns: {'results': list, 'total': int, 'offset': int, 'limit': int}
        """
        from apps.files.models import File

        qs = File.objects.select_related('created_by', 'current_holder', 'department', 'school')

        # Text search
        if query:
            qs = qs.filter(
                Q(title__icontains=query) |
                Q(file_number__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__icontains=query)
            )

        # Filters
        if file_type:
            qs = qs.filter(file_type=file_type)
        if status:
            qs = qs.filter(status=status)
        if classification:
            qs = qs.filter(classification=classification)
        if priority:
            qs = qs.filter(priority=priority)
        if department:
            qs = qs.filter(department_id=department)
        if school:
            qs = qs.filter(school_id=school)
        if created_by:
            qs = qs.filter(created_by_id=created_by)
        if current_holder:
            qs = qs.filter(current_holder_id=current_holder)

        # Date range
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        # Tags filter - use icontains for broad compatibility (SQLite doesn't support JSON __contains)
        if tags:
            tag_filter = Q()
            for tag in tags:
                # Search in the JSON text representation for compatibility
                tag_filter |= Q(tags__icontains=tag)
            qs = qs.filter(tag_filter)

        # Sorting
        allowed_sorts = {
            'created_at': 'created_at',
            '-created_at': '-created_at',
            'title': 'title',
            '-title': '-title',
            'status': 'status',
            'priority': 'priority',
            'due_date': 'due_date',
            '-due_date': '-due_date',
        }
        sort_field = allowed_sorts.get(sort_by, '-created_at')
        qs = qs.order_by(sort_field)

        # Count before pagination
        total = qs.count()

        # Pagination
        qs = qs[offset:offset + limit]

        # Serialize results
        results = []
        for f in qs:
            results.append({
                'id': f.id,
                'file_number': f.file_number,
                'title': f.title,
                'file_type': f.file_type,
                'file_category': f.file_category,
                'status': f.status,
                'classification': f.classification,
                'priority': f.priority,
                'created_by': {
                    'id': f.created_by.id,
                    'name': f.created_by.get_full_name() or f.created_by.username,
                } if f.created_by else None,
                'current_holder': {
                    'id': f.current_holder.id,
                    'name': f.current_holder.get_full_name() or f.current_holder.username,
                } if f.current_holder else None,
                'department': {
                    'id': f.department.id,
                    'name': f.department.name,
                } if f.department else None,
                'school': {
                    'id': f.school.id,
                    'name': f.school.name,
                } if f.school else None,
                'due_date': f.due_date.isoformat() if f.due_date else None,
                'tags': f.tags or [],
                'created_at': f.created_at.isoformat() if f.created_at else None,
                'updated_at': f.updated_at.isoformat() if f.updated_at else None,
            })

        return {
            'results': results,
            'total': total,
            'offset': offset,
            'limit': limit,
        }

    @staticmethod
    def search_movements(*, file_id=None, from_holder=None, to_holder=None,
                         action=None, date_from=None, date_to=None,
                         limit=50, offset=0) -> dict:
        """Search file movements."""
        from apps.files.models import FileMovement

        qs = FileMovement.objects.select_related('file', 'from_holder', 'to_holder')

        if file_id:
            qs = qs.filter(file_id=file_id)
        if from_holder:
            qs = qs.filter(from_holder_id=from_holder)
        if to_holder:
            qs = qs.filter(to_holder_id=to_holder)
        if action:
            qs = qs.filter(action=action)
        if date_from:
            qs = qs.filter(movement_date__date__gte=date_from)
        if date_to:
            qs = qs.filter(movement_date__date__lte=date_to)

        total = qs.count()
        qs = qs.order_by('-movement_date')[offset:offset + limit]

        results = []
        for m in qs:
            results.append({
                'id': m.id,
                'file_number': m.file.file_number,
                'file_title': m.file.title,
                'from_holder': m.from_holder.get_full_name() or m.from_holder.username,
                'to_holder': m.to_holder.get_full_name() or m.to_holder.username if m.to_holder else None,
                'action': m.action,
                'remarks': m.remarks,
                'movement_date': m.movement_date.isoformat(),
            })

        return {'results': results, 'total': total, 'offset': offset, 'limit': limit}

    @staticmethod
    def get_search_suggestions(query, limit=10) -> list:
        """Get search suggestions based on partial query."""
        from apps.files.models import File

        if not query or len(query) < 2:
            return []

        files = File.objects.filter(
            Q(file_number__icontains=query) |
            Q(title__icontains=query)
        ).values('file_number', 'title')[:limit]

        return list(files)
