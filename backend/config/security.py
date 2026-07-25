"""
Security utilities for Education District IV Portal.
Enterprise-grade security implementation.
"""

import hashlib
import os
import secrets
import string
from datetime import datetime, timedelta
from functools import wraps
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response


# ---------------------------------------------------------------------------
# Password Policy
# ---------------------------------------------------------------------------

class PasswordValidator:
    """Custom password validator with complexity requirements."""

    MIN_LENGTH = 12

    @staticmethod
    def validate(password):
        """Validate password meets security requirements. Returns list of errors."""
        errors = []

        if len(password) < PasswordValidator.MIN_LENGTH:
            errors.append(f'Password must be at least {PasswordValidator.MIN_LENGTH} characters long')

        if not any(c.isupper() for c in password):
            errors.append('Password must contain at least one uppercase letter')

        if not any(c.islower() for c in password):
            errors.append('Password must contain at least one lowercase letter')

        if not any(c.isdigit() for c in password):
            errors.append('Password must contain at least one digit')

        if not any(c in string.punctuation for c in password):
            errors.append('Password must contain at least one special character')

        # Reject common passwords
        common_passwords = [
            'password', '1234567890', 'qwertyuiop', 'asdfghjkl',
            'educationdistrict', 'admin123', 'welcome123',
        ]
        if password.lower() in common_passwords:
            errors.append('Password is too common')

        return errors

    @staticmethod
    def generate_password(length=16):
        """Generate a secure random password."""
        alphabet = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(alphabet) for _ in range(length))


# ---------------------------------------------------------------------------
# Account Lockout (cache-backed, 5 attempts / 30 min)
# ---------------------------------------------------------------------------

class AccountLockout:
    """Account lockout management — uses Django cache for speed."""

    MAX_ATTEMPTS = 5
    LOCKOUT_DURATION = 1800  # 30 minutes in seconds

    @staticmethod
    def _cache_key(user_id):
        return f"ediv:lockout:{user_id}"

    @classmethod
    def check_lockout(cls, user):
        """Return (is_locked: bool, remaining_seconds: float)."""
        lockout_data = cache.get(cls._cache_key(user.id))

        if lockout_data and lockout_data['attempts'] >= cls.MAX_ATTEMPTS:
            unlock_ts = lockout_data['until']
            now_ts = timezone.now().timestamp()
            if now_ts < unlock_ts:
                return True, unlock_ts - now_ts
            else:
                cache.delete(cls._cache_key(user.id))

        return False, 0

    @classmethod
    def record_failed_attempt(cls, user):
        """Increment failed attempts; lock if threshold reached."""
        lockout_data = cache.get(cls._cache_key(user.id), {'attempts': 0, 'until': 0})
        lockout_data['attempts'] += 1

        if lockout_data['attempts'] >= cls.MAX_ATTEMPTS:
            lockout_data['until'] = (
                timezone.now() + timedelta(seconds=cls.LOCKOUT_DURATION)
            ).timestamp()

        cache.set(cls._cache_key(user.id), lockout_data, timeout=cls.LOCKOUT_DURATION)

    @classmethod
    def reset_attempts(cls, user):
        """Clear failed attempts after successful login."""
        cache.delete(cls._cache_key(user.id))


# ---------------------------------------------------------------------------
# Rate Limiting
# ---------------------------------------------------------------------------

class RateLimiter:
    """Per-user / per-path rate limiting via cache."""

    @staticmethod
    def check_rate_limit(identifier, limit=100, window=3600):
        cache_key = f"ediv:ratelimit:{identifier}"
        request_count = cache.get(cache_key, 0)
        if request_count >= limit:
            return False
        cache.set(cache_key, request_count + 1, timeout=window)
        return True

    @staticmethod
    def get_remaining_requests(identifier, limit=100, window=3600):
        cache_key = f"ediv:ratelimit:{identifier}"
        return max(0, limit - cache.get(cache_key, 0))


# ---------------------------------------------------------------------------
# Input Sanitisation
# ---------------------------------------------------------------------------

class InputSanitizer:
    """Input sanitization utilities."""

    @staticmethod
    def sanitize_string(value):
        if not isinstance(value, str):
            return value
        for dangerous in ['<script>', '</script>', 'javascript:', 'onerror=']:
            value = value.replace(dangerous, '')
        return value.strip()

    @staticmethod
    def sanitize_html(value):
        import re
        return re.sub(re.compile('<.*?>'), '', value)

    @staticmethod
    def validate_email(email):
        import re
        return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))


# ---------------------------------------------------------------------------
# Audit Logger (database-backed)
# ---------------------------------------------------------------------------

