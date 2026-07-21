from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Vehicle, BusRoute, StudentTransport
from .serializers import VehicleSerializer, BusRouteSerializer, StudentTransportSerializer


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.select_related('school', 'driver').all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['school', 'vehicle_type', 'is_active']
    search_fields = ['registration_number']
    ordering_fields = ['registration_number', 'created_at']


class BusRouteViewSet(viewsets.ModelViewSet):
    queryset = BusRoute.objects.select_related('school', 'vehicle').all()
    serializer_class = BusRouteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['school', 'vehicle', 'is_active']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']


class StudentTransportViewSet(viewsets.ModelViewSet):
    queryset = StudentTransport.objects.select_related('student__user', 'route').all()
    serializer_class = StudentTransportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'route', 'academic_year', 'is_active']
    search_fields = ['student__user__first_name', 'student__user__last_name']
