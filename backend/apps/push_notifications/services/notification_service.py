import json
import logging
from django.utils import timezone
from .models import DeviceToken, PushNotification, NotificationLog

logger = logging.getLogger(__name__)


class PushNotificationService:
    @staticmethod
    def register_device(user, token, platform, device_name=''):
        device, created = DeviceToken.objects.update_or_create(
            user=user, token=token,
            defaults={
                'platform': platform,
                'device_name': device_name,
                'is_active': True,
            }
        )
        return device

    @staticmethod
    def unregister_device(token):
        DeviceToken.objects.filter(token=token).update(is_active=False)

    @staticmethod
    def send_notification(notification_id):
        try:
            notification = PushNotification.objects.get(id=notification_id)
        except PushNotification.DoesNotExist:
            return

        devices = DeviceToken.objects.filter(is_active=True)

        if notification.target_users.exists():
            devices = devices.filter(user__in=notification.target_users.all())
        elif notification.target_roles:
            devices = devices.filter(user__role__in=notification.target_roles)
        if notification.target_schools.exists():
            devices = devices.filter(user__school__in=notification.target_schools.all())

        sent_count = 0
        for device in devices:
            try:
                success = PushNotificationService._send_to_device(device, notification)
                if success:
                    sent_count += 1
                    NotificationLog.objects.create(
                        notification=notification,
                        device_token=device,
                        status='SENT'
                    )
                else:
                    NotificationLog.objects.create(
                        notification=notification,
                        device_token=device,
                        status='FAILED',
                        error_message='Send failed'
                    )
            except Exception as e:
                logger.error(f"Failed to send to {device.token}: {e}")
                NotificationLog.objects.create(
                    notification=notification,
                    device_token=device,
                    status='FAILED',
                    error_message=str(e)
                )

        notification.sent_at = timezone.now()
        notification.sent_count = sent_count
        notification.save()

        return {'sent_count': sent_count, 'total_devices': devices.count()}

    @staticmethod
    def _send_to_device(device, notification):
        payload = {
            'title': notification.title,
            'body': notification.message,
            'category': notification.category,
            'data': notification.data,
            'image': notification.image_url,
            'action_url': notification.action_url,
        }

        if device.platform == 'WEB':
            return PushNotificationService._send_web_push(device, payload)
        elif device.platform == 'ANDROID':
            return PushNotificationService._send_fcm(device, payload)
        elif device.platform == 'IOS':
            return PushNotificationService._send_apns(device, payload)
        return False

    @staticmethod
    def _send_web_push(device, payload):
        logger.info(f"Web push to {device.token[:20]}...: {payload['title']}")
        return True

    @staticmethod
    def _send_fcm(device, payload):
        logger.info(f"FCM push to {device.token[:20]}...: {payload['title']}")
        return True

    @staticmethod
    def _send_apns(device, payload):
        logger.info(f"APNs push to {device.token[:20]}...: {payload['title']}")
        return True

    @staticmethod
    def send_to_user(user, title, message, category='GENERAL', data=None):
        notification = PushNotification.objects.create(
            title=title,
            message=message,
            category=category,
            data=data or {},
            target_users=[user],
        )
        return PushNotificationService.send_notification(notification.id)

    @staticmethod
    def send_broadcast(title, message, category='ANNOUNCEMENT', roles=None, schools=None):
        notification = PushNotification.objects.create(
            title=title,
            message=message,
            category=category,
            target_roles=roles or [],
        )
        if schools:
            notification.target_schools.set(schools)
        return PushNotificationService.send_notification(notification.id)

    @staticmethod
    def mark_opened(notification_id, device_token):
        from django.db.models import F
        PushNotification.objects.filter(id=notification_id).update(
            opened_count=F('opened_count') + 1
        )
        NotificationLog.objects.filter(
            notification_id=notification_id,
            device_token__token=device_token
        ).update(status='OPENED')

    @staticmethod
    def get_user_notifications(user, limit=20):
        from django.db import models as db_models
        return PushNotification.objects.filter(
            db_models.Q(target_users=user) |
            db_models.Q(target_roles__contains=user.role) |
            db_models.Q(target_schools=user.school)
        ).distinct()[:limit]
