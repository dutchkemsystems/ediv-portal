from django.db import models
from django.conf import settings
from apps.schools.models import School


class VehicleType(models.TextChoices):
    BUS = 'BUS', 'Bus'
    VAN = 'VAN', 'Van'
    MINIBUS = 'MINIBUS', 'Minibus'
    OTHER = 'OTHER', 'Other'


class Vehicle(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='vehicles')
    registration_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=VehicleType.choices)
    capacity = models.IntegerField()
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_vehicles'
    )
    insurance_expiry = models.DateField()
    last_maintenance = models.DateField(null=True, blank=True)
    next_maintenance = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    gps_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['registration_number']
    
    def __str__(self):
        return f"{self.registration_number} ({self.vehicle_type})"


class BusRoute(models.Model):
    name = models.CharField(max_length=200)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='bus_routes')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='routes')
    stops = models.JSONField(default=list)
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    fare = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class StudentTransport(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='transport_assignments')
    route = models.ForeignKey(BusRoute, on_delete=models.CASCADE, related_name='student_assignments')
    academic_year = models.CharField(max_length=9)
    is_active = models.BooleanField(default=True)
    pickup_stop = models.CharField(max_length=200)
    dropoff_stop = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'route', 'academic_year']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.route.name}"
