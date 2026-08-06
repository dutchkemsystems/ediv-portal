from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import DeviceToken, PushNotification, NotificationLog
from .serializers import (
    DeviceTokenSerializer, PushNotificationSerializer,
    NotificationLogSerializer, SendNotificationSerializer
)
from .services.notification_service import PushNotificationService


class DeviceTokenViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DeviceToken.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='register')
    def register_device(self, request):
        token = request.data.get('token')
        platform = request.data.get('platform', 'WEB')
        device_name = request.data.get('device_name', '')
        device = PushNotificationService.register_device(
            request.user, token, platform, device_name
        )
        return Response({'message': 'Device registered', 'device_id': device.id})

    @action(detail=False, methods=['post'], url_path='unregister')
    def unregister_device(self, request):
        token = request.data.get('token')
        PushNotificationService.unregister_device(token)
        return Response({'message': 'Device unregistered'})


class PushNotificationViewSet(viewsets.ModelViewSet):
    serializer_class = PushNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return PushNotification.objects.all()
        return PushNotificationService.get_user_notifications(self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['post'], url_path='send')
    def send_notification(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Admin only'}, status=status.HTTP_403_FORBIDDEN)

        serializer = SendNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from django.contrib.auth import get_user_model
        User = get_user_model()

        notification = PushNotification.objects.create(
            title=serializer.validated_data['title'],
            message=serializer.validated_data['message'],
            category=serializer.validated_data['category'],
            data=serializer.validated_data.get('data', {}),
            created_by=request.user,
        )

        user_ids = serializer.validated_data.get('user_ids', [])
        if user_ids:
            notification.target_users.set(User.objects.filter(id__in=user_ids))

        roles = serializer.validated_data.get('roles', [])
        notification.target_roles = roles

        school_ids = serializer.validated_data.get('school_ids', [])
        if school_ids:
            from apps.schools.models import School
            notification.target_schools.set(School.objects.filter(id__in=school_ids))

        notification.save()
        result = PushNotificationService.send_notification(notification.id)

        return Response({
            'message': f"Notification sent to {result['sent_count']} devices",
            'notification_id': notification.id,
        })

    @action(detail=True, methods=['post'], url_path='mark-opened')
    def mark_opened(self, request, pk=None):
        notification = self.get_object()
        device_token = request.data.get('device_token', '')
        PushNotificationService.mark_opened(notification.id, device_token)
        return Response({'message': 'Marked as opened'})

    @action(detail=False, methods=['get'], url_path='my-notifications')
    def my_notifications(self, request):
        notifications = PushNotificationService.get_user_notifications(request.user, limit=20)
        return Response(PushNotificationSerializer(notifications, many=True).data)

    @action(detail=False, methods=['get'], url_path='stats')
    def notification_stats(self, request):
        total = PushNotification.objects.count()
        sent = PushNotification.objects.filter(sent_at__isnull=False).count()
        return Response({
            'total_notifications': total,
            'sent_notifications': sent,
            'total_devices': DeviceToken.objects.filter(is_active=True).count(),
        })


class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationLogSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return NotificationLog.objects.all()
