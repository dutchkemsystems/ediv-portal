import json
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger('apps')


class RealtimeBroadcaster:
    """Broadcast real-time updates via WebSocket channels."""

    @staticmethod
    def _get_channel_layer():
        try:
            return get_channel_layer()
        except Exception:
            logger.warning('Channel layer not available; skipping broadcast')
            return None

    @staticmethod
    def broadcast_to_user(user_id, event_type, data):
        layer = RealtimeBroadcaster._get_channel_layer()
        if not layer:
            return
        async_to_sync(layer.group_send)(
            f'notifications_{user_id}',
            {
                'type': 'send_notification',
                'data': {'event': event_type, **data},
            }
        )

    @staticmethod
    def broadcast_to_role(role, event_type, data):
        layer = RealtimeBroadcaster._get_channel_layer()
        if not layer:
            return
        async_to_sync(layer.group_send)(
            f'role_{role}',
            {
                'type': 'send_notification',
                'data': {'event': event_type, **data},
            }
        )

    @staticmethod
    def broadcast_file_movement(file_data):
        layer = RealtimeBroadcaster._get_channel_layer()
        if not layer:
            return
        async_to_sync(layer.group_send)(
            'dashboard_broadcast',
            {
                'type': 'file_movement',
                'data': file_data,
            }
        )

    @staticmethod
    def broadcast_dashboard_update(roles=None, data=None):
        layer = RealtimeBroadcaster._get_channel_layer()
        if not layer:
            return
        roles = roles or ['SYSADMIN', 'TG_PS']
        for role in roles:
            async_to_sync(layer.group_send)(
                f'dashboard_{role}',
                {
                    'type': 'stats_update',
                    'data': data or {},
                }
            )

    @staticmethod
    def broadcast_announcement(title, message, target_roles=None):
        layer = RealtimeBroadcaster._get_channel_layer()
        if not layer:
            return
        target_roles = target_roles or ['SYSADMIN', 'TG_PS']
        for role in target_roles:
            async_to_sync(layer.group_send)(
                f'role_{role}',
                {
                    'type': 'announcement',
                    'data': {'title': title, 'message': message},
                }
            )
