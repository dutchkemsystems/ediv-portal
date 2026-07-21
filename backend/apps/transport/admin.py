from django.contrib import admin
from .models import Vehicle, BusRoute, StudentTransport


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['registration_number', 'vehicle_type', 'school', 'capacity', 'driver', 'is_active']
    list_filter = ['vehicle_type', 'is_active']
    search_fields = ['registration_number']
    raw_id_fields = ['school', 'driver']


@admin.register(BusRoute)
class BusRouteAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'vehicle', 'departure_time', 'arrival_time', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    raw_id_fields = ['school', 'vehicle']


@admin.register(StudentTransport)
class StudentTransportAdmin(admin.ModelAdmin):
    list_display = ['student', 'route', 'academic_year', 'pickup_stop', 'dropoff_stop', 'is_active']
    list_filter = ['academic_year', 'is_active']
    raw_id_fields = ['student', 'route']
