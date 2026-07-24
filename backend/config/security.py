"""
Security utilities for Education District IV Portal.
Enterprise-grade security implementation.
"""

import hashlib
import secrets
import string
from datetime import datetime, timedelta
from functools import wraps
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden
from rest_framework import status
from rest_framework.response import Response


class PasswordValidator:
    """Custom password validator with complexity requirements."""
    
    @staticmethod
    def validate(password):
        """Validate password meets security requirements."""
        errors = []
        
        if len(password) < 12:
            errors.append('Password must be at least 12 characters long')
        
        if not any(c.isupper() for c in password):
            errors.append('Password must contain at least one uppercase letter')
        
        if not any(c.islower() for c in password):
            errors.append('Password must contain at least one lowercase letter')
        
        if not any(c.isdigit() for c in password):
            errors.append('Password must contain at least one digit')
        
        if not any(c in string.punctuation for c in password):
            errors.append('Password must contain at least one special character')
        
        # Check for common passwords
        common_passwords = [
            'password', '1234567890', 'qwertyuiop', 'asdfghjkl',
            'educationdistrict', 'admin123', 'welcome123'
        ]
        if password.lower() in common_passwords:
            errors.append('Password is too common')
        
        return errors
    
    @staticmethod
    def generate_password(length=16):
        """Generate a secure random password."""
        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password


class AccountLockout:
    """Account lockout management."""
    
    MAX_ATTEMPTS = 5
    LOCKOUT_DURATION = 1800  # 30 minutes
    
    @staticmethod
    def check_lockout(user):
        """Check if account is locked out."""
        cache_key = f"ediv:lockout:{user.id}"
        lockout_data = cache.get(cache_key)
        
        if lockout_data:
            if lockout_data['attempts'] >= AccountLockout.MAX_ATTEMPTS:
                lockout_until = lockout_data['until']
                if datetime.now().timestamp() < lockout_until:
                    return True, lockout_until - datetime.now().timestamp()
                else:
                    # Lockout expired, reset
                    cache.delete(cache_key)
        
        return False, 0
    
    @staticmethod
    def record_failed_attempt(user):
        """Record a failed login attempt."""
        cache_key = f"ediv:lockout:{user.id}"
        lockout_data = cache.get(cache_key, {'attempts': 0, 'until': 0})
        
        lockout_data['attempts'] += 1
        
        if lockout_data['attempts'] >= AccountLockout.MAX_ATTEMPTS:
            lockout_data['until'] = (
                datetime.now() + timedelta(seconds=AccountLockout.LOCKOUT_DURATION)
            ).timestamp()
        
        cache.set(cache_key, lockout_data, timeout=AccountLockout.LOCKOUT_DURATION)
    
    @staticmethod
    def reset_attempts(user):
        """Reset failed login attempts after successful login."""
        cache_key = f"ediv:lockout:{user.id}"
        cache.delete(cache_key)


class RateLimiter:
    """API rate limiting."""
    
    @staticmethod
    def check_rate_limit(identifier, limit=100, window=3600):
        """Check if request is within rate limit."""
        cache_key = f"ediv:ratelimit:{identifier}"
        request_count = cache.get(cache_key, 0)
        
        if request_count >= limit:
            return False
        
        cache.set(cache_key, request_count + 1, timeout=window)
        return True
    
    @staticmethod
    def get_remaining_requests(identifier, limit=100, window=3600):
        """Get remaining requests in current window."""
        cache_key = f"ediv:ratelimit:{identifier}"
        request_count = cache.get(cache_key, 0)
        
        return max(0, limit - request_count)


