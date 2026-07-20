from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'education_district_iv'),
        'USER': os.environ.get('POSTGRES_USER', 'ediv_user'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'ediv_password'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Debug Toolbar
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']

# CORS
CORS_ALLOW_ALL_ORIGINS = True
