"""Enhanced Search Service with Elasticsearch integration and database fallback."""
import logging
from django.db.models import Q
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


class SearchService:
    """Service for searching files with Elasticsearch fallback to database."""

    ES_AVAILABLE = False
    _es_client = None

    @classmethod
    def _get_es_client(cls):
        """Get or create Elasticsearch client."""
        if cls._es_client is not None:
            return cls._es_client

        es_hosts = getattr(settings, 'ELASTICSEARCH_HOSTS', None)
        if not es_hosts:
            return None

        try:
            from elasticsearch import Elasticsearch
            cls._es_client = Elasticsearch(es_hosts)
            if cls._es_client.ping():
                cls.ES_AVAILABLE = True
                logger.info("Elasticsearch connected successfully")
            else:
                logger.warning("Elasticsearch connection failed")
                cls._es_client = None
        except Exception as e:
            logger.warning(f"Elasticsearch not available: {e}")
            cls._es_client = None

        return cls._es_client

    @classmethod
    def index_file(cls, file):
        """Index a file in Elasticsearch."""
        es = cls._get_es_client()
        if not es:
            return False

        index_name = getattr(settings, 'ELASTICSEARCH_INDEX_NAME', 'files')
        try:
            doc = {
                'file_number': file.file_number,
                'title': file.title,
                'description': file.description,
                'status': file.status,
                'priority': file.priority,
                'classification': file.classification,
                'file_type': file.file_type,
                'file_category': file.file_category,
                'direction': getattr(file, 'direction', 'INCOMING'),
                'current_holder': {
                    'id': file.current_holder.id,
                    'name': file.current_holder.get_full_name() if file.current_holder else None,
                } if file.current_holder else None,
                'department': {
                    'id': file.department.id,
                    'name': file.department.name,
                } if file.department else None,
                'created_by': {
                    'id': file.created_by.id,
                    'name': file.created_by.get_full_name(),
                } if file.created_by else None,
                'tags': file.tags or [],
                'created_at': file.created_at.isoformat() if file.created_at else None,
                'updated_at': file.updated_at.isoformat() if file.updated_at else None,
                'due_date': file.due_date.isoformat() if file.due_date else None,
            }
            es.index(index=index_name, id=file.id, body=doc)
            return True
        except Exception as e:
            logger.error(f"Error indexing file {file.id}: {e}")
            return False

    @classmethod
    def delete_file_index(cls, file_id):
        """Delete file from Elasticsearch index."""
        es = cls._get_es_client()
        if not es:
            return False

        index_name = getattr(settings, 'ELASTICSEARCH_INDEX_NAME', 'files')
        try:
            es.delete(index=index_name, id=file_id)
            return True
        except Exception as e:
            logger.error(f"Error deleting file index {file_id}: {e}")
            return False

    @classmethod
    def search_files(cls, *, query=None, file_type=None, status=None, classification=None,
                     priority=None, department=None, school=None,
                     created_by=None, current_holder=None,
                     date_from=None, date_to=None,
                     tags=None, sort_by='-created_at', limit=50, offset=0) -> dict:
        """
        Search files using Elasticsearch with database fallback.
        Returns: {'results': list, 'total': int, 'offset': int, 'limit': int}
        """
        # Try Elasticsearch first
        es = cls._get_es_client()
        if es and query:
            try:
                return cls._es_search(
                    query=query, file_type=file_type, status=status,
                    classification=classification, priority=priority,
                    department=department, limit=limit, offset=offset,
                )
            except Exception as e:
                logger.warning(f"Elasticsearch search failed, falling back to database: {e}")

        # Database fallback
        return cls._db_search(
            query=query, file_type=file_type, status=status,
            classification=classification, priority=priority,
            department=department, school=school,
            created_by=created_by, current_holder=current_holder,
            date_from=date_from, date_to=date_to,
            tags=tags, sort_by=sort_by, limit=limit, offset=offset,
        )

    @classmethod
    def _es_search(cls, *, query, file_type=None, status=None, classification=None,
                   priority=None, department=None, limit=50, offset=0):
        """Elasticsearch-based search."""
        es = cls._get_es_client()
        index_name = getattr(settings, 'ELASTICSEARCH_INDEX_NAME', 'files')

        must = [{
            'multi_match': {
                'query': query,
                'fields': [
                    'title^3',
                    'description^2',
                    'file_number^2',
                    'tags^1.5',
                    'current_holder.name^1',
                    'department.name^1',
                ],
                'fuzziness': 'AUTO',
            }
        }]

        filters = []
        if file_type:
            filters.append({'term': {'file_type': file_type}})
        if status:
            filters.append({'term': {'status': status}})
        if classification:
            filters.append({'term': {'classification': classification}})
        if priority:
            filters.append({'term': {'priority': priority}})

        body = {
            'query': {'bool': {'must': must}},
            'from': offset,
            'size': limit,
            'sort': [{'created_at': {'order': 'desc'}}],
            'highlight': {
                'fields': {
                    'title': {},
                    'description': {},
                    'tags': {},
                }
            },
        }

        if filters:
            body['query']['bool']['filter'] = filters

        response = es.search(index=index_name, body=body)

        results = []
        for hit in response['hits']['hits']:
            source = hit['_source']
            results.append({
                'id': hit['_id'],
                'file_number': source.get('file_number'),
                'title': source.get('title'),
                'description': source.get('description'),
                'status': source.get('status'),
                'priority': source.get('priority'),
                'classification': source.get('classification'),
                'file_type': source.get('file_type'),
                'current_holder': source.get('current_holder'),
                'department': source.get('department'),
                'created_at': source.get('created_at'),
                'score': hit['_score'],
                'highlights': hit.get('highlight', {}),
            })

        total = response['hits']['total']['value']
        return {
            'results': results,
            'total': total,
            'offset': offset,
            'limit': limit,
            'source': 'elasticsearch',
        }

    @classmethod
    def _db_search(cls, *, query=None, file_type=None, status=None, classification=None,
                   priority=None, department=None, school=None,
                   created_by=None, current_holder=None,
                   date_from=None, date_to=None,
                   tags=None, sort_by='-created_at', limit=50, offset=0):
        """Database-based search fallback."""
        from apps.files.models import File

        qs = File.objects.select_related('created_by', 'current_holder', 'department', 'school')

        if query:
            qs = qs.filter(
                Q(title__icontains=query) |
                Q(file_number__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__icontains=query)
            )
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
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        if tags:
            tag_filter = Q()
            for tag in tags:
                tag_filter |= Q(tags__icontains=tag)
            qs = qs.filter(tag_filter)

        allowed_sorts = {
            'created_at': 'created_at', '-created_at': '-created_at',
            'title': 'title', '-title': '-title',
            'status': 'status', 'priority': 'priority',
            'due_date': 'due_date', '-due_date': '-due_date',
        }
        sort_field = allowed_sorts.get(sort_by, '-created_at')
        qs = qs.order_by(sort_field)

        total = qs.count()
        qs = qs[offset:offset + limit]

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
            'source': 'database',
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

    @classmethod
    def reindex_all(cls):
        """Reindex all files in Elasticsearch."""
        from apps.files.models import File
        es = cls._get_es_client()
        if not es:
            return {'error': 'Elasticsearch not available'}

        count = 0
        for file_obj in File.objects.all():
            if cls.index_file(file_obj):
                count += 1

        return {'indexed': count, 'total': File.objects.count()}
