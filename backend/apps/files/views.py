from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from .models import File, FileMovement, FileAttachment, FileComment
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
        if user.role in ('SYSADMIN', 'TG', 'PS'):
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

        file_obj.current_holder = to_holder
        file_obj.status = 'IN_TRANSIT'
        file_obj.save(update_fields=['current_holder', 'status', 'updated_at'])

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
            last_movement.actual_return_date = __import__('datetime').date.today()
            last_movement.is_returned = True
            last_movement.save(update_fields=['actual_return_date', 'is_returned'])

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

        if user.role not in ('SYSADMIN', 'TG', 'PS') and file_obj.created_by != user:
            return Response(
                {'error': 'Only the file creator or Admin/TG/PS can close a file.'},
                status=status.HTTP_403_FORBIDDEN
            )

        file_obj.status = 'ARCHIVED'
        file_obj.save(update_fields=['status', 'updated_at'])

        from config.security import AuditLogger
        AuditLogger.log_action(
            user=user,
            action='UPDATE',
            resource_type='File',
            resource_id=file_obj.id,
            description=f"File {file_obj.file_number} closed/archived by {user.get_full_name()}",
        )

        return Response({'message': f"File {file_obj.file_number} has been archived."})


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
