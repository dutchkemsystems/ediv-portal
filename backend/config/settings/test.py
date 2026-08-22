"""
Test settings for Django project.
Uses SQLite in-memory database for fast, deterministic test execution.
"""

from .base import *  # noqa: F401, F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

DEBUG = True

# Disable security middleware for tests
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Use faster password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable CORS for tests
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Skip migrations for faster tests
MIGRATION_MODULES = {
    "users": None,
    "schools": None,
    "staff": None,
    "students": None,
    "academics": None,
    "attendance": None,
    "files": None,
    "departments": None,
    "notifications": None,
    "workflows": None,
    "hr": None,
    "finance": None,
    "audit": None,
    "inspection": None,
    "discipline": None,
    "infrastructure": None,
    "transport": None,
    "assets": None,
    "library": None,
    "co_curricular": None,
    "e_learning": None,
    "wellness": None,
    "alumni": None,
    "reports": None,
    "analytics": None,
    "communication": None,
    "cpd": None,
    "french": None,
    "parent_teacher": None,
    "registry": None,
    "data_import_export": None,
    "mail_workflow": None,
    "sessions": None,
    "timetable": None,
    "predictive_analytics": None,
    "chatbot": None,
    "blockchain_cert": None,
    "multilingual": None,
    "gamification": None,
    "push_notifications": None,
    "iot_dashboard": None,
    "benchmarking": None,
    "report_card_gen": None,
}
