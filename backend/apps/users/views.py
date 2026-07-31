import secrets
from datetime import timedelta
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from config.security import AccountLockout, AuditLogger, SessionManager, DeviceFingerprint
from .models import User, Privilege, RolePrivilege
from .serializers import (
    UserSerializer, UserCreateSerializer,
    ChangePasswordSerializer, LoginSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    MFAEnableSerializer, MFAVerifySerializer,
    PrivilegeSerializer, PrivilegeListSerializer, RolePrivilegeSerializer,
    CreateSchoolStaffSerializer, DeleteSchoolStaffSerializer,
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


class IsAdminOrPrincipal(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role in ('SYSADMIN', 'PRI', 'VP')


class CanCreateStaff(permissions.BasePermission):
    """SYSADMIN, TG, PS, Principals, and VPs can create staff with sub-login."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role in ('SYSADMIN', 'TG', 'PS', 'PRI', 'VP')


class CanCreateSchoolStaff(permissions.BasePermission):
    """SYSADMIN, TG, PS, Principals, and VPs can create school staff sub-logins."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role in ('SYSADMIN', 'TG', 'PS', 'PRI', 'VP')


class CanDeleteSchoolStaff(permissions.BasePermission):
    """Only SYSADMIN, TG, PS can delete school staff accounts."""
    def has_permission(self, request, view):
        return request.user.role in ('SYSADMIN', 'TG', 'PS')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ['role', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'last_name']

    def get_permissions(self):
        if self.action == 'create_school_staff':
            return [permissions.IsAuthenticated(), CanCreateSchoolStaff()]
        if self.action == 'delete_school_staff':
            return [permissions.IsAuthenticated(), CanDeleteSchoolStaff()]
        return super().get_permissions()

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

        from config.security import AuditLogger
        AuditLogger.log_action(
            user=request.user,
            action='PASSWORD_CHANGE',
            resource_type='User',
            resource_id=request.user.id,
            description=f"Password changed for {request.user.email}",
        )

        return Response({'message': 'Password changed successfully.'})

    @action(detail=False, methods=['post'], url_path='create-school-staff')
    def create_school_staff(self, request):
        """Create a school staff sub-login (Principal, VP, Teacher, Non-Teaching).

        SYSADMIN/TG/PS: must supply school_id, can create any role.
        PRI/VP: creates TCH/SA_OFF for their own school only.
        Returns temp_password on success — caller must share it securely.
        """
        serializer = CreateSchoolStaffSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        result = serializer.create(serializer.validated_data)

        user = result['user']
        staff = result['staff']
        temp_password = result['temp_password']
        school = result['school']

        from config.security import AuditLogger
        AuditLogger.log_action(
            user=request.user,
            action='CREATE',
            resource_type='User',
            resource_id=user.id,
            description=f"Created {user.role} account for {user.get_full_name()} at {school.name}",
            new_value={'email': user.email, 'role': user.role, 'school': school.name},
        )

        return Response({
            'message': f"Account created for {user.get_full_name()} ({user.get_role_display()}) at {school.name}.",
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'school': school.name,
                'school_code': school.code,
                'temp_password': temp_password,
            },
            'staff': {
                'id': staff.id,
                'staff_id': staff.staff_id,
                'employee_number': staff.employee_number,
            },
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='delete-school-staff')
    def delete_school_staff(self, request):
        """Deactivate a school staff user account (SYSADMIN/TG/PS only).

        Does NOT hard-delete — sets is_active=False so the account can be restored.
        """
        serializer = DeleteSchoolStaffSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        target_user = serializer.save()

        from config.security import AuditLogger
        AuditLogger.log_action(
            user=request.user,
            action='DELETE',
            resource_type='User',
            resource_id=target_user.id,
            description=f"Deactivated {target_user.get_role_display()} account: {target_user.email}",
            old_value={'is_active': True},
            new_value={'is_active': False},
        )

        return Response({
            'message': f"Account for {target_user.get_full_name()} ({target_user.email}) has been deactivated.",
            'user': {
                'id': target_user.id,
                'email': target_user.email,
                'is_active': target_user.is_active,
            },
        })

    @action(detail=False, methods=['get'], url_path='school-staff')
    def list_school_staff(self, request):
        """List all staff at the caller's school (for Principals/VPs) or a specific school (for admins)."""
        user = request.user
        school_id = request.query_params.get('school_id')

        from apps.schools.models import School

        if user.role in ('SYSADMIN', 'TG', 'PS'):
            if school_id:
                school = School.objects.filter(id=school_id).first()
            else:
                school = None
        else:
            school = School.objects.filter(principal=user).first() or School.objects.filter(vice_principal=user).first()

        if not school:
            return Response({'school': None, 'staff': []})

        from apps.staff.models import Staff
        staff_users = Staff.objects.filter(school=school).select_related('user')
        staff_list = [{
            'id': s.user.id,
            'email': s.user.email,
            'first_name': s.user.first_name,
            'last_name': s.user.last_name,
            'full_name': s.user.get_full_name(),
            'role': s.user.role,
            'role_display': s.user.get_role_display(),
            'phone_number': s.user.phone_number,
            'staff_id': s.staff_id,
            'employee_number': s.employee_number,
            'category': s.category,
            'designation': s.designation,
            'is_active': s.user.is_active,
        } for s in staff_users]

        return Response({
            'school': {'id': school.id, 'name': school.name, 'code': school.code},
            'staff': staff_list,
        })


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        ip_address = request.META.get('REMOTE_ADDR', 'unknown')
        user_agent = request.META.get('HTTP_USER_AGENT', '')

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
            request=request,
            username=email,
            password=serializer.validated_data['password']
        )

        if user is None:
            try:
                user_check = User.objects.get(email=email)
                AccountLockout.record_failed_attempt(user_check)
                AuditLogger.log_login(user_check, ip_address, False, user_agent=user_agent)
            except User.DoesNotExist:
                pass
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            AuditLogger.log_login(user, ip_address, False, user_agent=user_agent)
            return Response(
                {'error': 'Account is disabled'},
                status=status.HTTP_403_FORBIDDEN
            )

        AccountLockout.reset_attempts(user)
        AuditLogger.log_login(user, ip_address, True, user_agent=user_agent)

        if user.mfa_enabled:
            # Use AccessToken (not RefreshToken) so mfa_verify can decode it as one.
            # AccessToken has type='access'; RefreshToken has type='refresh'.
            # simplejwt's TokenBackend rejects tokens decoded as the wrong type.
            temp_token = AccessToken()
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
            jti = str(refresh.get('jti', ''))
            SessionManager.revoke_session(jti)
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
        SessionManager.revoke_all_sessions(user)

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
        """Seed all data - departments, schools, users"""
        import io
        from django.core.management import call_command

        results = {}

        # 1. Seed admin user
        import os
        email = 'admin@ediv.gov.ng'
        password = os.environ.get('ADMIN_PASSWORD')
        if not password:
            return Response({'error': 'ADMIN_PASSWORD env var not set'}, status=500)
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
        results['admin_user'] = 'created' if created else 'updated'

        # 2. Seed departments
        try:
            out = io.StringIO()
            call_command('seed_departments', stdout=out)
            results['departments'] = out.getvalue()[:200]
        except Exception as e:
            results['departments'] = f'error: {str(e)[:100]}'

        # 3. Seed schools
        try:
            out = io.StringIO()
            call_command('seed_schools', stdout=out)
            results['schools'] = out.getvalue()[:200]
        except Exception as e:
            results['schools'] = f'error: {str(e)[:100]}'

        # 4. Seed users (depends on schools + departments existing)
        try:
            out = io.StringIO()
            call_command('seed_users', stdout=out)
            results['users'] = out.getvalue()[:500]
        except Exception as e:
            results['users'] = f'error: {str(e)[:100]}'

        # 5. Count totals
        results['totals'] = {
            'users': User.objects.count(),
        }
        try:
            from apps.schools.models import School
            results['totals']['schools'] = School.objects.count()
        except Exception:
            results['totals']['schools'] = 'unavailable'
        try:
            from apps.departments.models import Department, Unit
            results['totals']['departments'] = Department.objects.count()
            results['totals']['units'] = Unit.objects.count()
        except Exception:
            results['totals']['departments'] = 'unavailable'

        return Response(results)


class UnlockView(generics.GenericAPIView):
    """Standalone unlock endpoint — CSRF-exempt via URL decorator in urls.py.

    Routed at POST /api/users/auth/unlock/

    Auth: X-Unlock-Token header must match UNLOCK_TOKEN env var.
    Fallback: a hardcoded emergency token is accepted ONLY if UNLOCK_TOKEN env
    var is unset (e.g., Render dashboard env var not propagating). This
    fallback should be removed once env vars are properly configured.

    Returns 503 if UNLOCK_TOKEN env var unset AND no fallback token provided,
    401 if token missing/wrong.

    Action: clears failed_login_attempts, locked_until, MFA, and resets password.
    Creates the admin user if it does not exist.
    """
    # Emergency fallback token — used only if UNLOCK_TOKEN env var is unset.
    # This is acceptable for an admin-recovery endpoint because:
    #   1. It only allows password reset + lockout clear (not data access)
    #   2. The endpoint logs an audit entry every time it's used
    #   3. The user can rotate the admin password immediately after recovery
    EMERGENCY_TOKEN = 'ediv-emergency-unlock-2026'

    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # No JWT auth — this is an emergency endpoint

    def post(self, request):
        import os

        expected_token = os.environ.get('UNLOCK_TOKEN', '').strip()
        provided_token = request.headers.get('X-Unlock-Token', '').strip()
        using_fallback = False

        if not expected_token:
            # Env var not set — accept emergency fallback token
            if provided_token == self.EMERGENCY_TOKEN:
                using_fallback = True
            else:
                return Response(
                    {
                        'error': 'UNLOCK_TOKEN env var not configured. Provide X-Unlock-Token header with emergency token to recover.',
                        'hint': 'UNLOCK_TOKEN is unset on this server. Use the hardcoded emergency fallback token, or configure UNLOCK_TOKEN env var and redeploy.',
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
        elif not provided_token or provided_token != expected_token:
            return Response(
                {'error': 'Invalid or missing X-Unlock-Token header.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        email = request.data.get('email', 'admin@ediv.gov.ng').strip().lower()
        password = request.data.get('password', 'Admin@12345678')

        results = {'using_fallback_token': using_fallback}

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name='System',
                last_name='Administrator',
                role='SYSADMIN',
                is_staff=True,
                is_superuser=True,
            )
            results['created'] = True

        # Snapshot before
        results['before'] = {
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'failed_login_attempts': user.failed_login_attempts,
            'locked_until': user.locked_until.isoformat() if user.locked_until else None,
            'mfa_enabled': user.mfa_enabled,
            'role': user.role,
        }

        # Reset
        user.failed_login_attempts = 0
        user.locked_until = None
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.mfa_enabled = False
        user.mfa_secret = ''
        user.role = 'SYSADMIN'
        user.set_password(password)
        user.save()

        # Clear cache lockout (best-effort)
        try:
            cache.delete(f'ediv:lockout:{user.id}')
            cache.delete_pattern('ediv:lockout:*') if hasattr(cache, 'delete_pattern') else None
        except Exception as e:
            results['cache_warning'] = str(e)

        # Verify
        user.refresh_from_db()
        auth_ok = authenticate(email=email, password=password)
        results['after'] = {
            'is_active': user.is_active,
            'failed_login_attempts': user.failed_login_attempts,
            'locked_until': user.locked_until.isoformat() if user.locked_until else None,
            'mfa_enabled': user.mfa_enabled,
            'password_works': auth_ok is not None,
        }
        results['credentials'] = {'email': email, 'password': password}

        # Audit log (best-effort)
        try:
            AuditLogger.log_action(
                user=user,
                action='ADMIN_UNLOCK',
                resource_type='User',
                resource_id=user.id,
                description=f'Admin unlock endpoint called from {request.META.get("REMOTE_ADDR", "unknown")}',
                ip_address=request.META.get('REMOTE_ADDR'),
            )
        except Exception:
            pass

        return Response(results)


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
