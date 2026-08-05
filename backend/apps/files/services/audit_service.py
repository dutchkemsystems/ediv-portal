"""Audit trail service for file operations using the audit app's AuditLog."""
import logging
from apps.audit.models import AuditLog, AuditAction

logger = logging.getLogger(__name__)


class AuditService:
    """Service for creating and querying audit trail records for file operations."""

    @staticmethod
    def log_action(*, user, action, resource_type, resource_id='',
                   description, old_value=None, new_value=None,
                   ip_address=None, user_agent='') -> AuditLog:
        """
        Create an immutable audit log entry.

        Args:
            user: The user performing the action
            action: Action type (from AuditAction choices)
            resource_type: Type of resource (e.g., 'File', 'FileMovement')
            resource_id: ID of the resource
            description: Human-readable description of the action
            old_value: Previous state (dict)
            new_value: New state (dict)
            ip_address: Client IP address
            user_agent: Client user agent string

        Returns: AuditLog instance
        """
        # Map action to AuditAction if needed
        action_map = {
            'CREATE': AuditAction.CREATE,
            'UPDATE': AuditAction.UPDATE,
            'DELETE': AuditAction.DELETE,
            'MOVE': AuditAction.FILE_MOVEMENT,
            'ARCHIVE': AuditAction.UPDATE,
            'ESCALATE': AuditAction.UPDATE,
            'APPROVE': AuditAction.APPROVE,
            'REJECT': AuditAction.REJECT,
            'SUBMIT': AuditAction.UPDATE,
            'CLASSIFY': AuditAction.UPDATE,
            'IMPORT': AuditAction.IMPORT,
            'EXPORT': AuditAction.EXPORT,
            'LOGIN': AuditAction.LOGIN,
        }
        audit_action = action_map.get(action, AuditAction.UPDATE)

        log = AuditLog.objects.create(
            user=user,
            action=audit_action,
            module='files',
            object_type=resource_type,
            object_id=str(resource_id) if resource_id else '',
            description=description,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        logger.info(f"Audit: {user} - {action} - {resource_type}:{resource_id}")
        return log

    @staticmethod
    def get_resource_logs(resource_type, resource_id, limit=50) -> list:
        """Get audit logs for a specific resource."""
        return list(
            AuditLog.objects.filter(
                object_type=resource_type,
                object_id=str(resource_id),
                module='files',
            ).select_related('user').order_by('-created_at')[:limit]
        )

    @staticmethod
    def get_user_logs(user_id, action=None, limit=50) -> list:
        """Get audit logs for a specific user."""
        qs = AuditLog.objects.filter(user_id=user_id, module='files')
        if action:
            action_map = {
                'CREATE': AuditAction.CREATE,
                'UPDATE': AuditAction.UPDATE,
                'DELETE': AuditAction.DELETE,
                'MOVE': AuditAction.FILE_MOVEMENT,
                'APPROVE': AuditAction.APPROVE,
                'REJECT': AuditAction.REJECT,
                'IMPORT': AuditAction.IMPORT,
                'EXPORT': AuditAction.EXPORT,
            }
            audit_action = action_map.get(action)
            if audit_action:
                qs = qs.filter(action=audit_action)
        return list(qs.select_related('user').order_by('-created_at')[:limit])

    @staticmethod
    def get_recent_logs(limit=100, action=None) -> list:
        """Get recent audit logs across all file resources."""
        qs = AuditLog.objects.filter(module='files')
        if action:
            action_map = {
                'CREATE': AuditAction.CREATE,
                'UPDATE': AuditAction.UPDATE,
                'DELETE': AuditAction.DELETE,
                'MOVE': AuditAction.FILE_MOVEMENT,
            }
            audit_action = action_map.get(action)
            if audit_action:
                qs = qs.filter(action=audit_action)
        return list(qs.select_related('user').order_by('-created_at')[:limit])

    @staticmethod
    def get_resource_history(resource_type, resource_id) -> list:
        """Get full history of a resource."""
        return AuditService.get_resource_logs(resource_type, resource_id, limit=500)
