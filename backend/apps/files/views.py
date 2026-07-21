from rest_framework import viewsets, permissions, filters
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
        if user.role == 'SYSADMIN':
            return File.objects.all()
        return File.objects.filter(
            models.Q(created_by=user) |
            models.Q(current_holder=user) |
            models.Q(classification='PUBLIC')
        ).distinct()


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
