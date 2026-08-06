from django.utils import timezone
from django.db.models import Avg, Max, Min, Count
from datetime import timedelta
from .models import IoTDevice, SensorReading, AlertRule, IoTAlert


class IoTService:
    @staticmethod
    def record_reading(device_id, value, metadata=None):
        try:
            device = IoTDevice.objects.get(device_id=device_id)
        except IoTDevice.DoesNotExist:
            return None

        reading = SensorReading.objects.create(
            device=device,
            value=value,
            unit=device.sensor_type.unit,
            metadata=metadata or {}
        )

        device.last_reading = value
        device.last_reading_at = timezone.now()
        device.save(update_fields=['last_reading', 'last_reading_at'])

        IoTService._check_alerts(device, value)
        return reading

    @staticmethod
    def _check_alerts(device, value):
        rules = AlertRule.objects.filter(device=device, is_active=True)
        for rule in rules:
            triggered = False
            if '>' in rule.condition and value > rule.threshold_value:
                triggered = True
            elif '<' in rule.condition and value < rule.threshold_value:
                triggered = True
            elif '==' in rule.condition and value == rule.threshold_value:
                triggered = True
            elif '!=' in rule.condition and value != rule.threshold_value:
                triggered = True

            if triggered:
                IoTAlert.objects.create(
                    rule=rule,
                    device=device,
                    severity=rule.severity,
                    message=f"{device.name}: {value}{device.sensor_type.unit} - {rule.name}",
                    value=value,
                )
                rule.last_triggered = timezone.now()
                rule.save(update_fields=['last_triggered'])

    @staticmethod
    def get_device_stats(device_id, hours=24):
        try:
            device = IoTDevice.objects.get(device_id=device_id)
        except IoTDevice.DoesNotExist:
            return None

        since = timezone.now() - timedelta(hours=hours)
        readings = SensorReading.objects.filter(device=device, recorded_at__gte=since)

        stats = readings.aggregate(
            avg=Avg('value'),
            max=Max('value'),
            min=Min('value'),
            count=Count('id'),
        )

        return {
            'device': device_id,
            'name': device.name,
            'location': device.location,
            'status': device.status,
            'last_reading': device.last_reading,
            'stats': stats,
        }

    @staticmethod
    def get_school_dashboard(school_id):
        devices = IoTDevice.objects.filter(school_id=school_id)
        active = devices.filter(status='ACTIVE').count()
        alerts = IoTAlert.objects.filter(
            device__school_id=school_id,
            is_acknowledged=False
        ).count()

        readings = []
        for device in devices.filter(status='ACTIVE'):
            latest = SensorReading.objects.filter(device=device).first()
            if latest:
                readings.append({
                    'device': device.device_id,
                    'name': device.name,
                    'type': device.sensor_type.name,
                    'value': latest.value,
                    'unit': latest.unit,
                    'location': device.location,
                    'timestamp': latest.recorded_at.isoformat(),
                })

        return {
            'total_devices': devices.count(),
            'active_devices': active,
            'inactive_devices': devices.count() - active,
            'pending_alerts': alerts,
            'latest_readings': readings,
        }

    @staticmethod
    def get_energy_dashboard(school_id):
        devices = IoTDevice.objects.filter(
            school_id=school_id,
            sensor_type__code='ENERGY'
        )
        total_consumption = SensorReading.objects.filter(
            device__in=devices
        ).aggregate(total=Avg('value'))['total'] or 0

        return {
            'total_devices': devices.count(),
            'total_consumption_kwh': round(total_consumption, 2),
            'devices': [{
                'id': d.device_id,
                'name': d.name,
                'last_reading': d.last_reading,
            } for d in devices],
        }
