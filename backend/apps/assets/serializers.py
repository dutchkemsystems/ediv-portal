from rest_framework import serializers
from .models import Asset, AssetMaintenance, AssetTransfer


class AssetMaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetMaintenance
        fields = ['id', 'asset', 'maintenance_date', 'description', 'cost', 'performed_by',
                  'next_maintenance_date', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class AssetTransferSerializer(serializers.ModelSerializer):
    asset_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    received_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AssetTransfer
        fields = ['id', 'asset', 'asset_name', 'from_location', 'to_location', 'transfer_date',
                  'reason', 'approved_by', 'approved_by_name', 'received_by', 'received_by_name',
                  'notes', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_asset_name(self, obj):
        return obj.asset.name
    
    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return obj.approved_by.get_full_name()
        return None
    
    def get_received_by_name(self, obj):
        if obj.received_by:
            return obj.received_by.get_full_name()
        return None


class AssetSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    maintenance_records = AssetMaintenanceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Asset
        fields = ['id', 'school', 'school_name', 'asset_code', 'name', 'category',
                  'description', 'condition', 'purchase_date', 'purchase_price',
                  'current_value', 'location', 'assigned_to', 'assigned_to_name',
                  'warranty_expiry', 'last_maintenance', 'next_maintenance',
                  'is_active', 'maintenance_records', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_school_name(self, obj):
        return obj.school.name
    
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name()
        return None


class AssetListSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Asset
        fields = ['id', 'school_name', 'asset_code', 'name', 'category', 'condition', 'is_active']
    
    def get_school_name(self, obj):
        return obj.school.name