class AuditLogger:
    """Security audit logging — persists to database via AuditLog model."""

    @staticmethod
    def log_login(user, ip_address, success, user_agent=''):
        from apps.audit.models import AuditLog, AuditAction
        from apps.communication.models import UserNotification

        description = f"{'Successful' if success else 'Failed'} login from {ip_address}"
        AuditLog.objects.create(
            user=user,
            action=AuditAction.LOGIN,
            module='auth',
            object_type='User',
            object_id=str(user.id),
            object_repr=user.email,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            new_value={'success': success},
        )

        if not success:
            UserNotification.objects.create(
                user=user,
                title='Failed Login Attempt',
                message=f'Failed login from IP: {ip_address}',
                notification_type='WARNING',
            )

    @staticmethod
    def log_action(user, action, resource_type, resource_id, details=None,
                   ip_address=None, old_value=None, new_value=None, description=''):
        from apps.audit.models import AuditLog

        AuditLog.objects.create(
            user=user,
            action=action,
            module=resource_type,
            object_type=resource_type,
            object_id=str(resource_id) if resource_id else '',
            object_repr=description or f"{action} on {resource_type}#{resource_id}",
            description=description,
            ip_address=ip_address,
            old_value=old_value,
            new_value=new_value,
        )

    @staticmethod
    def get_audit_logs(user_id=None, action=None, module=None, limit=100):
        from apps.audit.models import AuditLog
        qs = AuditLog.objects.select_related('user').all()
        if user_id:
            qs = qs.filter(user_id=user_id)
        if action:
            qs = qs.filter(action=action)
        if module:
            qs = qs.filter(module=module)
        return list(qs.order_by('-created_at')[:limit])


# ---------------------------------------------------------------------------
# Session Manager (database-backed via UserSession, role-aware limits)
# ---------------------------------------------------------------------------

class SessionManager:
    """Session management — backed by UserSession model.

    Role-based max concurrent sessions:
      SYSADMIN/TG/PS  → 3
      Department heads → 3
      PRI/VP           → 3
      TCH/SA_OFF       → 3
      Students/Parents → 2
    """

    # Idle timeout: 30 minutes
    SESSION_TIMEOUT = 1800
    # Absolute timeout: 8 hours
    ABSOLUTE_TIMEOUT = 28800

    # Role → max concurrent sessions
    ROLE_MAX_SESSIONS = {
        'SYSADMIN': 3, 'TG': 3, 'PS': 3,
        'HR': 3, 'FIN': 3, 'AUDIT': 3, 'QA': 3, 'CC': 3,
        'EMIS': 3, 'PLAN': 3, 'PROC': 3, 'PA': 3, 'SA': 3,
        'FRENCH': 3, 'REG': 3,
        'PRI': 3, 'VP': 3,
        'TCH': 3, 'SA_OFF': 3, 'REG_OFF': 3,
        'STD': 2, 'PAR': 2,
    }

    @classmethod
    def max_sessions_for(cls, role):
        return cls.ROLE_MAX_SESSIONS.get(role, 3)

    @classmethod
    def get_active_sessions(cls, user):
        """Return queryset of active (non-expired, non-revoked) sessions."""
        from apps.users.models import UserSession
        now = timezone.now()
        return UserSession.objects.filter(
            user=user,
            status=UserSession.Status.ACTIVE,
        ).filter(
            # Either no explicit expiry, or not yet expired
            models_Q_or_no_expiry(now)
        )

    @classmethod
    def create_session(cls, user, session_key, device_fingerprint='', device_type='',
                       device_os='', device_browser='', ip_address='', user_agent=''):
        """Create a new UserSession. Evicts oldest if over limit."""
        from apps.users.models import UserSession

        max_sess = cls.max_sessions_for(user.role)
        active = UserSession.objects.filter(
            user=user, status=UserSession.Status.ACTIVE,
        ).order_by('last_activity')

        # Evict oldest sessions if at limit
        excess = active.count() - (max_sess - 1)  # -1 because we're adding one
        if excess > 0:
            for session in active[:excess]:
                session.revoke()

        expires_at = timezone.now() + timedelta(seconds=cls.ABSOLUTE_TIMEOUT)
        return UserSession.objects.create(
            user=user,
            session_key=session_key,
            device_fingerprint=device_fingerprint,
            device_type=device_type,
            device_os=device_os,
            device_browser=device_browser,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
        )

    @classmethod
    def validate_session(cls, user, session_key):
        """Check if a session is still valid (not expired, not revoked, idle < 30min)."""
        from apps.users.models import UserSession
        try:
            session = UserSession.objects.get(
                user=user, session_key=session_key, status=UserSession.Status.ACTIVE
            )
        except UserSession.DoesNotExist:
            return False

        now = timezone.now()

        # Check absolute timeout
        if session.expires_at and now > session.expires_at:
            session.revoke()
            return False

        # Check idle timeout
        idle_seconds = (now - session.last_activity).total_seconds()
        if idle_seconds > cls.SESSION_TIMEOUT:
            session.status = UserSession.Status.IDLE
            session.save(update_fields=['status'])
            return False

        return True

    @classmethod
    def update_activity(cls, session_key):
        """Touch the last_activity timestamp."""
        from apps.users.models import UserSession
        UserSession.objects.filter(session_key=session_key).update(last_activity=timezone.now())

    @classmethod
    def revoke_session(cls, session_key):
        """Revoke a single session."""
        from apps.users.models import UserSession
        UserSession.objects.filter(session_key=session_key).update(
            status=UserSession.Status.REVOKED, revoked_at=timezone.now()
        )

    @classmethod
    def revoke_all_sessions(cls, user, except_key=None):
        """Revoke all active sessions for a user (except one if specified)."""
        from apps.users.models import UserSession
        qs = UserSession.objects.filter(user=user, status=UserSession.Status.ACTIVE)
        if except_key:
            qs = qs.exclude(session_key=except_key)
        qs.update(status=UserSession.Status.REVOKED, revoked_at=timezone.now())


