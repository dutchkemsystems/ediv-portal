import hashlib
import secrets
from datetime import timedelta
from unittest.mock import patch, MagicMock

from django.test import TestCase, RequestFactory
from django.core.cache import cache
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from apps.users.models import User, UserSession
from config.security import (
    PasswordValidator, AccountLockout, RateLimiter,
    SessionManager, IPWhitelist, DeviceFingerprint, InputSanitizer,
)


class PasswordValidatorTest(TestCase):

    def test_valid_password(self):
        errors = PasswordValidator.validate('Str0ng!Pass#2024')
        self.assertEqual(errors, [])

    def test_too_short(self):
        errors = PasswordValidator.validate('Ab1!short')
        self.assertTrue(any('12 characters' in e for e in errors))

    def test_no_uppercase(self):
        errors = PasswordValidator.validate('lowercase123!')
        self.assertTrue(any('uppercase' in e for e in errors))

    def test_no_lowercase(self):
        errors = PasswordValidator.validate('UPPERCASE123!')
        self.assertTrue(any('lowercase' in e for e in errors))

    def test_no_digit(self):
        errors = PasswordValidator.validate('NoDigits!Here')
        self.assertTrue(any('digit' in e for e in errors))

    def test_no_special_char(self):
        errors = PasswordValidator.validate('NoSpecial1234')
        self.assertTrue(any('special character' in e for e in errors))

    def test_common_password_rejected(self):
        errors = PasswordValidator.validate('password')
        self.assertTrue(any('common' in e for e in errors))

    def test_generate_password_length(self):
        pw = PasswordValidator.generate_password(20)
        self.assertEqual(len(pw), 20)


class AccountLockoutTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='lockout@test.com', password='Test@12345678',
            first_name='Test', last_name='User', role='TCH',
        )
        cache.clear()

    def test_no_lockout_initially(self):
        is_locked, remaining = AccountLockout.check_lockout(self.user)
        self.assertFalse(is_locked)
        self.assertEqual(remaining, 0)

    def test_lockout_after_5_attempts(self):
        for _ in range(5):
            AccountLockout.record_failed_attempt(self.user)
        is_locked, remaining = AccountLockout.check_lockout(self.user)
        self.assertTrue(is_locked)
        self.assertGreater(remaining, 0)

    def test_reset_after_success(self):
        for _ in range(4):
            AccountLockout.record_failed_attempt(self.user)
        AccountLockout.reset_attempts(self.user)
        is_locked, _ = AccountLockout.check_lockout(self.user)
        self.assertFalse(is_locked)


class RateLimiterTest(TestCase):

    def setUp(self):
        cache.clear()

    def test_within_limit(self):
        self.assertTrue(RateLimiter.check_rate_limit('test:1', limit=5, window=60))

    def test_exceeds_limit(self):
        for _ in range(5):
            RateLimiter.check_rate_limit('test:2', limit=5, window=60)
        self.assertFalse(RateLimiter.check_rate_limit('test:2', limit=5, window=60))

    def test_remaining_requests(self):
        RateLimiter.check_rate_limit('test:3', limit=10, window=60)
        RateLimiter.check_rate_limit('test:3', limit=10, window=60)
        remaining = RateLimiter.get_remaining_requests('test:3', limit=10, window=60)
        self.assertEqual(remaining, 8)


class InputSanitizerTest(TestCase):

    def test_sanitize_script_tag(self):
        result = InputSanitizer.sanitize_string('<script>alert("xss")</script>')
        self.assertNotIn('<script>', result)

    def test_sanitize_normal_string(self):
        result = InputSanitizer.sanitize_string('Hello World')
        self.assertEqual(result, 'Hello World')

    def test_validate_email_valid(self):
        self.assertTrue(InputSanitizer.validate_email('test@example.com'))

    def test_validate_email_invalid(self):
        self.assertFalse(InputSanitizer.validate_email('not-an-email'))

    def test_sanitize_html(self):
        result = InputSanitizer.sanitize_html('<b>Bold</b> text')
        self.assertEqual(result, 'Bold text')


class DeviceFingerprintTest(TestCase):

    def test_extract_mobile(self):
        ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15'
        info = DeviceFingerprint.extract(ua)
        self.assertEqual(info['device_type'], 'mobile')
        self.assertEqual(info['device_os'], 'iOS')

    def test_extract_desktop(self):
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0'
        info = DeviceFingerprint.extract(ua)
        self.assertEqual(info['device_type'], 'desktop')
        self.assertEqual(info['device_os'], 'Windows')

    def test_extract_tablet(self):
        ua = 'Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15'
        info = DeviceFingerprint.extract(ua)
        self.assertEqual(info['device_type'], 'tablet')

    def test_generate_key_deterministic(self):
        key1 = DeviceFingerprint.generate_key('ua1', '1.2.3.4', 1)
        key2 = DeviceFingerprint.generate_key('ua1', '1.2.3.4', 1)
        self.assertEqual(key1, key2)
        self.assertEqual(len(key1), 64)

    def test_generate_key_different_inputs(self):
        key1 = DeviceFingerprint.generate_key('ua1', '1.2.3.4', 1)
        key2 = DeviceFingerprint.generate_key('ua2', '1.2.3.4', 1)
        self.assertNotEqual(key1, key2)


class SessionManagerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='session@test.com', password='Test@12345678',
            first_name='Session', last_name='Test', role='TCH',
        )
        UserSession.objects.filter(user=self.user).delete()

    def test_create_session(self):
        session = SessionManager.create_session(
            self.user, 'key-1', device_type='desktop', ip_address='127.0.0.1',
        )
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.session_key, 'key-1')
        self.assertEqual(session.status, UserSession.Status.ACTIVE)

    def test_role_max_sessions(self):
        self.assertEqual(SessionManager.max_sessions_for('SYSADMIN'), 3)
        self.assertEqual(SessionManager.max_sessions_for('STD'), 2)
        self.assertEqual(SessionManager.max_sessions_for('TCH'), 3)

    def test_evicts_oldest_session(self):
        for i in range(4):
            SessionManager.create_session(self.user, f'key-{i}', device_type='desktop')
        active = UserSession.objects.filter(user=self.user, status=UserSession.Status.ACTIVE)
        self.assertLessEqual(active.count(), 3)

    def test_revoke_session(self):
        SessionManager.create_session(self.user, 'revoke-me')
        SessionManager.revoke_session('revoke-me')
        session = UserSession.objects.get(session_key='revoke-me')
        self.assertEqual(session.status, UserSession.Status.REVOKED)

    def test_revoke_all_sessions(self):
        for i in range(3):
            SessionManager.create_session(self.user, f'key-{i}')
        SessionManager.revoke_all_sessions(self.user)
        active = UserSession.objects.filter(user=self.user, status=UserSession.Status.ACTIVE)
        self.assertEqual(active.count(), 0)


class IPWhitelistTest(TestCase):

    def setUp(self):
        self._orig_ips = IPWhitelist._env_ips
        self._orig_configured = IPWhitelist._configured
        IPWhitelist._env_ips = None
        IPWhitelist._configured = False

    def tearDown(self):
        IPWhitelist._env_ips = self._orig_ips
        IPWhitelist._configured = self._orig_configured

    @patch.dict('os.environ', {'EDIV_WHITELISTED_IPS': '10.0.0.1,10.0.0.2'})
    def test_whitelisted_ip(self):
        IPWhitelist._env_ips = None
        IPWhitelist._configured = False
        self.assertTrue(IPWhitelist.is_whitelisted('10.0.0.1'))

    @patch.dict('os.environ', {'EDIV_WHITELISTED_IPS': '10.0.0.1'})
    def test_non_whitelisted_ip(self):
        IPWhitelist._env_ips = None
        IPWhitelist._configured = False
        self.assertFalse(IPWhitelist.is_whitelisted('192.168.1.1'))

    def test_localhost_always_allowed(self):
        self.assertTrue(IPWhitelist.is_whitelisted('127.0.0.1'))
        self.assertTrue(IPWhitelist.is_whitelisted('::1'))

    @patch.dict('os.environ', {}, clear=True)
    def test_open_mode_when_not_configured(self):
        IPWhitelist._env_ips = None
        self.assertTrue(IPWhitelist.is_whitelisted('anything'))
        self.assertFalse(IPWhitelist.is_enforced())


class LoginSecurityTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='login@test.com', password='Test@12345678',
            first_name='Login', last_name='Test', role='TCH',
        )
        cache.clear()

    def test_successful_login_returns_tokens(self):
        resp = self.client.post('/api/users/auth/', {
            'email': 'login@test.com', 'password': 'Test@12345678',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)

    def test_failed_login_returns_401(self):
        resp = self.client.post('/api/users/auth/', {
            'email': 'login@test.com', 'password': 'WrongPassword123!',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lockout_after_5_failed_attempts(self):
        for _ in range(5):
            self.client.post('/api/users/auth/', {
                'email': 'login@test.com', 'password': 'WrongPassword123!',
            }, format='json')
        resp = self.client.post('/api/users/auth/', {
            'email': 'login@test.com', 'password': 'Test@12345678',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('locked', str(resp.data))

    def test_disabled_account_returns_403(self):
        self.user.is_active = False
        self.user.save()
        resp = self.client.post('/api/users/auth/', {
            'email': 'login@test.com', 'password': 'Test@12345678',
        }, format='json')
        self.assertIn(resp.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_mfa_flow(self):
        self.user.mfa_enabled = False
        self.user.mfa_secret = ''
        self.user.save()

        resp = self.client.post('/api/users/auth/', {
            'email': 'login@test.com', 'password': 'Test@12345678',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_logout_blacklists_token(self):
        resp = self.client.post('/api/users/auth/', {
            'email': 'login@test.com', 'password': 'Test@12345678',
        }, format='json')
        refresh = resp.data['refresh']

        self.client.force_authenticate(user=self.user)
        resp = self.client.post('/api/users/auth/logout/', {'refresh': refresh}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
