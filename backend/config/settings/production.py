import logging
import os

import dj_database_url

from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
    if h.strip()
] or [
    "localhost",
    "127.0.0.1",
]

# Production must never run with a default/dev secret key.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise SystemExit("Missing DJANGO_SECRET_KEY environment variable.")

# Get DATABASE_URL from environment
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Use the provided DATABASE_URL
    ssl_require = os.environ.get("DB_SSL_REQUIRE", "True").lower() == "true"
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL, conn_max_age=600, ssl_require=ssl_require
        )
    }
else:
    # Fallback configuration for build time (when DATABASE_URL is not set)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "dummy_db"),
            "USER": os.environ.get("POSTGRES_USER", "dummy_user"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "dummy_password"),
            "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
            "OPTIONS": {
                "sslmode": "require",
            },
        }
    }

# Cache configuration (if Redis is available)
if os.environ.get("REDIS_URL"):
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.environ.get("REDIS_URL"),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }

# Email configuration (SMTP)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL", "EDIV Portal <noreply@ediv.gov.ng>"
)
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", "noreply@ediv.gov.ng")

# Security settings (allow override for plain-HTTP staging/VM deploys)
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "True").lower() == "true"
SESSION_COOKIE_SECURE = (
    os.environ.get("SESSION_COOKIE_SECURE", "True").lower() == "true"
)
CSRF_COOKIE_SECURE = os.environ.get("CSRF_COOKIE_SECURE", "True").lower() == "true"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Gunicorn timeout for cold starts
GUNICORN_TIMEOUT = int(os.environ.get("GUNICORN_TIMEOUT", "180"))

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# ---- Cloudinary file storage (production uploads) ----
CLOUDINARY_URL = os.environ.get("CLOUDINARY_URL")
if CLOUDINARY_URL:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.cloudinary.CloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
    # Limit upload sizes (10MB default, 50MB for large Access DB files)
    FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
    DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
else:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
    # Set upload size limits even without Cloudinary (Django defaults are only 2.5MB)
    FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
    DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
    logging.getLogger(__name__).warning(
        "CLOUDINARY_URL not set — uploads use local filesystem and will be lost on restart."
    )
