from django.db import models
from django.conf import settings


class SensorType(models.Model):
    UNIT_CHOICES = [
        ('°C', 'Celsius'),
        ('%', 'Percentage'),
        ('kWh', 'Kilowatt Hour'),
        ('L', 'Liters'),
        ('ppm', 'Parts Per Million'),
        ('dB', 'Decibels'),
        ('lux', 'Lux'),
        ('m³', 'Cubic Meters'),
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)
    min_threshold = models.FloatField(default=0)
    max_threshold = models.FloatField(default=100)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'sensor_types'

    def __str__(self):
        return f"{self.name} ({self.unit})"


class IoTDevice(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('MAINTENANCE', 'Under Maintenance'),
        ('ERROR', 'Error'),
    ]

    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='iot_devices')
    sensor_type = models.ForeignKey(SensorType, on_delete=models.CASCADE, related_name='devices')
    device_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ACTIVE')
    last_reading = models.FloatField(null=True, blank=True)
    last_reading_at = models.DateTimeField(null=True, blank=True)
    install_date = models.DateField(null=True, blank=True)
    firmware_version = models.CharField(max_length=50, blank=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = 'iot_devices'
        unique_together = ['school', 'device_id']

    def __str__(self):
        return f"{self.name} - {self.school.name}"


class SensorReading(models.Model):
    device = models.ForeignKey(IoTDevice, on_delete=models.CASCADE, related_name='readings')
    value = models.FloatField()
    unit = models.CharField(max_length=10)
    is_anomaly = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sensor_readings'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['device', '-recorded_at']),
        ]

    def __str__(self):
        return f"{self.device.name}: {self.value} {self.unit}"


class AlertRule(models.Model):
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    device = models.ForeignKey(IoTDevice, on_delete=models.CASCADE, related_name='alert_rules')
    name = models.CharField(max_length=200)
    condition = models.CharField(max_length=50, help_text='e.g., > 35, < 10, == 0')
    threshold_value = models.FloatField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='MEDIUM')
    is_active = models.BooleanField(default=True)
    notify_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    last_triggered = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'alert_rules'

    def __str__(self):
        return f"{self.name}: {self.condition} {self.threshold_value}"


class IoTAlert(models.Model):
    rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE, related_name='alerts')
    device = models.ForeignKey(IoTDevice, on_delete=models.CASCADE, related_name='alerts')
    severity = models.CharField(max_length=10, choices=AlertRule.SEVERITY_CHOICES)
    message = models.TextField()
    value = models.FloatField()
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                       null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'iot_alerts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.device.name}: {self.message}"
