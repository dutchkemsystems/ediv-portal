from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import SensorType, IoTDevice, SensorReading, AlertRule, IoTAlert
from .serializers import (
    SensorTypeSerializer, IoTDeviceSerializer, SensorReadingSerializer,
    AlertRuleSerializer, IoTAlertSerializer, RecordReadingSerializer
)
from .services.iot_service import IoTService


class SensorTypeViewSet(viewsets.ModelViewSet):
    queryset = SensorType.objects.all()
    serializer_class = SensorTypeSerializer
    permission_classes = [permissions.IsAdminUser]


class IoTDeviceViewSet(viewsets.ModelViewSet):
    queryset = IoTDevice.objects.all()
    serializer_class = IoTDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['school', 'status', 'sensor_type']

    @action(detail=True, methods=['get'], url_path='stats')
    def device_stats(self, request, pk=None):
        device = self.get_object()
        hours = int(request.query_params.get('hours', 24))
        stats = IoTService.get_device_stats(device.device_id, hours)
        return Response(stats)

    @action(detail=False, methods=['get'], url_path='by-school')
    def by_school(self, request):
        school_id = request.query_params.get('school_id')
        if not school_id:
            return Response({'error': 'school_id required'}, status=status.HTTP_400_BAD_REQUEST)
        devices = IoTDevice.objects.filter(school_id=school_id)
        return Response(IoTDeviceSerializer(devices, many=True).data)


class SensorReadingViewSet(viewsets.ModelViewSet):
    queryset = SensorReading.objects.all()
    serializer_class = SensorReadingSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post']

    @action(detail=False, methods=['post'], url_path='record')
    def record_reading(self, request):
        serializer = RecordReadingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reading = IoTService.record_reading(
            serializer.validated_data['device_id'],
            serializer.validated_data['value'],
            serializer.validated_data.get('metadata', {})
        )
        if reading:
            return Response(SensorReadingSerializer(reading).data)
        return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)


class AlertRuleViewSet(viewsets.ModelViewSet):
    queryset = AlertRule.objects.all()
    serializer_class = AlertRuleSerializer
    permission_classes = [permissions.IsAdminUser]


class IoTAlertViewSet(viewsets.ModelViewSet):
    queryset = IoTAlert.objects.all()
    serializer_class = IoTAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['severity', 'is_acknowledged']

    @action(detail=True, methods=['post'], url_path='acknowledge')
    def acknowledge_alert(self, request, pk=None):
        alert = self.get_object()
        alert.is_acknowledged = True
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        return Response({'message': 'Alert acknowledged.'})

    @action(detail=False, methods=['get'], url_path='dashboard')
    def iot_dashboard(self, request):
        school_id = request.query_params.get('school_id')
        if not school_id:
            return Response({'error': 'school_id required'}, status=status.HTTP_400_BAD_REQUEST)
        dashboard = IoTService.get_school_dashboard(school_id)
        return Response(dashboard)

    @action(detail=False, methods=['get'], url_path='energy')
    def energy_dashboard(self, request):
        school_id = request.query_params.get('school_id')
        if not school_id:
            return Response({'error': 'school_id required'}, status=status.HTTP_400_BAD_REQUEST)
        energy = IoTService.get_energy_dashboard(school_id)
        return Response(energy)
