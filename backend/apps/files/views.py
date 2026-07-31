from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from .models import File, FileMovement, FileAttachment, FileComment, FileStatus, FileCategory, SecurityClassification
from .serializers import (
    FileSerializer, FileListSerializer,
    FileMovementSerializer, FileAttachmentSerializer, FileCommentSerializer
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
