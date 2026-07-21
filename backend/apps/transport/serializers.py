from rest_framework import serializers
from .models import Vehicle, BusRoute, StudentTransport


class VehicleSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    driver_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehicle
        fields = ['id', 'school', 'school_name', 'registration_number', 'vehicle_type',
                  'capacity', 'driver', 'driver_name', 'insurance_expiry', 'last_maintenance',
                  'next_maintenance', 'is_active', 'gps_enabled', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_school_name(self, obj):
        return obj.school.name
    
    def get_driver_name(self, obj):
        if obj.driver:
            return obj.driver.get_full_name()
        return None


class BusRouteSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    vehicle_registration = serializers.SerializerMethodField()
    
    class Meta:
        model = BusRoute
        fields = ['id', 'name', 'school', 'school_name', 'vehicle', 'vehicle_registration',
                  'stops', 'departure_time', 'arrival_time', 'is_active', 'fare',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_school_name(self, obj):
        return obj.school.name
    
    def get_vehicle_registration(self, obj):
        return obj.vehicle.registration_number


class StudentTransportSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    route_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentTransport
        fields = ['id', 'student', 'student_name', 'route', 'route_name', 'academic_year',
                  'is_active', 'pickup_stop', 'dropoff_stop', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name()
    
    def get_route_name(self, obj):
        return obj.route.name

