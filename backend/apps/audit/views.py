from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import AuditLog, ComplianceItem, ComplianceRecord, Violation
from .serializers import (
    AuditLogSerializer, AuditLogListSerializer,
    ComplianceItemSerializer, ComplianceRecordSerializer,
    ComplianceRecordListSerializer, ViolationSerializer, ViolationListSerializer
)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role in ['SYSADMIN', 'TG', 'AUDIT']


class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = AuditLog.objects.select_related('user').all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ['user', 'action', 'module']
    search_fields = ['description', 'object_repr', 'module']
    ordering_fields = ['created_at', 'action', 'module']

    def get_serializer_class(self):
        if self.action == 'list':
            return AuditLogListSerializer
        return AuditLogSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ['SYSADMIN', 'TG', 'AUDIT']:
            return AuditLog.objects.select_related('user').all()
        return AuditLog.objects.select_related('user').filter(user=user)


class ComplianceItemViewSet(viewsets.ModelViewSet):
    queryset = ComplianceItem.objects.all()
    serializer_class = ComplianceItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ['category', 'is_mandatory', 'is_active']
    search_fields = ['title', 'description', 'reference_document']
    ordering_fields = ['category', 'title', 'created_at']


class ComplianceRecordViewSet(viewsets.ModelViewSet):
    queryset = ComplianceRecord.objects.select_related('item', 'school', 'department', 'reviewed_by').all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ['status', 'school', 'department', 'academic_year', 'item']
    search_fields = ['item__title', 'school__name', 'evidence']
    ordering_fields = ['due_date', 'status', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ComplianceRecordListSerializer
        return ComplianceRecordSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ViolationViewSet(viewsets.ModelViewSet):
    queryset = Violation.objects.select_related('school', 'department', 'reported_by', 'assigned_to').all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ['severity', 'status', 'category', 'school', 'department']
    search_fields = ['title', 'description', 'resolution_notes']
    ordering_fields = ['severity', 'incident_date', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ViolationListSerializer
        return ViolationSerializer

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)
