import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


class NotificationConsumer(AsyncWebsocketConsumer):
    """Real-time notification stream for authenticated users."""

    async def connect(self):
        self.user = self.scope.get('user', AnonymousUser())
        if self.user.is_anonymous:
            await self.close()
            return

        self.user_group = f'notifications_{self.user.id}'
        self.role_group = f'role_{self.user.role}'
        self.global_group = 'notifications_global'

        await self.channel_layer.group_add(self.user_group, self.channel_name)
        await self.channel_layer.group_add(self.role_group, self.channel_name)
        await self.channel_layer.group_add(self.global_group, self.channel_name)

        await self.channel_layer.group_add('dashboard_broadcast', self.channel_name)
        await self.accept()

        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'connected',
            'unread_count': unread_count,
            'user_id': self.user.id,
            'role': self.user.role,
        }))

    async def disconnect(self, close_code):
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(self.user_group, self.channel_name)
            await self.channel_layer.group_discard(self.role_group, self.channel_name)
            await self.channel_layer.group_discard(self.global_group, self.channel_name)
            await self.channel_layer.group_discard('dashboard_broadcast', self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type', '')

        if msg_type == 'mark_read':
            notification_id = data.get('notification_id')
            if notification_id:
                await self.mark_notification_read(notification_id)
                unread_count = await self.get_unread_count()
                await self.send(text_data=json.dumps({
                    'type': 'unread_update',
                    'unread_count': unread_count,
                }))

        elif msg_type == 'mark_all_read':
            await self.mark_all_read()
            await self.send(text_data=json.dumps({
                'type': 'unread_update',
                'unread_count': 0,
            }))

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'data': event['data'],
        }))

    async def dashboard_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'dashboard_update',
            'data': event['data'],
        }))

    async def file_movement(self, event):
        await self.send(text_data=json.dumps({
            'type': 'file_movement',
            'data': event['data'],
        }))

    async def attendance_alert(self, event):
        await self.send(text_data=json.dumps({
            'type': 'attendance_alert',
            'data': event['data'],
        }))

    async def announcement(self, event):
        await self.send(text_data=json.dumps({
            'type': 'announcement',
            'data': event['data'],
        }))

    @database_sync_to_async
    def get_unread_count(self):
        from apps.notifications.models import UserNotification
        return UserNotification.objects.filter(
            user=self.user, is_read=False
        ).count()

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        from apps.notifications.models import UserNotification
        UserNotification.objects.filter(
            id=notification_id, user=self.user
        ).update(is_read=True)

    @database_sync_to_async
    def mark_all_read(self):
        from apps.notifications.models import UserNotification
        UserNotification.objects.filter(
            user=self.user, is_read=False
        ).update(is_read=True)


class DashboardConsumer(AsyncWebsocketConsumer):
    """Live dashboard stats streaming for authorized users."""

    async def connect(self):
        self.user = self.scope.get('user', AnonymousUser())
        if self.user.is_anonymous:
            await self.close()
            return

        self.dashboard_group = f'dashboard_{self.user.role}'
        await self.channel_layer.group_add(self.dashboard_group, self.channel_name)
        await self.channel_layer.group_add('dashboard_broadcast', self.channel_name)
        await self.accept()

        stats = await self.get_dashboard_stats()
        await self.send(text_data=json.dumps({
            'type': 'initial_stats',
            'data': stats,
        }))

    async def disconnect(self, close_code):
        if hasattr(self, 'dashboard_group'):
            await self.channel_layer.group_discard(self.dashboard_group, self.channel_name)
            await self.channel_layer.group_discard('dashboard_broadcast', self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'request_refresh':
            stats = await self.get_dashboard_stats()
            await self.send(text_data=json.dumps({
                'type': 'stats_update',
                'data': stats,
            }))

    async def stats_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'stats_update',
            'data': event['data'],
        }))

    async def file_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'file_update',
            'data': event['data'],
        }))

    @database_sync_to_async
    def get_dashboard_stats(self):
        from django.db.models import Count, Q
        from apps.files.models import File, FileMovement
        from apps.users.models import User

        stats = {}
        if self.user.role in ('SYSADMIN', 'TG_PS'):
            stats['total_users'] = User.objects.filter(is_active=True).count()
            stats['total_files'] = File.objects.count()
            stats['active_files'] = File.objects.filter(status='ACTIVE').count()
            stats['pending_files'] = File.objects.filter(status='PENDING').count()
            stats['overdue_files'] = File.objects.filter(
                expected_completion_date__lt=__import__('datetime').date.today(),
                status__in=['ACTIVE', 'PENDING', 'IN_TRANSIT']
            ).count()
            stats['today_movements'] = FileMovement.objects.filter(
                movement_date__date=__import__('datetime').date.today()
            ).count()
        elif self.user.role in ('HR', 'FIN', 'AUDIT', 'QA', 'CC', 'EMIS', 'PLAN',
                                'PROC', 'PA', 'SA', 'FRENCH', 'REG'):
            stats['held_files'] = File.objects.filter(
                current_holder=self.user
            ).count()
            stats['my_movements'] = FileMovement.objects.filter(
                Q(from_holder=self.user) | Q(to_holder=self.user)
            ).count()

        return stats
