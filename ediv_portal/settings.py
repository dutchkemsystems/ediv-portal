"""
Django settings for ediv_portal project — wired to backend config.
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Add backend/ to Python path so config.* and apps.* imports work
BACKEND_DIR = str(BASE_DIR / 'backend')
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Set the settings module for the backend config
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

# Import everything from the backend production settings
from config.settings.production import *  # noqa: F401, F403

# Override ROOT_URLCONF to use our root URL config
ROOT_URLCONF = 'ediv_portal.urls'

# Override WSGI application
WSGI_APPLICATION = 'ediv_portal.wsgi.application'

# Recalculate paths relative to root (BASE_DIR is now the project root)
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'
