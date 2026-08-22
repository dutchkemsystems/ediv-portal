import importlib.util
import os
from copy import copy as _copy
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _patch_django_context_copy():
    """Fix Django < 4.2.27 BaseContext.__copy__ crash on Python 3.14+.

    Upstream fix: https://github.com/django/django/pull/18824 (ticket #35844).
    ``copy(super())`` is no longer copyable on Python 3.14+, so template
    contexts crash during tests (store_rendered_templates) and admin rendering.
    """
    try:
        from django.template import context as _django_context
    except ImportError:
        return

    cls = _django_context.BaseContext
    try:
        import inspect

        src_text = inspect.getsource(cls.__copy__)
    except (OSError, TypeError):
        src_text = ""
    # Only patch the known-buggy implementation.
    if "copy(super())" not in src_text:
        return

    def _base_context_copy(self):
        duplicate = cls()
        duplicate.__class__ = self.__class__
        duplicate.__dict__ = _copy(self.__dict__)
        duplicate.dicts = self.dicts[:]
        return duplicate

    cls.__copy__ = _base_context_copy


_patch_django_context_copy()


def _load_env_file(path):
    """Load a .env file into os.environ without overriding existing variables."""
    if not path.is_file():
        return
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


# Load .env files so settings can be configured without exporting variables.
_load_env_file(BASE_DIR / ".env")
_load_env_file(BASE_DIR.parent / ".env")

# Dev/CI-safe default. production.py re-validates and refuses to start without a key.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or "django-insecure-dev-only-do-not-use-in-production"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "rest_framework",
    "corsheaders",
    "django_filters",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    # Local apps
    "apps.users",
    "apps.schools",
    "apps.staff",
    "apps.students",
    "apps.academics",
    "apps.attendance",
    "apps.finance",
    "apps.communication",
    "apps.reports",
    "apps.hr",
    "apps.registry",
    "apps.departments",
    "apps.files",
    "apps.workflows",
    "apps.notifications",
    "apps.inspection",
    "apps.co_curricular",
    "apps.french",
    "apps.infrastructure",
    "apps.library",
    "apps.e_learning",
    "apps.wellness",
    "apps.alumni",
    "apps.assets",
    "apps.discipline",
    "apps.timetable",
    "apps.transport",
    "apps.cpd",
    "apps.audit",
    "apps.parent_teacher",
    "apps.analytics",
    "apps.data_import_export",
    "apps.mail_workflow",
    "apps.predictive_analytics",
    "apps.chatbot",
    "apps.blockchain_cert",
    "apps.multilingual",
    "apps.gamification",
    "apps.push_notifications",
    "apps.iot_dashboard",
    "apps.benchmarking",
    "apps.report_card_gen",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "config.middleware.SessionTrackingMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 12}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
    "EXCEPTION_HANDLER": "config.exceptions.custom_exception_handler",
}

# JWT Settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.environ.get("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", "30"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.environ.get("JWT_REFRESH_TOKEN_LIFETIME_DAYS", "7"))),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://ediv-portal.onrender.com",
    "https://ediv-frontend-static.onrender.com",
]
CORS_ALLOW_CREDENTIALS = True

# Celery (optional - requires Redis/RabbitMQ)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "")

# Wire django_celery_beat only when installed (absent on Render-free tier)
if importlib.util.find_spec("django_celery_beat"):
    INSTALLED_APPS += ["django_celery_beat", "django_celery_results"]
    CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# Elasticsearch (optional - falls back to database search when unavailable)
ELASTICSEARCH_HOSTS = [os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200")]

# Session & Cache - default to database session, overridden in production if Redis available
SESSION_ENGINE = "django.contrib.sessions.backends.db"
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Channels - default to in-memory, overridden in production if Redis available
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# KoraPay
KORA_PAY_PUBLIC_KEY = os.environ.get("KORA_PAY_PUBLIC_KEY", "")
KORA_PAY_SECRET_KEY = os.environ.get("KORA_PAY_SECRET_KEY", "")
KORA_PAY_WEBHOOK_SECRET = os.environ.get("KORA_PAY_WEBHOOK_SECRET", "")
KORA_PAY_API_URL = os.environ.get("KORA_PAY_API_URL", "https://api.korapay.com/merchant/api/v1")

# Frontend URL
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")
