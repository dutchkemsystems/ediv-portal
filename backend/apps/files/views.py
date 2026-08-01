from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    File, FileMovement, FileAttachment, FileComment, FileStatus, FileCategory, SecurityClassification,
    WorkflowConfig, FileTemplate, FileClassification, OfflineQueue,
)
from .serializers import (
    FileSerializer, FileListSerializer,
    FileMovementSerializer, FileAttachmentSerializer, FileCommentSerializer,
    WorkflowConfigSerializer, FileTemplateSerializer, FileClassificationSerializer, OfflineQueueSerializer,
)


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.select_related('created_by', 'current_holder', 'department', 'school').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['file_type', 'status', 'classification', 'priority', 'department', 'school']
    search_fields = ['file_number', 'title', 'description']
    ordering_fields = ['file_number', 'created_at', 'due_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return FileListSerializer
        return FileSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ('SYSADMIN', 'TG_PS'):
            return File.objects.all()
        return File.objects.filter(
            models.Q(created_by=user) |
            models.Q(current_holder=user) |
            models.Q(classification='PUBLIC')
        ).distinct()

    def perform_create(self, serializer):
        import datetime
        year = datetime.date.today().year
        dept_code = 'GEN'
        if serializer.validated_data.get('department'):
            dept_code = serializer.validated_data['department'].code[:3]
        elif serializer.validated_data.get('school'):
            dept_code = serializer.validated_data['school'].code[:3]
        seq = File.objects.filter(file_number__startswith=f'EDIV-{year}-{dept_code}').count() + 1
        file_number = f'EDIV-{year}-{dept_code}-{seq:04d}'

        file_obj = serializer.save(
            file_number=file_number,
            created_by=self.request.user,
            current_holder=self.request.user,
        )

        from config.security import AuditLogger
        AuditLogger.log_action(
            user=self.request.user,
            action='CREATE',
            resource_type='File',
            resource_id=file_obj.id,
            description=f"Created file {file_number}: {file_obj.title}",
            new_value={'file_number': file_number, 'title': file_obj.title, 'status': file_obj.status},
        )

    @action(detail=True, methods=['post'], url_path='move')
    def move_file(self, request, pk=None):
        """Move a file to another holder. Creates a FileMovement record and updates current_holder.

        Body: { "to_holder_id": <int>, "action": <str>, "remarks": <str>, "expected_return_date": <date> }
        """
        file_obj = self.get_object()
        to_holder_id = request.data.get('to_holder_id')
        action_type = request.data.get('action', 'Forwarded')
        remarks = request.data.get('remarks', '')
        expected_return = request.data.get('expected_return_date')

        if not to_holder_id:
            return Response({'error': 'to_holder_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            to_holder = User.objects.get(id=to_holder_id)
        except User.DoesNotExist:
            return Response({'error': 'Target user not found.'}, status=status.HTTP_404_NOT_FOUND)

        movement = FileMovement.objects.create(
            file=file_obj,
            from_holder=file_obj.current_holder or request.user,
            to_holder=to_holder,
            action=action_type,
            remarks=remarks,
            expected_return_date=expected_return if expected_return else None,
        )

        import datetime as dt
        timeline_entry = {
            'timestamp': dt.datetime.now(dt.timezone.utc).isoformat(),
            'status': 'IN_TRANSIT',
            'changed_by_id': request.user.id,
            'changed_by_name': request.user.get_full_name(),
            'notes': f"Moved to {to_holder.get_full_name()}: {action_type}",
        }
        file_obj.status_timeline = (file_obj.status_timeline or []) + [timeline_entry]

        file_obj.current_holder = to_holder
        file_obj.status = 'IN_TRANSIT'
        file_obj.save(update_fields=['current_holder', 'status', 'status_timeline', 'updated_at'])

        from config.security import AuditLogger
        AuditLogger.log_action(
            user=request.user,
            action='FILE_MOVEMENT',
            resource_type='File',
            resource_id=file_obj.id,
            description=f"Moved {file_obj.file_number} from {file_obj.created_by.get_full_name()} to {to_holder.get_full_name()}: {action_type}",
            new_value={
                'file_number': file_obj.file_number,
                'from': file_obj.created_by.email,
                'to': to_holder.email,
                'action': action_type,
                'remarks': remarks,
            },
        )

        return Response({
            'message': f"File {file_obj.file_number} moved to {to_holder.get_full_name()}.",
            'movement': FileMovementSerializer(movement).data,
        })

    @action(detail=True, methods=['post'], url_path='receive')
    def receive_file(self, request, pk=None):
        """Mark a file as received by the current holder."""
        file_obj = self.get_object()

        if file_obj.current_holder != request.user:
            return Response(
                {'error': 'You are not the current holder of this file.'},
                status=status.HTTP_403_FORBIDDEN
            )

        file_obj.status = 'ACTIVE'
        file_obj.save(update_fields=['status', 'updated_at'])

        last_movement = FileMovement.objects.filter(file=file_obj).order_by('-movement_date').first()
        if last_movement and not last_movement.is_returned:
            completion_notes = request.data.get('completion_notes', '')
            last_movement.actual_return_date = __import__('datetime').date.today()
            last_movement.is_returned = True
            last_movement.completion_notes = completion_notes
            last_movement.save(update_fields=['actual_return_date', 'is_returned', 'completion_notes'])

        import datetime as dt
        timeline_entry = {
            'timestamp': dt.datetime.now(dt.timezone.utc).isoformat(),
            'status': 'ACTIVE',
            'changed_by_id': request.user.id,
            'changed_by_name': request.user.get_full_name(),
            'notes': f"Received by {request.user.get_full_name()}",
        }
        file_obj.status_timeline = (file_obj.status_timeline or []) + [timeline_entry]
        file_obj.save(update_fields=['status_timeline'])

        from config.security import AuditLogger
        AuditLogger.log_action(
            user=request.user,
            action='UPDATE',
            resource_type='File',
            resource_id=file_obj.id,
            description=f"File {file_obj.file_number} received by {request.user.get_full_name()}",
        )

        return Response({'message': f"File {file_obj.file_number} marked as received."})

    @action(detail=True, methods=['post'], url_path='close')
    def close_file(self, request, pk=None):
        """Archive/close a file. Only file creator or SYSADMIN/TG can close."""
        file_obj = self.get_object()
        user = request.user

        if user.role not in ('SYSADMIN', 'TG_PS') and file_obj.created_by != user:
            return Response(
                {'error': 'Only the file creator or Admin/TG/PS can close a file.'},
                status=status.HTTP_403_FORBIDDEN
            )

        file_obj.status = 'ARCHIVED'
        file_obj.save(update_fields=['status', 'updated_at'])

        import datetime as dt
        timeline_entry = {
            'timestamp': dt.datetime.now(dt.timezone.utc).isoformat(),
            'status': 'ARCHIVED',
            'changed_by_id': user.id,
            'changed_by_name': user.get_full_name(),
            'notes': f"File closed/archived by {user.get_full_name()}",
        }
        file_obj.status_timeline = (file_obj.status_timeline or []) + [timeline_entry]
        file_obj.save(update_fields=['status_timeline'])

        from config.security import AuditLogger
        AuditLogger.log_action(
            user=user,
            action='UPDATE',
            resource_type='File',
            resource_id=file_obj.id,
            description=f"File {file_obj.file_number} closed/archived by {user.get_full_name()}",
        )

        return Response({'message': f"File {file_obj.file_number} has been archived."})

    @action(detail=True, methods=['post'], url_path='log-status')
    def log_status_change(self, request, pk=None):
        """Log a manual status change with notes. Only current holder or creator can do this."""
        file_obj = self.get_object()
        user = request.user

        if file_obj.current_holder != user and file_obj.created_by != user and user.role not in ('SYSADMIN', 'TG_PS'):
            return Response(
                {'error': 'Only the current holder, file creator, or Admin can log status changes.'},
                status=status.HTTP_403_FORBIDDEN
            )

        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        valid_statuses = [choice[0] for choice in FileStatus.choices]
        if new_status and new_status not in valid_statuses:
            return Response({'error': f'Invalid status. Choose from: {valid_statuses}'}, status=status.HTTP_400_BAD_REQUEST)

        if new_status:
            file_obj.status = new_status
            file_obj.save(update_fields=['status', 'updated_at'])

        import datetime as dt
        timeline_entry = {
            'timestamp': dt.datetime.now(dt.timezone.utc).isoformat(),
            'status': new_status or file_obj.status,
            'changed_by_id': user.id,
            'changed_by_name': user.get_full_name(),
            'notes': notes,
        }
        file_obj.status_timeline = (file_obj.status_timeline or []) + [timeline_entry]
        file_obj.save(update_fields=['status_timeline'])

        from config.security import AuditLogger
        AuditLogger.log_action(
            user=user,
            action='UPDATE',
            resource_type='File',
            resource_id=file_obj.id,
            description=f"File {file_obj.file_number} status logged: {new_status or file_obj.status}",
        )

        return Response({
            'message': f"Status change logged for {file_obj.file_number}.",
            'timeline': file_obj.status_timeline,
        })

    @action(detail=True, methods=['post'], url_path='submit')
    def submit_file(self, request, pk=None):
        """Submit a file for review. Only file creator can submit."""
        file_obj = self.get_object()
        user = request.user

        if file_obj.created_by != user and user.role not in ('SYSADMIN', 'TG_PS'):
            return Response(
                {'error': 'Only the file creator or Admin can submit a file.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if file_obj.status != 'DRAFT':
            return Response(
                {'error': 'Only files in DRAFT status can be submitted.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        file_obj.status = 'PENDING'
        file_obj.save(update_fields=['status', 'updated_at'])

        import datetime as dt
        timeline_entry = {
            'timestamp': dt.datetime.now(dt.timezone.utc).isoformat(),
            'status': 'PENDING',
            'changed_by_id': user.id,
            'changed_by_name': user.get_full_name(),
            'notes': f"File submitted for review by {user.get_full_name()}",
        }
        file_obj.status_timeline = (file_obj.status_timeline or []) + [timeline_entry]
        file_obj.save(update_fields=['status_timeline'])

        from config.security import AuditLogger
        AuditLogger.log_action(
            user=user,
            action='SUBMIT',
            resource_type='File',
            resource_id=file_obj.id,
            description=f"File {file_obj.file_number} submitted for review",
        )

        return Response({'message': f"File {file_obj.file_number} submitted for review."})

    @action(detail=True, methods=['post'], url_path='approve')
    def approve_file(self, request, pk=None):
        """Approve a file. Only TG/PS or department head can approve."""
        file_obj = self.get_object()
        user = request.user

        if user.role not in ('SYSADMIN', 'TG_PS'):
            return Response(
                {'error': 'Only Admin/TG/PS can approve files.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if file_obj.status != 'PENDING':
            return Response(
                {'error': 'Only files in PENDING status can be approved.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        notes = request.data.get('notes', '')
        file_obj.status = 'ACTIVE'
        file_obj.save(update_fields=['status', 'updated_at'])

        import datetime as dt
        timeline_entry = {
            'timestamp': dt.datetime.now(dt.timezone.utc).isoformat(),
            'status': 'ACTIVE',
            'changed_by_id': user.id,
            'changed_by_name': user.get_full_name(),
            'notes': notes or f"File approved by {user.get_full_name()}",
        }
        file_obj.status_timeline = (file_obj.status_timeline or []) + [timeline_entry]
        file_obj.save(update_fields=['status_timeline'])

        from config.security import AuditLogger
        AuditLogger.log_action(
            user=user,
            action='APPROVE',
            resource_type='File',
            resource_id=file_obj.id,
            description=f"File {file_obj.file_number} approved by {user.get_full_name()}",
        )

        return Response({'message': f"File {file_obj.file_number} has been approved."})

    @action(detail=True, methods=['post'], url_path='reject')
    def reject_file(self, request, pk=None):
        """Reject a file. Only TG/PS can reject."""
        file_obj = self.get_object()
        user = request.user

        if user.role not in ('SYSADMIN', 'TG_PS'):
            return Response(
                {'error': 'Only Admin/TG/PS can reject files.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if file_obj.status != 'PENDING':
            return Response(
                {'error': 'Only files in PENDING status can be rejected.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        notes = request.data.get('notes', '')
        file_obj.status = 'DRAFT'
        file_obj.save(update_fields=['status', 'updated_at'])

        import datetime as dt
        timeline_entry = {
            'timestamp': dt.datetime.now(dt.timezone.utc).isoformat(),
            'status': 'DRAFT',
            'changed_by_id': user.id,
            'changed_by_name': user.get_full_name(),
            'notes': notes or f"File rejected by {user.get_full_name()}",
        }
        file_obj.status_timeline = (file_obj.status_timeline or []) + [timeline_entry]
        file_obj.save(update_fields=['status_timeline'])

        from config.security import AuditLogger
        AuditLogger.log_action(
            user=user,
            action='REJECT',
            resource_type='File',
            resource_id=file_obj.id,
            description=f"File {file_obj.file_number} rejected by {user.get_full_name()}",
        )

        return Response({'message': f"File {file_obj.file_number} has been rejected and returned to draft."})

    @action(detail=True, methods=['post'], url_path='escalate')
    def escalate_file(self, request, pk=None):
        """Escalate a file to higher authority."""
        file_obj = self.get_object()
        user = request.user

        to_holder_id = request.data.get('to_holder_id')
        if not to_holder_id:
            return Response({'error': 'to_holder_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            to_holder = User.objects.get(id=to_holder_id)
        except User.DoesNotExist:
            return Response({'error': 'Target user not found.'}, status=status.HTTP_404_NOT_FOUND)

        notes = request.data.get('notes', '')

        movement = FileMovement.objects.create(
            file=file_obj,
            from_holder=user,
            to_holder=to_holder,
            action='ESCALATED',
            remarks=notes,
        )

        import datetime as dt
        timeline_entry = {
            'timestamp': dt.datetime.now(dt.timezone.utc).isoformat(),
            'status': file_obj.status,
            'changed_by_id': user.id,
            'changed_by_name': user.get_full_name(),
            'notes': f"File escalated to {to_holder.get_full_name()} by {user.get_full_name()}",
        }
        file_obj.status_timeline = (file_obj.status_timeline or []) + [timeline_entry]
        file_obj.current_holder = to_holder
        file_obj.save(update_fields=['current_holder', 'status_timeline', 'updated_at'])

        from config.security import AuditLogger
        AuditLogger.log_action(
            user=user,
            action='ESCALATE',
            resource_type='File',
            resource_id=file_obj.id,
            description=f"File {file_obj.file_number} escalated to {to_holder.get_full_name()}",
        )

        return Response({
            'message': f"File {file_obj.file_number} escalated to {to_holder.get_full_name()}.",
            'movement': FileMovementSerializer(movement).data,
        })


class FileMovementViewSet(viewsets.ModelViewSet):
    queryset = FileMovement.objects.select_related('file', 'from_holder', 'to_holder').all()
    serializer_class = FileMovementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['file', 'from_holder', 'to_holder', 'is_returned']
    ordering_fields = ['movement_date']


class FileAttachmentViewSet(viewsets.ModelViewSet):
    queryset = FileAttachment.objects.select_related('file', 'uploaded_by').all()
    serializer_class = FileAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['file']


class FileCommentViewSet(viewsets.ModelViewSet):
    queryset = FileComment.objects.select_related('file', 'author').all()
    serializer_class = FileCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['file']
    ordering_fields = ['created_at']


# === NEW VIEWS FOR ENTERPRISE FEATURES ===


class WorkflowConfigViewSet(viewsets.ModelViewSet):
    """CRUD for workflow configuration."""
    queryset = WorkflowConfig.objects.all()
    serializer_class = WorkflowConfigSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['direction', 'is_active']
    search_fields = ['step_name']


class FileTemplateViewSet(viewsets.ModelViewSet):
    """CRUD for file templates."""
    queryset = FileTemplate.objects.select_related('created_by', 'default_department').all()
    serializer_class = FileTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['usage_count', 'created_at', 'name']

    @action(detail=True, methods=['post'], url_path='generate-file')
    def generate_file(self, request, pk=None):
        """Generate a new File from this template."""
        template = self.get_object()
        title = request.data.get('title')
        field_values = request.data.get('field_values', {})

        if not title:
            return Response({'error': 'title is required.'}, status=status.HTTP_400_BAD_REQUEST)

        from .services.template_service import TemplateService
        try:
            file_obj = TemplateService.generate_file_from_template(
                template=template,
                title=title,
                created_by=request.user,
                field_values=field_values,
            )
            return Response({
                'message': f"File {file_obj.file_number} created from template.",
                'file_id': file_obj.id,
                'file_number': file_obj.file_number,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='stats')
    def usage_stats(self, request):
        """Get template usage statistics."""
        from .services.template_service import TemplateService
        stats = TemplateService.get_template_usage_stats()
        return Response(stats)


class FileClassificationViewSet(viewsets.ModelViewSet):
    """CRUD for file classifications."""
    queryset = FileClassification.objects.select_related('file').all()
    serializer_class = FileClassificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['urgency', 'sensitivity', 'suggested_department']

    @action(detail=False, methods=['post'], url_path='classify')
    def classify_file(self, request):
        """Classify a single file."""
        file_id = request.data.get('file_id')
        if not file_id:
            return Response({'error': 'file_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            file_obj = File.objects.get(id=file_id)
        except File.DoesNotExist:
            return Response({'error': 'File not found.'}, status=status.HTTP_404_NOT_FOUND)

        from .services.classification_service import ClassificationService
        classification = ClassificationService.classify_file(file=file_obj)
        return Response(FileClassificationSerializer(classification).data)

    @action(detail=False, methods=['post'], url_path='bulk-classify')
    def bulk_classify(self, request):
        """Classify multiple files at once."""
        file_ids = request.data.get('file_ids', [])

        from .services.classification_service import ClassificationService
        results = ClassificationService.bulk_classify(file_ids=file_ids if file_ids else None)
        return Response({
            'classified': len(results),
            'results': FileClassificationSerializer(results, many=True).data,
        })

    @action(detail=True, methods=['get'], url_path='suggestions')
    def suggestions(self, request, pk=None):
        """Get classification suggestions for a file without saving."""
        classification = self.get_object()
        from .services.classification_service import ClassificationService
        suggestions = ClassificationService.get_classification_suggestions(classification.file)
        return Response(suggestions)


class OfflineQueueViewSet(viewsets.ModelViewSet):
    """CRUD for offline sync queue."""
    queryset = OfflineQueue.objects.select_related('user').all()
    serializer_class = OfflineQueueSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'action_type', 'user']

    @action(detail=False, methods=['post'], url_path='queue')
    def queue_action(self, request):
        """Add an action to the offline queue."""
        object_id = request.data.get('object_id')
        action_type = request.data.get('action_type')
        data = request.data.get('data', {})

        if not object_id or not action_type:
            return Response({'error': 'object_id and action_type are required.'},
                          status=status.HTTP_400_BAD_REQUEST)

        from .services.offline_sync_service import OfflineSyncService
        item = OfflineSyncService.queue_action(
            user=request.user,
            object_id=object_id,
            action_type=action_type,
            data=data,
        )
        return Response(OfflineQueueSerializer(item).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='process')
    def process_queue(self, request):
        """Process pending items in the queue."""
        from .services.offline_sync_service import OfflineSyncService
        result = OfflineSyncService.process_queue(user=request.user)
        return Response(result)

    @action(detail=False, methods=['get'], url_path='pending-count')
    def pending_count(self, request):
        """Get count of pending items."""
        from .services.offline_sync_service import OfflineSyncService
        count = OfflineSyncService.get_pending_count(user=request.user)
        return Response({'pending_count': count})

    @action(detail=False, methods=['post'], url_path='retry-failed')
    def retry_failed(self, request):
        """Retry failed items."""
        from .services.offline_sync_service import OfflineSyncService
        result = OfflineSyncService.retry_failed(user=request.user)
        return Response(result)


# === SEARCH AND IMPORT/EXPORT VIEWS ===


class FileSearchView(APIView):
    """Advanced file search endpoint."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from .services.search_service import SearchService

        params = {
            'query': request.query_params.get('q'),
            'file_type': request.query_params.get('file_type'),
            'status': request.query_params.get('status'),
            'classification': request.query_params.get('classification'),
            'priority': request.query_params.get('priority'),
            'department': request.query_params.get('department'),
            'school': request.query_params.get('school'),
            'created_by': request.query_params.get('created_by'),
            'current_holder': request.query_params.get('current_holder'),
            'date_from': request.query_params.get('date_from'),
            'date_to': request.query_params.get('date_to'),
            'sort_by': request.query_params.get('sort', '-created_at'),
            'limit': int(request.query_params.get('limit', 50)),
            'offset': int(request.query_params.get('offset', 0)),
        }

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        results = SearchService.search_files(**params)
        return Response(results)


class FileSearchSuggestionsView(APIView):
    """Search suggestions endpoint."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '')
        limit = int(request.query_params.get('limit', 10))

        from .services.search_service import SearchService
        suggestions = SearchService.get_search_suggestions(query, limit=limit)
        return Response(suggestions)


class FileImportView(APIView):
    """Import files from documents."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        uploaded_file = request.FILES.get('file')
        file_format = request.data.get('format')
        department = request.data.get('department')
        default_classification = request.data.get('classification', 'INTERNAL')
        default_priority = request.data.get('priority', 'NORMAL')

        if not uploaded_file:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        if not file_format:
            # Auto-detect from filename
            filename = uploaded_file.name.lower()
            ext_map = {'.doc': 'doc', '.docx': 'docx', '.xls': 'xls', '.xlsx': 'xlsx',
                       '.pdf': 'pdf', '.jpeg': 'jpeg', '.jpg': 'jpeg', '.png': 'png',
                       '.csv': 'csv', '.txt': 'txt'}
            import os
            ext = os.path.splitext(filename)[1]
            file_format = ext_map.get(ext, 'txt')

        from .services.import_export_service import ImportExportService
        from departments.models import Department

        dept = None
        if department:
            try:
                dept = Department.objects.get(id=department)
            except Department.DoesNotExist:
                pass

        result = ImportExportService.import_file(
            uploaded_file=uploaded_file,
            file_format=file_format,
            created_by=request.user,
            department=dept,
            default_classification=default_classification,
            default_priority=default_priority,
        )

        return Response({
            'file_id': result['file'].id if result.get('file') else None,
            'file_number': result['file'].file_number if result.get('file') else None,
            'attachments': len(result.get('attachments', [])),
            'errors': result.get('errors', []),
        })


class FileExportView(APIView):
    """Export files to various formats."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        file_ids = request.data.get('file_ids', [])
        export_format = request.data.get('format', 'xlsx')

        if not file_ids:
            return Response({'error': 'No file IDs provided.'}, status=status.HTTP_400_BAD_REQUEST)

        files = File.objects.filter(id__in=file_ids)
        if not files.exists():
            return Response({'error': 'No files found.'}, status=status.HTTP_404_NOT_FOUND)

        from .services.import_export_service import ImportExportService

        try:
            content = ImportExportService.export_files(
                file_ids=file_ids,
                export_format=export_format,
                exported_by=request.user,
            )

            content_type_map = {
                'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'csv': 'text/csv',
                'pdf': 'application/pdf',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            }

            response = HttpResponse(content.read(), content_type=content_type_map.get(export_format, 'application/octet-stream'))
            response['Content-Disposition'] = f'attachment; filename="{content.name}"'
            return response

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class FileBulkImportView(APIView):
    """Bulk import from CSV/XLSX."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        uploaded_file = request.FILES.get('file')
        file_format = request.data.get('format', 'csv')
        department = request.data.get('department')

        if not uploaded_file:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        from .services.import_export_service import ImportExportService
        from departments.models import Department

        dept = None
        if department:
            try:
                dept = Department.objects.get(id=department)
            except Department.DoesNotExist:
                pass

        result = ImportExportService.bulk_import(
            uploaded_file=uploaded_file,
            file_format=file_format,
            created_by=request.user,
            department=dept,
        )

        return Response(result)


class NotificationListView(APIView):
    """List user notifications."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        unread_only = request.query_params.get('unread_only', 'false').lower() == 'true'
        limit = int(request.query_params.get('limit', 50))

        from .services.notification_service import NotificationService
        notifications = NotificationService.get_user_notifications(
            user=request.user,
            unread_only=unread_only,
            limit=limit,
        )

        # Serialize notifications
        data = []
        for n in notifications:
            data.append({
                'id': n.id,
                'title': getattr(n, 'title', ''),
                'message': getattr(n, 'message', ''),
                'is_read': getattr(n, 'is_read', False),
                'created_at': getattr(n, 'created_at', None),
                'notification_type': getattr(n, 'notification_type', ''),
            })

        return Response(data)


class NotificationReadView(APIView):
    """Mark notification as read."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk=None):
        from .services.notification_service import NotificationService
        success = NotificationService.mark_notification_read(pk, request.user)
        if success:
            return Response({'message': 'Notification marked as read.'})
        return Response({'error': 'Notification not found.'}, status=status.HTTP_404_NOT_FOUND)