# ---------------------------------------------------------------------------
# IP Whitelist (Head Office access control)
# ---------------------------------------------------------------------------

class IPWhitelist:
    """IP whitelist management for Head Office access.

    Whitelist is loaded from:
      1. Environment variable EDIV_WHITELISTED_IPS (comma-separated)
      2. Falls back to localhost/127.0.0.1
    """

    _env_ips = None
    _configured = False

    @classmethod
    def _load_whitelist(cls):
        if cls._env_ips is None:
            raw = os.environ.get('EDIV_WHITELISTED_IPS', '')
            cls._configured = bool(raw)
            cls._env_ips = set(
                ip.strip() for ip in raw.split(',') if ip.strip()
            ) if raw else set()
            cls._env_ips.update(['127.0.0.1', '::1'])
        return cls._env_ips

    @classmethod
    def is_whitelisted(cls, ip_address):
        whitelist = cls._load_whitelist()
        if not cls._configured:
            return True
        return ip_address in whitelist

    @classmethod
    def is_enforced(cls):
        cls._load_whitelist()
        return cls._configured


def require_whitelist(view_func):
    """Decorator to require whitelisted IP (only enforced if EDIV_WHITELISTED_IPS is set)."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if IPWhitelist.is_enforced():
            ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or \
                 request.META.get('REMOTE_ADDR', '')
            if not IPWhitelist.is_whitelisted(ip):
                return HttpResponseForbidden('IP not whitelisted for Head Office access')
        return view_func(request, *args, **kwargs)
    return wrapper


def rate_limit(limit=100, window=3600):
    """Decorator for rate limiting."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            identifier = f"{request.user.id}:{request.path}"
            if not RateLimiter.check_rate_limit(identifier, limit, window):
                return Response(
                    {'error': 'Rate limit exceeded'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# Device Fingerprinting helper
# ---------------------------------------------------------------------------

class DeviceFingerprint:
    """Parse and normalise device information from User-Agent + headers."""

    @staticmethod
    def extract(user_agent='', forwarded_for=''):
        """Return dict with device_type, device_os, device_browser."""
        ua = user_agent.lower()
        result = {'device_type': 'desktop', 'device_os': '', 'device_browser': ''}

        # OS (check before device type since iPhone UA contains "Mac OS X")
        if 'iphone' in ua or 'ipad' in ua:
            result['device_os'] = 'iOS'
        elif 'android' in ua:
            result['device_os'] = 'Android'
        elif 'windows' in ua:
            result['device_os'] = 'Windows'
        elif 'mac os' in ua or 'macos' in ua:
            result['device_os'] = 'macOS'
        elif 'linux' in ua:
            result['device_os'] = 'Linux'

        # Device type
        if any(k in ua for k in ('mobile', 'android', 'iphone', 'ipad')):
            if 'ipad' in ua or 'tablet' in ua:
                result['device_type'] = 'tablet'
            else:
                result['device_type'] = 'mobile'

        # Browser
        if 'edg/' in ua or 'edge/' in ua:
            result['device_browser'] = 'Edge'
        elif 'chrome/' in ua and 'edg/' not in ua:
            result['device_browser'] = 'Chrome'
        elif 'firefox/' in ua:
            result['device_browser'] = 'Firefox'
        elif 'safari/' in ua and 'chrome/' not in ua:
            result['device_browser'] = 'Safari'

        return result

    @staticmethod
    def generate_key(user_agent, ip_address, user_id):
        """Deterministic fingerprint hash from UA + IP + user ID."""
        raw = f"{user_agent}:{ip_address}:{user_id}"
        return hashlib.sha256(raw.encode()).hexdigest()[:64]


# Helper for SessionManager.get_active_sessions (avoids importing django.db.models.Q at module top)
def models_Q_or_no_expiry(now):
    from django.db.models import Q
    return Q(expires_at__isnull=True) | Q(expires_at__gt=now)
