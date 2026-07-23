import secrets
from datetime import timedelta
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from config.security import AccountLockout, AuditLogger
from .models import User, Privilege, RolePrivilege
from .serializers import (
    UserSerializer, UserCreateSerializer,
    ChangePasswordSerializer, LoginSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    MFAEnableSerializer, MFAVerifySerializer,
    PrivilegeSerializer, PrivilegeListSerializer, RolePrivilegeSerializer,
)
from .mfa import (
    generate_mfa_secret, get_mfa_qr_code_url,
    verify_mfa_code, get_mfa_provisioning_uri,
)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == 'SYSADMIN'


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ['role', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'last_name']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'SYSADMIN':
            return User.objects.all()
        elif user.is_department_head or user.is_head_office_staff:
            return User.objects.all()
        elif user.is_school_staff:
            return User.objects.filter(role__in=['PRI', 'VP', 'TCH', 'STD'])
        return User.objects.filter(id=user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'message': 'Password changed successfully.'})


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        ip_address = request.META.get('REMOTE_ADDR', 'unknown')

        # Check account lockout
        try:
            user_check = User.objects.get(email=email)
            is_locked, remaining = AccountLockout.check_lockout(user_check)
            if is_locked:
                return Response(
                    {'error': f'Account is locked. Try again in {int(remaining / 60)} minutes.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except User.DoesNotExist:
            pass

        user = authenticate(
            email=email,
            password=serializer.validated_data['password']
        )

        if user is None:
            try:
                user_check = User.objects.get(email=email)
                AccountLockout.record_failed_attempt(user_check)
                AuditLogger.log_login(user_check, ip_address, False)
            except User.DoesNotExist:
                pass
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            AuditLogger.log_login(user, ip_address, False)
            return Response(
                {'error': 'Account is disabled'},
                status=status.HTTP_403_FORBIDDEN
            )

        AccountLockout.reset_attempts(user)
        AuditLogger.log_login(user, ip_address, True)

        if user.mfa_enabled:
            temp_token = RefreshToken()
            temp_token['user_id'] = user.id
            temp_token.set_exp(lifetime=timedelta(minutes=5))
            return Response({
                'mfa_required': True,
                'temp_token': str(temp_token),
                'user': UserSerializer(user).data,
            })

        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        })

    @action(detail=False, methods=['post'])
    def refresh(self, request):
        try:
            refresh = RefreshToken(request.data.get('refresh'))
            return Response({
                'access': str(refresh.access_token),
            })
        except Exception:
            return Response(
                {'error': 'Invalid refresh token'},
                status=status.HTTP_401_UNAUTHORIZED
            )

    @action(detail=False, methods=['post'])
    def logout(self, request):
        try:
            refresh = RefreshToken(request.data.get('refresh'))
            refresh.blacklist()
            return Response({'message': 'Logged out successfully.'})
        except Exception:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def forgot_password(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        # Always return success to prevent email enumeration
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            return Response(
                {'message': 'If an account exists with this email, a reset link has been sent.'}
            )

        # Generate secure token
        token = secrets.token_urlsafe(32)
        cache_key = f"ediv:password_reset:{token}"
        cache.set(cache_key, {'user_id': user.id, 'created_at': str(__import__('datetime').datetime.now())}, timeout=3600)

        # Build reset URL
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        reset_url = f"{frontend_url}/reset-password?token={token}"

        # Send email
        try:
            send_mail(
                subject='Education District IV — Password Reset Request',
                message=(
                    f'Hello {user.get_full_name()},\n\n'
                    f'We received a request to reset your password.\n\n'
                    f'Click the link below to reset your password (valid for 1 hour):\n\n'
                    f'{reset_url}\n\n'
                    f'If you did not request this, please ignore this email.\n\n'
                    f'Regards,\nEducation District IV Portal'
                ),
                from_email=getattr(settings, 'EMAIL_HOST_USER', 'noreply@ediv.gov.ng'),
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass  # Don't reveal email failure to the user

        return Response(
            {'message': 'If an account exists with this email, a reset link has been sent.'}
        )

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        cache_key = f"ediv:password_reset:{token}"
        reset_data = cache.get(cache_key)

        if not reset_data:
            return Response(
                {'error': 'Invalid or expired reset token.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=reset_data['user_id'], is_active=True)
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired reset token.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Set new password
        user.set_password(new_password)
        user.failed_login_attempts = 0
        user.locked_until = None
        user.save()

        # Invalidate the token
        cache.delete(cache_key)

        # Invalidate all existing sessions
        from config.security import SessionManager
        SessionManager.invalidate_all_sessions(user)

        AuditLogger.log_action(user, 'PASSWORD_RESET', 'user', user.id)

        return Response({'message': 'Password reset successfully. You can now log in with your new password.'})

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mfa_setup(self, request):
        user = request.user
        if user.mfa_enabled:
            return Response(
                {'error': 'MFA is already enabled. Disable it first to reconfigure.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        secret = generate_mfa_secret()
        user.mfa_secret = secret
        user.save(update_fields=['mfa_secret'])

        qr_url = get_mfa_qr_code_url(secret, user.email)
        provisioning_uri = get_mfa_provisioning_uri(secret, user.email)

        return Response({
            'secret': secret,
            'qr_code_url': qr_url,
            'provisioning_uri': provisioning_uri,
        })

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mfa_enable(self, request):
        serializer = MFAEnableSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.mfa_secret:
            return Response(
                {'error': 'MFA setup not initiated. Call mfa/setup first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.mfa_enabled:
            return Response(
                {'error': 'MFA is already enabled.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not verify_mfa_code(user.mfa_secret, serializer.validated_data['code']):
            return Response(
                {'error': 'Invalid MFA code.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.mfa_enabled = True
        user.save(update_fields=['mfa_enabled'])

        return Response({'message': 'MFA enabled successfully.'})

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mfa_disable(self, request):
        serializer = MFAEnableSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.mfa_enabled:
            return Response(
                {'error': 'MFA is not enabled.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not verify_mfa_code(user.mfa_secret, serializer.validated_data['code']):
            return Response(
                {'error': 'Invalid MFA code.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.mfa_enabled = False
        user.mfa_secret = ''
        user.save(update_fields=['mfa_enabled', 'mfa_secret'])

        return Response({'message': 'MFA disabled successfully.'})

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def mfa_verify(self, request):
        serializer = MFAVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        temp_token = serializer.validated_data['temp_token']
        mfa_code = serializer.validated_data['mfa_code']

        try:
            from rest_framework_simplejwt.tokens import AccessToken
            token = AccessToken(temp_token)
            user_id = token['user_id']
        except Exception:
            return Response(
                {'error': 'Invalid or expired temp token.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired temp token.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.mfa_enabled:
            return Response(
                {'error': 'MFA is not enabled for this account.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not verify_mfa_code(user.mfa_secret, mfa_code):
            return Response(
                {'error': 'Invalid MFA code.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        })

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def seed(self, request):
        """Seed admin user - for initial deployment only"""
        email = 'admin@ediv.gov.ng'
        password = 'Admin@12345678'
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'SYSADMIN',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        user.set_password(password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.role = 'SYSADMIN'
        user.save()
        return Response({
            'message': f'Admin user {"created" if created else "updated"}',
            'email': email,
        })


class PrivilegeViewSet(viewsets.ModelViewSet):
    queryset = Privilege.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ['role', 'module']
    search_fields = ['role', 'module']
    ordering_fields = ['role', 'module', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return PrivilegeListSerializer
        return PrivilegeSerializer


class RolePrivilegeViewSet(viewsets.ModelViewSet):
    queryset = RolePrivilege.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = RolePrivilegeSerializer
    filterset_fields = ['role']
    search_fields = ['role', 'description']
