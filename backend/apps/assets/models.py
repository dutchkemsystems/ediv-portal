from django.db import models
from django.conf import settings
from apps.schools.models import School


class AssetCategory(models.TextChoices):
    FURNITURE = 'FURNITURE', 'Furniture'
    ELECTRONICS = 'ELECTRONICS', 'Electronics'
    VEHICLE = 'VEHICLE', 'Vehicle'
    EQUIPMENT = 'EQUIPMENT', 'Equipment'
    BUILDING = 'BUILDING', 'Building'
    OTHER = 'OTHER', 'Other'


class AssetCondition(models.TextChoices):
    NEW = 'NEW', 'New'
    GOOD = 'GOOD', 'Good'
    FAIR = 'FAIR', 'Fair'
    POOR = 'POOR', 'Poor'
    DAMAGED = 'DAMAGED', 'Damaged'
    RETIRED = 'RETIRED', 'Retired'


class Asset(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='assets')
    asset_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=AssetCategory.choices)
    description = models.TextField(blank=True)
    condition = models.CharField(max_length=20, choices=AssetCondition.choices, default='NEW')
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    current_value = models.DecimalField(max_digits=12, decimal_places=2)
    location = models.CharField(max_length=200)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_assets'
    )
    warranty_expiry = models.DateField(null=True, blank=True)
    last_maintenance = models.DateField(null=True, blank=True)
    next_maintenance = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['school', 'category', 'asset_code']
        indexes = [
            models.Index(fields=['school']),
            models.Index(fields=['asset_code']),
            models.Index(fields=['category']),
            models.Index(fields=['condition']),
        ]
    
    def __str__(self):
        return f"{self.asset_code} - {self.name}"


class AssetMaintenance(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_date = models.DateField()
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    performed_by = models.CharField(max_length=200)
    next_maintenance_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-maintenance_date']
    
    def __str__(self):
        return f"{self.asset.name} - {self.maintenance_date}"


class AssetTransfer(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='transfers')
    from_location = models.CharField(max_length=200)
    to_location = models.CharField(max_length=200)
    transfer_date = models.DateField()
    reason = models.TextField()
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='approved_asset_transfers'
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_asset_transfers'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-transfer_date']
    
    def __str__(self):
        return f"{self.asset.name} - {self.transfer_date}"
