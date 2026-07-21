from django.contrib import admin
from .models import Asset, AssetMaintenance, AssetTransfer


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['asset_code', 'name', 'school', 'category', 'condition', 'is_active']
    list_filter = ['school', 'category', 'condition', 'is_active']
    search_fields = ['asset_code', 'name']
    raw_id_fields = ['school', 'assigned_to']


@admin.register(AssetMaintenance)
class AssetMaintenanceAdmin(admin.ModelAdmin):
    list_display = ['asset', 'maintenance_date', 'cost', 'performed_by']
    search_fields = ['description', 'performed_by']
    raw_id_fields = ['asset']


@admin.register(AssetTransfer)
class AssetTransferAdmin(admin.ModelAdmin):
    list_display = ['asset', 'from_location', 'to_location', 'transfer_date']
    search_fields = ['reason']
    raw_id_fields = ['asset', 'approved_by', 'received_by']
