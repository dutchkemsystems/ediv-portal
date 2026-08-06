from rest_framework import serializers
from .models import SensorType, IoTDevice, SensorReading, AlertRule, IoTAlert


class SensorTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorType
        fields = ['id', 'name', 'code', 'unit', 'min_threshold', 'max_threshold', 'description']


class IoTDeviceSerializer(serializers.ModelSerializer):
    school_name = serializers.SerializerMethodField()
    sensor_type_name = serializers.SerializerMethodField()

    class Meta:
        model = IoTDevice
        fields = ['id', 'school', 'school_name', 'sensor_type', 'sensor_type_name',
                  'device_id', 'name', 'location', 'latitude', 'longitude',
                  'status', 'last_reading', 'last_reading_at', 'install_date',
                  'firmware_version', 'metadata']
        read_only_fields = ['id', 'last_reading', 'last_reading_at']

    def get_school_name(self, obj):
        return obj.school.name

    def get_sensor_type_name(self, obj):
        return obj.sensor_type.name


class SensorReadingSerializer(serializers.ModelSerializer):
    device_name = serializers.SerializerMethodField()

    class Meta:
        model = SensorReading
        fields = ['id', 'device', 'device_name', 'value', 'unit', 'is_anomaly',
                  'metadata', 'recorded_at']
        read_only_fields = ['id', 'recorded_at']

    def get_device_name(self, obj):
        return obj.device.name


class AlertRuleSerializer(serializers.ModelSerializer):
    device_name = serializers.SerializerMethodField()

    class Meta:
        model = AlertRule
        fields = ['id', 'device', 'device_name', 'name', 'condition',
                  'threshold_value', 'severity', 'is_active', 'last_triggered']
        read_only_fields = ['id', 'last_triggered']

    def get_device_name(self, obj):
        return obj.device.name


class IoTAlertSerializer(serializers.ModelSerializer):
    device_name = serializers.SerializerMethodField()
    acknowledged_by_name = serializers.SerializerMethodField()

    class Meta:
        model = IoTAlert
        fields = ['id', 'rule', 'device', 'device_name', 'severity', 'message',
                  'value', 'is_acknowledged', 'acknowledged_by', 'acknowledged_by_name',
                  'acknowledged_at', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_device_name(self, obj):
        return obj.device.name

    def get_acknowledged_by_name(self, obj):
        return obj.acknowledged_by.get_full_name() if obj.acknowledged_by else None


class RecordReadingSerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=100)
    value = serializers.FloatField()
    metadata = serializers.DictField(required=False, default=dict)
