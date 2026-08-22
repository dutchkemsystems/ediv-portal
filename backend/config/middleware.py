from django.utils.deprecation import MiddlewareMixin

from config.security import DeviceFingerprint, SessionManager


class SessionTrackingMiddleware(MiddlewareMixin):
    """Enforces session timeout, creates UserSession records, and tracks device fingerprints.

    Optimized for cold start: skips DB operations when no session_key is found,
    and uses select_related where possible to minimize queries.
    """

    SAFE_PATHS = ("/api/users/auth/", "/health/", "/api/health/", "/wake/", "/admin/", "/static/", "/media/")
    SAFE_PREFIXES = ("/api/users/auth/", "/health/", "/api/health/", "/wake/")

    def process_request(self, request):
        path = request.path

        if any(path.startswith(p) for p in self.SAFE_PREFIXES):
            return None

        if not hasattr(request, "user") or not request.user.is_authenticated:
            return None

        user = request.user
        session_key = self._get_session_key(request)

        if not session_key:
            return None

        session = self._get_or_create_session(request, user, session_key)
        if session is None:
            return None

        if not SessionManager.validate_session(user, session_key):
            SessionManager.revoke_session(session_key)
            from rest_framework import status
            from rest_framework.response import Response

            return Response(
                {"error": "Session expired. Please log in again."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        SessionManager.update_activity(session_key)
        return None

    def _get_session_key(self, request):
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth.startswith("Bearer "):
            return None

        token_str = auth[7:]
        try:
            from rest_framework_simplejwt.tokens import AccessToken

            token = AccessToken(token_str)
            return str(token.get("jti", token_str[:32]))
        except Exception:
            return None

    def _get_or_create_session(self, request, user, session_key):
        from apps.users.models import UserSession

        try:
            return UserSession.objects.select_related("user").get(
                session_key=session_key, status=UserSession.Status.ACTIVE
            )
        except UserSession.DoesNotExist:
            pass

        ua = request.META.get("HTTP_USER_AGENT", "")
        ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or request.META.get("REMOTE_ADDR", "")
        device_info = DeviceFingerprint.extract(ua, ip)
        fp_hash = DeviceFingerprint.generate_key(ua, ip, user.id)

        return SessionManager.create_session(
            user=user,
            session_key=session_key,
            device_fingerprint=fp_hash,
            device_type=device_info["device_type"],
            device_os=device_info["device_os"],
            device_browser=device_info["device_browser"],
            ip_address=ip,
            user_agent=ua,
        )