class InputSanitizer:
    """Input sanitization utilities."""
    
    @staticmethod
    def sanitize_string(value):
        """Sanitize string input."""
        if not isinstance(value, str):
            return value
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<script>', '</script>', 'javascript:', 'onerror=']
        for char in dangerous_chars:
            value = value.replace(char, '')
        
        return value.strip()
    
    @staticmethod
    def sanitize_html(value):
        """Remove HTML tags from input."""
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', value)
    
    @staticmethod
    def validate_email(email):
        """Validate email format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))


class AuditLogger:
    """Security audit logging — persists to database via AuditLog model."""

    @staticmethod
    def log_login(user, ip_address, success, user_agent=''):
        """Log login attempt to database."""
        from apps.audit.models import AuditLog, AuditAction
        from apps.communication.models import UserNotification

        action = AuditAction.LOGIN if success else AuditAction.LOGIN
        description = f"{'Successful' if success else 'Failed'} login from {ip_address}"

        AuditLog.objects.create(
            user=user,
            action=action,
            module='auth',
            object_type='User',
            object_id=str(user.id),
            object_repr=user.email,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            new_value={'success': success},
        )

        # Create notification for failed attempts
        if not success:
            UserNotification.objects.create(
                user=user,
                title='Failed Login Attempt',
                message=f'Failed login from IP: {ip_address}',
                notification_type='WARNING'
            )

    @staticmethod
    def log_action(user, action, resource_type, resource_id, details=None,
                   ip_address=None, old_value=None, new_value=None, description=''):
        """Log arbitrary user action to database."""
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
        """Get audit logs from database."""
        from apps.audit.models import AuditLog

        qs = AuditLog.objects.select_related('user').all()

        if user_id:
            qs = qs.filter(user_id=user_id)
        if action:
            qs = qs.filter(action=action)
        if module:
            qs = qs.filter(module=module)

        return list(qs.order_by('-created_at')[:limit])


class SessionManager:
    """Session management utilities."""
    
    MAX_SESSIONS = 3
    SESSION_TIMEOUT = 1800  # 30 minutes
    ABSOLUTE_TIMEOUT = 28800  # 8 hours
    
    @staticmethod
    def check_session_limit(user):
        """Check if user has exceeded session limit."""
        cache_key = f"ediv:sessions:{user.id}"
        sessions = cache.get(cache_key, [])
        
        # Clean expired sessions
        active_sessions = [
            s for s in sessions
            if datetime.now().timestamp() - s['last_activity'] < SessionManager.SESSION_TIMEOUT
        ]
        
        cache.set(cache_key, active_sessions, timeout=SessionManager.ABSOLUTE_TIMEOUT)
        
        return len(active_sessions) >= SessionManager.MAX_SESSIONS
    
    @staticmethod
    def create_session(user, session_id):
        """Create a new session."""
        cache_key = f"ediv:sessions:{user.id}"
        sessions = cache.get(cache_key, [])
        
        sessions.append({
            'session_id': session_id,
            'created_at': datetime.now().timestamp(),
            'last_activity': datetime.now().timestamp()
        })
        
        cache.set(cache_key, sessions, timeout=SessionManager.ABSOLUTE_TIMEOUT)
    
    @staticmethod
    def update_session_activity(user, session_id):
        """Update session last activity."""
        cache_key = f"ediv:sessions:{user.id}"
        sessions = cache.get(cache_key, [])
        
        for session in sessions:
            if session['session_id'] == session_id:
                session['last_activity'] = datetime.now().timestamp()
                break
        
        cache.set(cache_key, sessions, timeout=SessionManager.ABSOLUTE_TIMEOUT)
    
    @staticmethod
    def invalidate_session(user, session_id):
        """Invalidate a specific session."""
        cache_key = f"ediv:sessions:{user.id}"
        sessions = cache.get(cache_key, [])
        
        sessions = [s for s in sessions if s['session_id'] != session_id]
        cache.set(cache_key, sessions, timeout=SessionManager.ABSOLUTE_TIMEOUT)
    
    @staticmethod
    def invalidate_all_sessions(user):
        """Invalidate all user sessions."""
        cache_key = f"ediv:sessions:{user.id}"
        cache.delete(cache_key)


class IPWhitelist:
    """IP whitelist management for Head Office access."""
    
    WHITELISTED_IPS = [
        '127.0.0.1',
        'localhost',
        # Add Head Office IP ranges here
    ]
    
    @staticmethod
    def is_whitelisted(ip_address):
        """Check if IP is whitelisted."""
        return ip_address in IPWhitelist.WHITELISTED_IPS
    
    @staticmethod
    def add_ip(ip_address):
        """Add IP to whitelist."""
        if ip_address not in IPWhitelist.WHITELISTED_IPS:
            IPWhitelist.WHITELISTED_IPS.append(ip_address)
    
    @staticmethod
    def remove_ip(ip_address):
        """Remove IP from whitelist."""
        if ip_address in IPWhitelist.WHITELISTED_IPS:
            IPWhitelist.WHITELISTED_IPS.remove(ip_address)


def require_whitelist(view_func):
    """Decorator to require whitelisted IP."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        ip_address = request.META.get('REMOTE_ADDR')
        if not IPWhitelist.is_whitelisted(ip_address):
            return HttpResponseForbidden('IP not whitelisted')
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
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
