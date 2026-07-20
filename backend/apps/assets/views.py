from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Asset, AssetMaintenance, AssetTransfer
from .serializers import (
    AssetSerializer, AssetListSerializer,
    AssetMaintenanceSerializer, AssetTransferSerializer
)


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.select_related('school', 'assigned_to').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['school', 'category', 'condition', 'is_active']
    search_fields = ['asset_code', 'name', 'description']
    ordering_fields = ['asset_code', 'purchase_date', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AssetListSerializer
        return AssetSerializer


class AssetMaintenanceViewSet(viewsets.ModelViewSet):
    queryset = AssetMaintenance.objects.select_related('asset').all()
    serializer_class = AssetMaintenanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['asset']
    ordering_fields = ['maintenance_date', 'created_at']


class AssetTransferViewSet(viewsets.ModelViewSet):
    queryset = AssetTransfer.objects.select_related('asset', 'approved_by', 'received_by').all()
    serializer_class = AssetTransferSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['asset']
    ordering_fields = ['transfer_date', 'created_at']
