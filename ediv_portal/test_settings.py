"""
Test settings for Django project.
Uses SQLite in-memory database for fast test execution.
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Add backend/ to Python path
BACKEND_DIR = str(BASE_DIR / 'backend')
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Set environment
os.environ.setdefault('DJANGO_SECRET_KEY', 'test-secret-key-for-testing-only')

# Import base settings
from config.settings.base import *  # noqa

# Override database to SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Debug for tests
DEBUG = True

# Disable security middleware for tests
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Use faster password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Override ROOT_URLCONF
ROOT_URLCONF = 'ediv_portal.urls'
WSGI_APPLICATION = 'ediv_portal.wsgi.application'

# Disable CORS for tests
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Skip migrations for faster tests
MIGRATION_MODULES = {
    'users': None,
    'schools': None,
    'staff': None,
    'students': None,
    'academics': None,
    'attendance': None,
    'files': None,
    'departments': None,
    'notifications': None,
    'workflows': None,
    'hr': None,
    'finance': None,
    'audit': None,
    'inspection': None,
    'discipline': None,
    'infrastructure': None,
    'transport': None,
    'assets': None,
    'library': None,
    'co_curricular': None,
    'e_learning': None,
    'wellness': None,
    'alumni': None,
    'reports': None,
    'analytics': None,
    'communication': None,
    'cpd': None,
    'french': None,
    'parent_teacher': None,
    'registry': None,
    'data_import_export': None,
    'mail_workflow': None,
    'sessions': None,
    'timetable': None,
}
