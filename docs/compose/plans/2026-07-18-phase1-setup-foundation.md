# Phase 1: Setup & Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use compose:subagent (recommended) or compose:execute to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the complete project infrastructure — Docker environment, Django backend, PostgreSQL, Redis, custom user model with 22+ roles, JWT authentication with MFA, department structure, and admin dashboard.

**Architecture:** Django 4.2+ REST API backend with PostgreSQL 16, Redis 7, Elasticsearch 8. React 18 frontend with Material-UI. Docker Compose for local development. JWT authentication with refresh tokens and MFA support.

**Tech Stack:** Django 4.2, DRF 3.14, PostgreSQL 16, Redis 7, Elasticsearch 8, Celery 5.3, RabbitMQ 3.12, React 18, Redux Toolkit, Material-UI 5, Docker, GitHub Actions.

## Global Constraints

- Python 3.11+, Node.js 18+
- Django 4.2+ LTS
- PostgreSQL 16+
- Redis 7+
- All API responses must be paginated (default 20 items)
- All dates/times stored in UTC
- All models must have created_at, updated_at timestamps
- All strings use UTF-8 encoding
- Password minimum 12 characters with complexity requirements
- JWT access token expiry: 30 minutes, refresh token: 7 days
- Account lockout after 5 failed attempts for 30 minutes

---

## Task 1: Create Project Directory Structure

**Covers:** Project scaffolding

**Files:**
- Create: All directories per specification
- Create: `.gitignore`
- Create: `README.md`

- [ ] **Step 1: Create full directory structure**

```bash
mkdir -p backend/apps/{users,schools,staff,students,academics,attendance,finance,communication,reports,hr/{recruitment,payroll,performance,training,welfare},registry/{documents,filing,correspondence,retention,circulation,archive},departments/{tutor_general,admin_hr,finance,internal_audit,quality_assurance,co_curricular/{french,activities},emis,planning,procurement,public_affairs,schools_admin},files,workflows,notifications,inspection,co_curricular,french,infrastructure,library,e_learning,wellness,alumni,assets,discipline,timetable,transport,cpd,analytics}
mkdir -p backend/config/{settings,}
mkdir -p backend/requirements
mkdir -p backend/templates
mkdir -p backend/static/{css,js,images}
mkdir -p frontend/public
mkdir -p frontend/src/{api,components/{common,auth,dashboard,admin,tutor_general,departments,principal,teacher,student},pages,services,store,utils,styles}
mkdir -p docker
mkdir -p scripts/{seed,migration,backup}
mkdir -p docs
mkdir -p .github/workflows
mkdir -p mobile/src/{screens,components,navigation,services}
```

- [ ] **Step 2: Create .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
*.egg-info/
dist/
build/

# Django
*.log
local_settings.py
db.sqlite3
media/

# Node
node_modules/
frontend/build/
frontend/dist/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Docker
docker-compose.override.yml

# OS
.DS_Store
Thumbs.db

# Celery
celerybeat-schedule
celerybeat.pid
```

- [ ] **Step 3: Create README.md**

```markdown
# Education District IV Portal

Comprehensive digital ecosystem for Education District IV — serving 80,000+ students, 5,000+ staff across 95 schools.

## Quick Start

```bash
# Clone and start
cp .env.example .env
docker-compose up -d

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Access
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/
# Admin: http://localhost:8000/admin/
```

## Development

```bash
# Run tests
docker-compose exec backend pytest

# Run migrations
docker-compose exec backend python manage.py migrate

# Seed data
docker-compose exec backend python manage.py seed_data
```

## Documentation

- [API Documentation](docs/API_DOCS.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [User Manual](docs/USER_MANUAL.md)
```

- [ ] **Step 4: Initialize git and commit**

```bash
git init
git add .
git commit -m "feat: initialize project structure"
```

---

## Task 2: Docker Configuration

**Covers:** Docker setup, infrastructure

**Files:**
- Create: `docker-compose.yml`
- Create: `docker/Dockerfile.backend`
- Create: `docker/Dockerfile.frontend`
- Create: `docker/Dockerfile.nginx`
- Create: `.env.example`

- [ ] **Step 1: Create .env.example**

```env
# Django
DJANGO_SECRET_KEY=your-secret-key-here-change-in-production
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=config.settings.development

# Database
POSTGRES_DB=education_district_iv
POSTGRES_USER=ediv_user
POSTGRES_PASSWORD=ediv_password_change_me
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Elasticsearch
ELASTICSEARCH_URL=http://elasticsearch:9200

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# Celery
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672/
CELERY_RESULT_BACKEND=redis://redis:6379/1

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=30
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# SMS (Twilio)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Frontend
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8000/ws
```

- [ ] **Step 2: Create docker-compose.yml**

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: ediv_postgres
    restart: unless-stopped
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=${POSTGRES_DB:-education_district_iv}
      - POSTGRES_USER=${POSTGRES_USER:-ediv_user}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-ediv_password}
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-ediv_user} -d ${POSTGRES_DB:-education_district_iv}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: ediv_redis
    restart: unless-stopped
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  elasticsearch:
    image: elasticsearch:8.11.0
    container_name: ediv_elasticsearch
    restart: unless-stopped
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5

  rabbitmq:
    image: rabbitmq:3.12-management-alpine
    container_name: ediv_rabbitmq
    restart: unless-stopped
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    ports:
      - "5672:5672"
      - "15672:15672"
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "check_port_connectivity"]
      interval: 30s
      timeout: 10s
      retries: 5

  backend:
    build:
      context: ../backend
      dockerfile: ../docker/Dockerfile.backend
    container_name: ediv_backend
    restart: unless-stopped
    command: sh -c "python manage.py migrate &&
                    python manage.py collectstatic --noinput &&
                    python manage.py runserver 0.0.0.0:8000"
    volumes:
      - ../backend:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    env_file:
      - ../.env
    environment:
      - POSTGRES_HOST=postgres
      - REDIS_URL=redis://redis:6379/0
      - ELASTICSEARCH_URL=http://elasticsearch:9200
      - CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672/
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      elasticsearch:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy

  celery_worker:
    build:
      context: ../backend
      dockerfile: ../docker/Dockerfile.backend
    container_name: ediv_celery_worker
    restart: unless-stopped
    command: celery -A config worker -l info
    volumes:
      - ../backend:/app
    env_file:
      - ../.env
    environment:
      - POSTGRES_HOST=postgres
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672/
    depends_on:
      - backend
      - rabbitmq

  celery_beat:
    build:
      context: ../backend
      dockerfile: ../docker/Dockerfile.backend
    container_name: ediv_celery_beat
    restart: unless-stopped
    command: celery -A config beat -l info
    volumes:
      - ../backend:/app
    env_file:
      - ../.env
    environment:
      - POSTGRES_HOST=postgres
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672/
    depends_on:
      - backend
      - rabbitmq

  frontend:
    build:
      context: ../frontend
      dockerfile: ../docker/Dockerfile.frontend
    container_name: ediv_frontend
    restart: unless-stopped
    volumes:
      - ../frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000/api
    depends_on:
      - backend

  nginx:
    image: nginx:1.24-alpine
    container_name: ediv_nginx
    restart: unless-stopped
    volumes:
      - ../docker/nginx.conf:/etc/nginx/conf.d/default.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  redis_data:
  elasticsearch_data:
  rabbitmq_data:
  static_volume:
  media_volume:
```

- [ ] **Step 3: Create docker/Dockerfile.backend**

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ .
RUN pip install --no-cache-dir -r base.txt

COPY . .

EXPOSE 8000
```

- [ ] **Step 4: Create docker/Dockerfile.frontend**

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000
CMD ["npm", "start"]
```

- [ ] **Step 5: Create docker/nginx.conf**

```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:3000;
}

server {
    listen 80;
    server_name localhost;

    client_max_body_size 100M;

    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /admin/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /app/staticfiles/;
    }

    location /media/ {
        alias /app/media/;
    }

    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

- [ ] **Step 6: Commit Docker configuration**

```bash
git add .
git commit -m "feat: add Docker configuration with PostgreSQL, Redis, Elasticsearch, RabbitMQ"
```

---

## Task 3: Django Project Initialization

**Covers:** Django project setup

**Files:**
- Create: `backend/manage.py`
- Create: `backend/config/__init__.py`
- Create: `backend/config/settings/__init__.py`
- Create: `backend/config/settings/base.py`
- Create: `backend/config/settings/development.py`
- Create: `backend/config/settings/production.py`
- Create: `backend/config/urls.py`
- Create: `backend/config/celery.py`
- Create: `backend/requirements/base.txt`
- Create: `backend/requirements/dev.txt`
- Create: `backend/requirements/prod.txt`

- [ ] **Step 1: Create requirements/base.txt**

```
Django>=4.2,<5.0
djangorestframework>=3.14,<4.0
django-cors-headers>=4.3,<5.0
django-filter>=23.5,<24.0
psycopg2-binary>=2.9,<3.0
redis>=5.0,<6.0
celery>=5.3,<6.0
django-celery-beat>=2.5,<3.0
django-celery-results>=2.5,<3.0
elasticsearch-dsl>=8.11,<9.0
django-elasticsearch-dsl>=8.0,<9.0
PyJWT>=2.8,<3.0
django-rest-framework-simplejwt>=5.3,<6.0
python-decouple>=3.8,<4.0
gunicorn>=21.2,<22.0
whitenoise>=6.6,<7.0
Pillow>=10.1,<11.0
openpyxl>=3.1,<4.0
python-docx>=1.1,<2.0
PyPDF2>=3.0,<4.0
djangorestframework-simplejwt[crypto]>=5.3,<6.0
channels>=4.0,<5.0
channels-redis>=4.2,<5.0
django-storages>=1.14,<2.0
boto3>=1.34,<2.0
python-dateutil>=2.8,<3.0
pytz>=2023.3
```

- [ ] **Step 2: Create requirements/dev.txt**

```
-r base.txt
pytest-django>=4.7,<5.0
pytest-cov>=4.1,<5.0
factory-boy>=3.3,<4.0
faker>=20.1,<21.0
django-debug-toolbar>=4.2,<5.0
django-silk>=5.1,<6.0
flake8>=7.0,<8.0
black>=24.0,<25.0
isort>=5.13,<6.0
mypy>=1.8,<2.0
django-stubs>=4.4,<5.0
```

- [ ] **Step 3: Create requirements/prod.txt**

```
-r base.txt
sentry-sdk>=1.39,<2.0
django-redis>=5.4,<6.0
```

- [ ] **Step 4: Create backend/manage.py**

```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
```

- [ ] **Step 5: Create backend/config/__init__.py**

```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

- [ ] **Step 6: Create backend/config/celery.py**

```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
```

- [ ] **Step 7: Create backend/config/settings/base.py**

```python
import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-change-this-in-production')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'corsheaders',
    'django_filters',
    'django_celery_beat',
    'django_celery_results',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'channels',
    # Local apps
    'apps.users',
    'apps.schools',
    'apps.staff',
    'apps.students',
    'apps.academics',
    'apps.attendance',
    'apps.finance',
    'apps.communication',
    'apps.reports',
    'apps.hr',
    'apps.registry',
    'apps.departments',
    'apps.files',
    'apps.workflows',
    'apps.notifications',
    'apps.inspection',
    'apps.co_curricular',
    'apps.french',
    'apps.infrastructure',
    'apps.library',
    'apps.e_learning',
    'apps.wellness',
    'apps.alumni',
    'apps.assets',
    'apps.discipline',
    'apps.timetable',
    'apps.transport',
    'apps.cpd',
    'apps.analytics',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

AUTH_USER_MODEL = 'users.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    'EXCEPTION_HANDLER': 'config.exceptions.custom_exception_handler',
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.environ.get('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', 30))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.environ.get('JWT_REFRESH_TOKEN_LIFETIME_DAYS', 7))),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# CORS
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]
CORS_ALLOW_CREDENTIALS = True

# Celery
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672/')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [os.environ.get('REDIS_URL', 'redis://localhost:6379/0')],
        },
    },
}

# Session
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    }
}

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

- [ ] **Step 8: Create backend/config/settings/__init__.py**

```python
```

- [ ] **Step 9: Create backend/config/settings/development.py**

```python
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
```

- [ ] **Step 10: Create backend/config/settings/production.py**

```python
from .base import *

DEBUG = False

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        'CONN_MAX_AGE': 600,
    }
}

# Security
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'

# WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

- [ ] **Step 11: Create backend/config/urls.py**

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/schools/', include('apps.schools.urls')),
    path('api/staff/', include('apps.staff.urls')),
    path('api/students/', include('apps.students.urls')),
    path('api/academics/', include('apps.academics.urls')),
    path('api/attendance/', include('apps.attendance.urls')),
    path('api/finance/', include('apps.finance.urls')),
    path('api/communication/', include('apps.communication.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/hr/', include('apps.hr.urls')),
    path('api/registry/', include('apps.registry.urls')),
    path('api/departments/', include('apps.departments.urls')),
    path('api/files/', include('apps.files.urls')),
    path('api/workflows/', include('apps.workflows.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/inspection/', include('apps.inspection.urls')),
    path('api/co-curricular/', include('apps.co_curricular.urls')),
    path('api/french/', include('apps.french.urls')),
    path('api/infrastructure/', include('apps.infrastructure.urls')),
    path('api/library/', include('apps.library.urls')),
    path('api/e-learning/', include('apps.e_learning.urls')),
    path('api/wellness/', include('apps.wellness.urls')),
    path('api/alumni/', include('apps.alumni.urls')),
    path('api/assets/', include('apps.assets.urls')),
    path('api/discipline/', include('apps.discipline.urls')),
    path('api/timetable/', include('apps.timetable.urls')),
    path('api/transport/', include('apps.transport.urls')),
    path('api/cpd/', include('apps.cpd.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

- [ ] **Step 12: Create backend/config/exceptions.py**

```python
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        response.data = {
            'success': False,
            'error': {
                'status_code': response.status_code,
                'message': response.data,
            }
        }
    else:
        response = Response({
            'success': False,
            'error': {
                'status_code': 500,
                'message': str(exc),
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response
```

- [ ] **Step 13: Create placeholder __init__.py files**

```bash
touch backend/apps/users/__init__.py
touch backend/apps/schools/__init__.py
touch backend/apps/staff/__init__.py
touch backend/apps/students/__init__.py
touch backend/apps/academics/__init__.py
touch backend/apps/attendance/__init__.py
touch backend/apps/finance/__init__.py
touch backend/apps/communication/__init__.py
touch backend/apps/reports/__init__.py
touch backend/apps/hr/__init__.py
touch backend/apps/registry/__init__.py
touch backend/apps/departments/__init__.py
touch backend/apps/files/__init__.py
touch backend/apps/workflows/__init__.py
touch backend/apps/notifications/__init__.py
touch backend/apps/inspection/__init__.py
touch backend/apps/co_curricular/__init__.py
touch backend/apps/french/__init__.py
touch backend/apps/infrastructure/__init__.py
touch backend/apps/library/__init__.py
touch backend/apps/e_learning/__init__.py
touch backend/apps/wellness/__init__.py
touch backend/apps/alumni/__init__.py
touch backend/apps/assets/__init__.py
touch backend/apps/discipline/__init__.py
touch backend/apps/timetable/__init__.py
touch backend/apps/transport/__init__.py
touch backend/apps/cpd/__init__.py
touch backend/apps/analytics/__init__.py
touch backend/apps/__init__.py
```

- [ ] **Step 14: Commit Django project**

```bash
git add .
git commit -m "feat: initialize Django project with settings, URLs, and Celery"
```

---

## Task 4: Custom User Model with All Roles

**Covers:** Authentication, user management

**Files:**
- Create: `backend/apps/users/models.py`
- Create: `backend/apps/users/managers.py`
- Create: `backend/apps/users/serializers.py`
- Create: `backend/apps/users/views.py`
- Create: `backend/apps/users/urls.py`
- Create: `backend/apps/users/admin.py`
- Create: `backend/apps/users/tests.py`

- [ ] **Step 1: Create users/managers.py**

```python
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'SYSADMIN')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)
```

- [ ] **Step 2: Create users/models.py**

```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinLengthValidator
from .managers import UserManager


class User(AbstractUser):
    """Custom user model with role-based access control."""
    
    class Role(models.TextChoices):
        SYSADMIN = 'SYSADMIN', 'System Administrator'
        TG = 'TG', 'Tutor General'
        PS = 'PS', 'Permanent Secretary'
        HR = 'HR', 'Admin & HR Head'
        FIN = 'FIN', 'Finance Director'
        AUDIT = 'AUDIT', 'Internal Audit Head'
        QA = 'QA', 'Quality Assurance Head'
        CC = 'CC', 'Co-Curricular Head'
        EMIS = 'EMIS', 'EMIS Head'
        PLAN = 'PLAN', 'Planning Head'
        PROC = 'PROC', 'Procurement Head'
        PA = 'PA', 'Public Affairs Head'
        SA = 'SA', 'Schools Admin Head'
        FRENCH = 'FRENCH', 'French Unit Head'
        REG = 'REG', 'Registry Head'
        PRI = 'PRI', 'Principal'
        VP = 'VP', 'Vice Principal'
        TCH = 'TCH', 'Teacher'
        STD = 'STD', 'Student'
        PAR = 'PAR', 'Parent'
        REG_OFF = 'REG_OFF', 'Registry Officer'
        SA_OFF = 'SA_OFF', 'School Admin Officer'
    
    username = None
    email = models.EmailField('email address', unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STD)
    phone_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=32, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']
    
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
    
    @property
    def is_department_head(self):
        return self.role in ['HR', 'FIN', 'AUDIT', 'QA', 'CC', 'EMIS', 'PLAN', 'PROC', 'PA', 'SA', 'FRENCH', 'REG']
    
    @property
    def is_school_staff(self):
        return self.role in ['PRI', 'VP', 'TCH', 'SA_OFF']
    
    @property
    def is_head_office_staff(self):
        return self.role in ['TG', 'PS', 'HR', 'FIN', 'AUDIT', 'QA', 'CC', 'EMIS', 'PLAN', 'PROC', 'PA', 'SA', 'FRENCH', 'REG', 'REG_OFF']
    
    def can_access_module(self, module):
        """Check if user can access a specific module based on role."""
        permissions = {
            'dashboard': ['SYSADMIN', 'TG', 'PS', 'HR', 'FIN', 'AUDIT', 'QA', 'CC', 'EMIS', 'PLAN', 'PROC', 'PA', 'SA', 'FRENCH', 'REG', 'PRI', 'VP', 'TCH', 'STD', 'PAR'],
            'registry': ['SYSADMIN', 'TG', 'PS', 'HR', 'FIN', 'AUDIT', 'QA', 'CC', 'EMIS', 'PLAN', 'PROC', 'PA', 'SA', 'FRENCH', 'REG', 'REG_OFF', 'PRI', 'VP', 'TCH', 'STD', 'PAR'],
            'hr': ['SYSADMIN', 'TG', 'PS', 'HR'],
            'finance': ['SYSADMIN', 'TG', 'PS', 'FIN'],
            'qa': ['SYSADMIN', 'TG', 'PS', 'QA'],
            'academics': ['SYSADMIN', 'TG', 'PS', 'PRI', 'VP', 'TCH', 'STD', 'PAR'],
            'attendance': ['SYSADMIN', 'TG', 'PS', 'PRI', 'VP', 'TCH', 'STD', 'PAR'],
            'co_curricular': ['SYSADMIN', 'TG', 'PS', 'CC', 'PRI', 'VP', 'TCH', 'STD'],
            'reports': ['SYSADMIN', 'TG', 'PS', 'HR', 'FIN', 'AUDIT', 'QA', 'CC', 'EMIS', 'PLAN', 'PROC', 'PA', 'SA', 'FRENCH', 'REG', 'PRI', 'VP', 'TCH', 'STD', 'PAR'],
        }
        return module in permissions and self.role in permissions[module]
```

- [ ] **Step 3: Create users/serializers.py**

```python
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'role', 
                  'phone_number', 'is_active', 'mfa_enabled', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'phone_number', 'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class MFAEnableSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)


class MFALoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    mfa_code = serializers.CharField(max_length=6)
```

- [ ] **Step 4: Create users/views.py**

```python
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import (
    UserSerializer, UserCreateSerializer, 
    ChangePasswordSerializer, LoginSerializer
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
        
        user = authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        if user is None:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {'error': 'Account is disabled'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if user.failed_login_attempts >= 5:
            return Response(
                {'error': 'Account is locked. Try again later.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
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
```

- [ ] **Step 5: Create users/urls.py**

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, AuthViewSet

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('', include(router.urls)),
]
```

- [ ] **Step 6: Create users/admin.py**

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Roles & Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Security', {'fields': ('mfa_enabled', 'mfa_secret', 'failed_login_attempts', 'locked_until', 'last_login_ip')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )
```

- [ ] **Step 7: Create users/tests.py**

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!@#',
            first_name='Test',
            last_name='User',
            role='TCH'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'TCH')
        self.assertTrue(user.check_password('TestPass123!@#'))
    
    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='AdminPass123!@#'
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.role, 'SYSADMIN')
    
    def test_user_str(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!@#',
            first_name='Test',
            last_name='User',
            role='TCH'
        )
        self.assertEqual(str(user), 'Test User (TCH)')


class AuthViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!@#',
            first_name='Test',
            last_name='User',
            role='TCH'
        )
    
    def test_login_success(self):
        response = self.client.post('/api/users/auth/', {
            'email': 'test@example.com',
            'password': 'TestPass123!@#'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_invalid_credentials(self):
        response = self.client.post('/api/users/auth/', {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post('/api/users/auth/', {
            'email': 'test@example.com',
            'password': 'TestPass123!@#'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserViewSetTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='AdminPass123!@#',
            first_name='Admin',
            last_name='User',
            role='SYSADMIN'
        )
        self.teacher = User.objects.create_user(
            email='teacher@example.com',
            password='TeacherPass123!@#',
            first_name='Teacher',
            last_name='User',
            role='TCH'
        )
        self.admin_token = RefreshToken.for_user(self.admin)
        self.teacher_token = RefreshToken.for_user(self.teacher)
    
    def test_list_users_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token.access_token}')
        response = self.client.get('/api/users/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_users_teacher(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.teacher_token.access_token}')
        response = self.client.get('/api/users/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token.access_token}')
        response = self.client.post('/api/users/users/', {
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'TCH',
            'password': 'NewPass123!@#',
            'password_confirm': 'NewPass123!@#'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
```

- [ ] **Step 8: Commit User model**

```bash
git add .
git commit -m "feat: add custom User model with 22 roles and JWT authentication"
```

---

## Task 5: Department Structure

**Covers:** Department management

**Files:**
- Create: `backend/apps/departments/models.py`
- Create: `backend/apps/departments/serializers.py`
- Create: `backend/apps/departments/views.py`
- Create: `backend/apps/departments/urls.py`
- Create: `backend/apps/departments/admin.py`

- [ ] **Step 1: Create departments/models.py**

```python
from django.db import models
from django.conf import settings


class DepartmentCategory(models.TextChoices):
    CORE = 'CORE', 'Core Department'
    SUPPORT = 'SUPPORT', 'Support Unit'


class Department(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    category = models.CharField(max_length=10, choices=DepartmentCategory.choices)
    description = models.TextField(blank=True)
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_departments'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'departments'
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Unit(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='units')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_units'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['department', 'code']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.department.name} - {self.name}"
```

- [ ] **Step 2: Create departments/serializers.py**

```python
from rest_framework import serializers
from .models import Department, Unit


class UnitSerializer(serializers.ModelSerializer):
    head_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Unit
        fields = ['id', 'name', 'code', 'description', 'head', 'head_name', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_head_name(self, obj):
        if obj.head:
            return obj.head.get_full_name()
        return None


class DepartmentSerializer(serializers.ModelSerializer):
    head_name = serializers.SerializerMethodField()
    units = UnitSerializer(many=True, read_only=True)
    sub_departments = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'category', 'description', 'head', 'head_name', 
                  'parent', 'units', 'sub_departments', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_head_name(self, obj):
        if obj.head:
            return obj.head.get_full_name()
        return None
    
    def get_sub_departments(self, obj):
        sub_depts = obj.sub_departments.filter(is_active=True)
        return DepartmentListSerializer(sub_depts, many=True).data


class DepartmentListSerializer(serializers.ModelSerializer):
    head_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'category', 'head_name', 'is_active']
    
    def get_head_name(self, obj):
        if obj.head:
            return obj.head.get_full_name()
        return None
```

- [ ] **Step 3: Create departments/views.py**

```python
from rest_framework import viewsets, permissions
from .models import Department, Unit
from .serializers import DepartmentSerializer, DepartmentListSerializer, UnitSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DepartmentListSerializer
        return DepartmentSerializer


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.select_related('department', 'head').all()
    serializer_class = UnitSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['department', 'is_active']
    search_fields = ['name', 'code']
```

- [ ] **Step 4: Create departments/urls.py**

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, UnitViewSet

router = DefaultRouter()
router.register('departments', DepartmentViewSet)
router.register('units', UnitViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

- [ ] **Step 5: Create departments/admin.py**

```python
from django.contrib import admin
from .models import Department, Unit


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'category', 'head', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'code']


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'head', 'is_active']
    list_filter = ['department', 'is_active']
    search_fields = ['name', 'code']
```

- [ ] **Step 6: Commit Department models**

```bash
git add .
git commit -m "feat: add Department and Unit models with hierarchy"
```

---

## Task 6: School Model

**Covers:** School management

**Files:**
- Create: `backend/apps/schools/models.py`
- Create: `backend/apps/schools/serializers.py`
- Create: `backend/apps/schools/views.py`
- Create: `backend/apps/schools/urls.py`
- Create: `backend/apps/schools/admin.py`

- [ ] **Step 1: Create schools/models.py**

```python
from django.db import models
from django.conf import settings


class SchoolType(models.TextChoices):
    JUNIOR = 'JUNIOR', 'Junior Secondary School'
    SENIOR = 'SENIOR', 'Senior Secondary School'


class LocalGovernmentArea(models.TextChoices):
    APAPA = 'APAPA', 'Apapa'
    MAINLAND = 'MAINLAND', 'Mainland'
    SURULERE = 'SURULERE', 'Surulere'


class School(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    school_type = models.CharField(max_length=10, choices=SchoolType.choices)
    lga = models.CharField(max_length=20, choices=LocalGovernmentArea.choices)
    address = models.TextField()
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    principal = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='schools_as_principal'
    )
    vice_principal = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='schools_as_vice_principal'
    )
    established_date = models.DateField(null=True, blank=True)
    student_capacity = models.IntegerField(default=0)
    current_enrollment = models.IntegerField(default=0)
    number_of_classrooms = models.IntegerField(default=0)
    number_of_staff = models.IntegerField(default=0)
    has_science_lab = models.BooleanField(default=False)
    has_computer_lab = models.BooleanField(default=False)
    has_library = models.BooleanField(default=False)
    has_sports_field = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['lga', 'school_type', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['school_type']),
            models.Index(fields=['lga']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def occupancy_rate(self):
        if self.student_capacity > 0:
            return (self.current_enrollment / self.student_capacity) * 100
        return 0


class SchoolAcademicYear(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='academic_years')
    year = models.CharField(max_length=9)  # e.g., "2024/2025"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['school', 'year']
        ordering = ['-year']
    
    def __str__(self):
        return f"{self.school.name} - {self.year}"
```

- [ ] **Step 2: Create schools/serializers.py**

```python
from rest_framework import serializers
from .models import School, SchoolAcademicYear


class SchoolAcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolAcademicYear
        fields = ['id', 'year', 'start_date', 'end_date', 'is_current', 'created_at']
        read_only_fields = ['id', 'created_at']


class SchoolSerializer(serializers.ModelSerializer):
    principal_name = serializers.SerializerMethodField()
    vice_principal_name = serializers.SerializerMethodField()
    academic_years = SchoolAcademicYearSerializer(many=True, read_only=True)
    occupancy_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = School
        fields = ['id', 'name', 'code', 'school_type', 'lga', 'address', 'phone', 'email',
                  'website', 'principal', 'principal_name', 'vice_principal', 'vice_principal_name',
                  'established_date', 'student_capacity', 'current_enrollment', 'number_of_classrooms',
                  'number_of_staff', 'has_science_lab', 'has_computer_lab', 'has_library',
                  'has_sports_field', 'latitude', 'longitude', 'is_active', 'occupancy_rate',
                  'academic_years', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_principal_name(self, obj):
        if obj.principal:
            return obj.principal.get_full_name()
        return None
    
    def get_vice_principal_name(self, obj):
        if obj.vice_principal:
            return obj.vice_principal.get_full_name()
        return None


class SchoolListSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['id', 'name', 'code', 'school_type', 'lga', 'current_enrollment', 'is_active']
```

- [ ] **Step 3: Create schools/views.py**

```python
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import School, SchoolAcademicYear
from .serializers import SchoolSerializer, SchoolListSerializer, SchoolAcademicYearSerializer


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.select_related('principal', 'vice_principal').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['school_type', 'lga', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SchoolListSerializer
        return SchoolSerializer


class SchoolAcademicYearViewSet(viewsets.ModelViewSet):
    serializer_class = SchoolAcademicYearSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SchoolAcademicYear.objects.filter(school_id=self.kwargs['school_pk'])
    
    def perform_create(self, serializer):
        serializer.save(school_id=self.kwargs['school_pk'])
```

- [ ] **Step 4: Create schools/urls.py**

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SchoolViewSet, SchoolAcademicYearViewSet

router = DefaultRouter()
router.register('schools', SchoolViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('schools/<int:school_pk>/academic-years/', SchoolAcademicYearViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('schools/<int:school_pk>/academic-years/<int:pk>/', SchoolAcademicYearViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    })),
]
```

- [ ] **Step 5: Create schools/admin.py**

```python
from django.contrib import admin
from .models import School, SchoolAcademicYear


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'school_type', 'lga', 'principal', 'current_enrollment', 'is_active']
    list_filter = ['school_type', 'lga', 'is_active']
    search_fields = ['name', 'code']
    raw_id_fields = ['principal', 'vice_principal']


@admin.register(SchoolAcademicYear)
class SchoolAcademicYearAdmin(admin.ModelAdmin):
    list_display = ['school', 'year', 'start_date', 'end_date', 'is_current']
    list_filter = ['is_current']
```

- [ ] **Step 6: Commit School models**

```bash
git add .
git commit -m "feat: add School model with 95 schools support and LGA tracking"
```

---

## Task 7: CI/CD Pipeline

**Covers:** GitHub Actions, CI/CD

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `.github/workflows/deploy.yml`
- Create: `.github/workflows/security_scan.yml`

- [ ] **Step 1: Create .github/workflows/ci.yml**

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: ediv_user
          POSTGRES_PASSWORD: ediv_password
          POSTGRES_DB: education_district_iv_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Cache pip
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements/dev.txt') }}
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements/dev.txt
      
      - name: Run tests
        env:
          DJANGO_SETTINGS_MODULE: config.settings.development
          POSTGRES_HOST: localhost
          POSTGRES_DB: education_district_iv_test
          POSTGRES_USER: ediv_user
          POSTGRES_PASSWORD: ediv_password
          REDIS_URL: redis://localhost:6379/0
          CELERY_BROKER_URL: redis://localhost:6379/1
        run: |
          cd backend
          python manage.py test --verbosity=2
      
      - name: Run linting
        run: |
          cd backend
          flake8 . --max-line-length=120
          black --check .
          isort --check-only .
```

- [ ] **Step 2: Create .github/workflows/deploy.yml**

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    needs: [test]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to production
        run: |
          echo "Deployment steps would go here"
          echo "Configure for your deployment target (AWS, Azure, etc.)"
```

- [ ] **Step 3: Create .github/workflows/security_scan.yml**

```yaml
name: Security Scan

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  push:
    branches: [main]

jobs:
  security:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Run security scan
        run: |
          echo "Security scan steps would go here"
          echo "Configure for your security scanning tools"
```

- [ ] **Step 4: Commit CI/CD**

```bash
git add .
git commit -m "feat: add GitHub Actions CI/CD pipelines"
```

---

## Task 8: Database Migrations and Initial Data

**Covers:** Database setup, seed data

**Files:**
- Create: `backend/apps/departments/management/commands/seed_departments.py`
- Create: `backend/apps/schools/management/commands/seed_schools.py`
- Create: `backend/apps/users/management/commands/seed_users.py`

- [ ] **Step 1: Create department seeding command**

```bash
mkdir -p backend/apps/departments/management/commands
touch backend/apps/departments/management/__init__.py
touch backend/apps/departments/management/commands/__init__.py
```

```python
# backend/apps/departments/management/commands/seed_departments.py
from django.core.management.base import BaseCommand
from apps.departments.models import Department, Unit


class Command(BaseCommand):
    help = 'Seed departments and units'
    
    def handle(self, *args, **options):
        departments = [
            {'name': 'Administration & Human Resources', 'code': 'ADMIN_HR', 'category': 'CORE', 'description': 'Oversees all administrative and staff-related affairs'},
            {'name': 'Finance Department', 'code': 'FINANCE', 'category': 'CORE', 'description': 'Handles all financial services and monetary matters'},
            {'name': 'Internal Audit Unit', 'code': 'AUDIT', 'category': 'CORE', 'description': 'Oversees staff audit, compliance, and liaises with State Auditor General'},
            {'name': 'Quality Assurance Unit', 'code': 'QA', 'category': 'CORE', 'description': 'Specializes in school inspection and reporting'},
            {'name': 'Co-Curricular Science Department', 'code': 'CO_CURRICULAR', 'category': 'CORE', 'description': 'Oversees extra-curricular activities, sciences, and French'},
            {'name': 'EMIS Unit', 'code': 'EMIS', 'category': 'SUPPORT', 'description': 'Education Management Information System'},
            {'name': 'Planning Unit', 'code': 'PLANNING', 'category': 'SUPPORT', 'description': 'Strategic planning and policy development'},
            {'name': 'Procurement Unit', 'code': 'PROCUREMENT', 'category': 'SUPPORT', 'description': 'Procurement planning and management'},
            {'name': 'Public Affairs Unit', 'code': 'PUBLIC_AFFAIRS', 'category': 'SUPPORT', 'description': 'Public relations and communications'},
            {'name': 'Schools Administration Department', 'code': 'SCHOOLS_ADMIN', 'category': 'SUPPORT', 'description': 'School supervision and administration'},
            {'name': 'Registry', 'code': 'REGISTRY', 'category': 'SUPPORT', 'description': 'Document and file management'},
        ]
        
        for dept_data in departments:
            dept, created = Department.objects.get_or_create(
                code=dept_data['code'],
                defaults=dept_data
            )
            if created:
                self.stdout.write(f'Created department: {dept.name}')
            else:
                self.stdout.write(f'Department already exists: {dept.name}')
        
        units = [
            {'department_code': 'CO_CURRICULAR', 'name': 'French Unit', 'code': 'FRENCH'},
            {'department_code': 'CO_CURRICULAR', 'name': 'Sports Unit', 'code': 'SPORTS'},
            {'department_code': 'CO_CURRICULAR', 'name': 'Cultural Activities', 'code': 'CULTURAL'},
            {'department_code': 'ADMIN_HR', 'name': 'Recruitment', 'code': 'RECRUITMENT'},
            {'department_code': 'ADMIN_HR', 'name': 'Payroll', 'code': 'PAYROLL'},
            {'department_code': 'ADMIN_HR', 'name': 'Performance', 'code': 'PERFORMANCE'},
            {'department_code': 'ADMIN_HR', 'name': 'Training', 'code': 'TRAINING'},
            {'department_code': 'ADMIN_HR', 'name': 'Welfare', 'code': 'WELFARE'},
            {'department_code': 'REGISTRY', 'name': 'Documents', 'code': 'DOCUMENTS'},
            {'department_code': 'REGISTRY', 'name': 'Filing', 'code': 'FILING'},
            {'department_code': 'REGISTRY', 'name': 'Correspondence', 'code': 'CORRESPONDENCE'},
            {'department_code': 'REGISTRY', 'name': 'Retention', 'code': 'RETENTION'},
            {'department_code': 'REGISTRY', 'name': 'Circulation', 'code': 'CIRCULATION'},
            {'department_code': 'REGISTRY', 'name': 'Archive', 'code': 'ARCHIVE'},
        ]
        
        for unit_data in units:
            department = Department.objects.get(code=unit_data['department_code'])
            unit, created = Unit.objects.get_or_create(
                department=department,
                code=unit_data['code'],
                defaults={'name': unit_data['name']}
            )
            if created:
                self.stdout.write(f'Created unit: {unit.name}')
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded departments and units'))
```

- [ ] **Step 2: Create user seeding command**

```bash
mkdir -p backend/apps/users/management/commands
touch backend/apps/users/management/__init__.py
touch backend/apps/users/management/commands/__init__.py
```

```python
# backend/apps/users/management/commands/seed_users.py
from django.core.management.base import BaseCommand
from apps.users.models import User


class Command(BaseCommand):
    help = 'Seed initial users'
    
    def handle(self, *args, **options):
        # System Administrator
        if not User.objects.filter(email='admin@ediv.gov.ng').exists():
            User.objects.create_superuser(
                email='admin@ediv.gov.ng',
                password='Admin@12345678',
                first_name='System',
                last_name='Administrator',
                role='SYSADMIN'
            )
            self.stdout.write(self.style.SUCCESS('Created superuser: admin@ediv.gov.ng'))
        
        # Tutor General
        if not User.objects.filter(email='tg@ediv.gov.ng').exists():
            User.objects.create_user(
                email='tg@ediv.gov.ng',
                password='TutorGen@12345',
                first_name='Tutor',
                last_name='General',
                role='TG'
            )
            self.stdout.write(self.style.SUCCESS('Created Tutor General'))
        
        # Department Heads
        dept_heads = [
            ('hr@ediv.gov.ng', 'HR', 'HR Head'),
            ('finance@ediv.gov.ng', 'FIN', 'Finance Director'),
            ('audit@ediv.gov.ng', 'AUDIT', 'Audit Head'),
            ('qa@ediv.gov.ng', 'QA', 'QA Head'),
            ('cc@ediv.gov.ng', 'CC', 'Co-Curricular Head'),
            ('emis@ediv.gov.ng', 'EMIS', 'EMIS Head'),
            ('planning@ediv.gov.ng', 'PLAN', 'Planning Head'),
            ('procurement@ediv.gov.ng', 'PROC', 'Procurement Head'),
            ('pa@ediv.gov.ng', 'PA', 'Public Affairs Head'),
            ('sa@ediv.gov.ng', 'SA', 'Schools Admin Head'),
            ('french@ediv.gov.ng', 'FRENCH', 'French Unit Head'),
            ('registry@ediv.gov.ng', 'REG', 'Registry Head'),
        ]
        
        for email, role, name in dept_heads:
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(
                    email=email,
                    password='DeptHead@12345',
                    first_name=name.split()[0],
                    last_name=' '.join(name.split()[1:]),
                    role=role
                )
                self.stdout.write(self.style.SUCCESS(f'Created {name}'))
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded users'))
```

- [ ] **Step 3: Run migrations and seed data**

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py seed_departments
python manage.py seed_users
```

- [ ] **Step 4: Commit seed data**

```bash
git add .
git commit -m "feat: add seed data commands for departments and users"
```

---

## Task 9: Frontend React Setup

**Covers:** Frontend project setup

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/src/App.jsx`
- Create: `frontend/src/main.jsx`
- Create: `frontend/src/store/index.js`
- Create: `frontend/src/api/client.js`

- [ ] **Step 1: Create package.json**

```json
{
  "name": "education-district-iv-portal",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0"
  },
  "dependencies": {
    "@emotion/react": "^11.11.0",
    "@emotion/styled": "^11.11.0",
    "@mui/icons-material": "^5.14.0",
    "@mui/material": "^5.14.0",
    "@reduxjs/toolkit": "^1.9.7",
    "axios": "^1.6.0",
    "chart.js": "^4.4.0",
    "react": "^18.2.0",
    "react-chartjs-2": "^5.2.0",
    "react-dom": "^18.2.0",
    "react-redux": "^8.1.3",
    "react-router-dom": "^6.20.0",
    "react-toastify": "^9.1.3"
  },
  "devDependencies": {
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "@vitejs/plugin-react": "^4.2.0",
    "eslint": "^8.53.0",
    "eslint-plugin-react": "^7.33.2",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.5",
    "vite": "^5.0.0"
  }
}
```

- [ ] **Step 2: Create vite.config.js**

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 3: Create frontend/src/main.jsx**

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import App from './App'
import { store } from './store'
import './styles/index.css'

const theme = createTheme({
  palette: {
    primary: {
      main: '#1a237e',
      light: '#534bae',
      dark: '#000051',
    },
    secondary: {
      main: '#f57c00',
      light: '#ffad42',
      dark: '#bb4d00',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Provider store={store}>
      <BrowserRouter>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <App />
        </ThemeProvider>
      </BrowserRouter>
    </Provider>
  </React.StrictMode>,
)
```

- [ ] **Step 4: Create frontend/src/App.jsx**

```jsx
import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useSelector } from 'react-redux'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Layout from './components/common/Layout'

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useSelector((state) => state.auth)
  return isAuthenticated ? children : <Navigate to="/login" />
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout>
              <Dashboard />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}

export default App
```

- [ ] **Step 5: Create frontend/src/store/index.js**

```javascript
import { configureStore } from '@reduxjs/toolkit'
import authReducer from './authSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
  },
})
```

- [ ] **Step 6: Create frontend/src/store/authSlice.js**

```javascript
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../api/client'

export const login = createAsyncThunk(
  'auth/login',
  async ({ email, password }, { rejectWithValue }) => {
    try {
      const response = await api.post('/users/auth/', { email, password })
      localStorage.setItem('access_token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data || { error: 'Login failed' })
    }
  }
)

export const logout = createAsyncThunk('auth/logout', async () => {
  const refreshToken = localStorage.getItem('refresh_token')
  try {
    await api.post('/users/auth/logout/', { refresh: refreshToken })
  } finally {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }
})

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    isAuthenticated: !!localStorage.getItem('access_token'),
    loading: false,
    error: null,
  },
  reducers: {
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false
        state.isAuthenticated = true
        state.user = action.payload.user
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload?.error || 'Login failed'
      })
      .addCase(logout.fulfilled, (state) => {
        state.isAuthenticated = false
        state.user = null
      })
  },
})

export const { clearError } = authSlice.actions
export default authSlice.reducer
```

- [ ] **Step 7: Create frontend/src/api/client.js**

```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        const response = await axios.post('/api/users/auth/refresh/', {
          refresh: refreshToken,
        })
        localStorage.setItem('access_token', response.data.access)
        originalRequest.headers.Authorization = `Bearer ${response.data.access}`
        return api(originalRequest)
      } catch (refreshError) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }
    return Promise.reject(error)
  }
)

export default api
```

- [ ] **Step 8: Create frontend/src/pages/Login.jsx**

```jsx
import React, { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
} from '@mui/material'
import { login, clearError } from '../store/authSlice'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { loading, error } = useSelector((state) => state.auth)

  const handleSubmit = async (e) => {
    e.preventDefault()
    const result = await dispatch(login({ email, password }))
    if (login.fulfilled.match(result)) {
      navigate('/')
    }
  }

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Typography variant="h4" align="center" gutterBottom sx={{ color: '#1a237e' }}>
            Education District IV
          </Typography>
          <Typography variant="h6" align="center" gutterBottom color="text.secondary">
            Portal Login
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => dispatch(clearError())}>
              {error}
            </Alert>
          )}
          
          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              margin="normal"
              required
              autoFocus
            />
            <TextField
              fullWidth
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              margin="normal"
              required
            />
            <Button
              fullWidth
              type="submit"
              variant="contained"
              size="large"
              disabled={loading}
              sx={{ mt: 3, bgcolor: '#1a237e', '&:hover': { bgcolor: '#0d1642' } }}
            >
              {loading ? <CircularProgress size={24} /> : 'Login'}
            </Button>
          </form>
        </Paper>
      </Box>
    </Container>
  )
}

export default Login
```

- [ ] **Step 9: Create frontend/src/pages/Dashboard.jsx**

```jsx
import React from 'react'
import { useSelector } from 'react-redux'
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CardActionArea,
} from '@mui/material'
import {
  School as SchoolIcon,
  People as PeopleIcon,
  Assignment as AssignmentIcon,
  BarChart as BarChartIcon,
} from '@mui/icons-material'

const stats = [
  { title: 'Total Schools', value: '95', icon: <SchoolIcon sx={{ fontSize: 48 }} />, color: '#1a237e' },
  { title: 'Total Students', value: '80,000+', icon: <PeopleIcon sx={{ fontSize: 48 }} />, color: '#f57c00' },
  { title: 'Total Staff', value: '5,000+', icon: <PeopleIcon sx={{ fontSize: 48 }} />, color: '#388e3c' },
  { title: 'Active Files', value: '1,234', icon: <AssignmentIcon sx={{ fontSize: 48 }} />, color: '#d32f2f' },
]

function Dashboard() {
  const { user } = useSelector((state) => state.auth)

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Welcome, {user?.first_name || 'User'}
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Education District IV Portal Dashboard
      </Typography>
      
      <Grid container spacing={3} sx={{ mt: 2 }}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardActionArea>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box>
                      <Typography variant="h4" sx={{ color: stat.color }}>
                        {stat.value}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {stat.title}
                      </Typography>
                    </Box>
                    <Box sx={{ color: stat.color, opacity: 0.3 }}>
                      {stat.icon}
                    </Box>
                  </Box>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>
      
      <Grid container spacing={3} sx={{ mt: 3 }}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <Typography color="text.secondary">
              No recent activity to display.
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Typography color="text.secondary">
              Quick actions will appear here based on your role.
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard
```

- [ ] **Step 10: Create frontend/src/components/common/Layout.jsx**

```jsx
import React, { useState } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import {
  AppBar,
  Box,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Avatar,
  Menu,
  MenuItem,
  Divider,
} from '@mui/material'
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  School as SchoolIcon,
  People as PeopleIcon,
  Assignment as AssignmentIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material'
import { logout } from '../../store/authSlice'

const drawerWidth = 260

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Schools', icon: <SchoolIcon />, path: '/schools' },
  { text: 'Staff', icon: <PeopleIcon />, path: '/staff' },
  { text: 'Students', icon: <PeopleIcon />, path: '/students' },
  { text: 'Registry', icon: <AssignmentIcon />, path: '/registry' },
  { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
]

function Layout({ children }) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const [anchorEl, setAnchorEl] = useState(null)
  const { user } = useSelector((state) => state.auth)
  const dispatch = useDispatch()
  const navigate = useNavigate()

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen)
  }

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget)
  }

  const handleMenuClose = () => {
    setAnchorEl(null)
  }

  const handleLogout = () => {
    dispatch(logout())
    navigate('/login')
  }

  const drawer = (
    <Box>
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="h6" sx={{ color: '#1a237e', fontWeight: 'bold' }}>
          EDIV Portal
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Education District IV
        </Typography>
      </Box>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton onClick={() => { navigate(item.path); setMobileOpen(false) }}>
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  )

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ bgcolor: '#1a237e' }}>
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap sx={{ flexGrow: 1 }}>
            Education District IV Portal
          </Typography>
          <IconButton onClick={handleMenuOpen} sx={{ ml: 2 }}>
            <Avatar sx={{ bgcolor: '#f57c00' }}>
              {user?.first_name?.[0] || 'U'}
            </Avatar>
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem disabled>
              <Typography variant="body2">{user?.email}</Typography>
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout}>
              <ListItemIcon><LogoutIcon fontSize="small" /></ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>
      
      <Box component="nav" sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}>
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
      </Box>
      
      <Box component="main" sx={{ flexGrow: 1, p: 3, width: { sm: `calc(100% - ${drawerWidth}px)` } }}>
        <Toolbar />
        {children}
      </Box>
    </Box>
  )
}

export default Layout
```

- [ ] **Step 11: Create frontend/src/styles/index.css**

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f5f5;
}

::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}
```

- [ ] **Step 12: Create frontend/index.html**

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/x-icon" href="/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="Education District IV Portal - Digital ecosystem for education administration" />
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <title>Education District IV Portal</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

- [ ] **Step 13: Create frontend/manifest.json**

```json
{
  "short_name": "EDIV Portal",
  "name": "Education District IV Portal",
  "icons": [
    {
      "src": "favicon.ico",
      "sizes": "64x64 32x32 24x24 16x16",
      "type": "image/x-icon"
    }
  ],
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#1a237e",
  "background_color": "#ffffff"
}
```

- [ ] **Step 14: Commit frontend setup**

```bash
git add .
git commit -m "feat: add React frontend with Material-UI, Redux, and routing"
```

---

## Task 10: Final Integration and Verification

**Covers:** Integration testing

- [ ] **Step 1: Verify backend starts**

```bash
cd backend
pip install -r requirements/dev.txt
python manage.py check
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

- [ ] **Step 2: Verify frontend starts**

```bash
cd frontend
npm install
npm run dev
```

- [ ] **Step 3: Run all tests**

```bash
cd backend
python manage.py test --verbosity=2
```

- [ ] **Step 4: Final commit**

```bash
git add .
git commit -m "feat: Phase 1 complete - Setup & Foundation"
git tag v1.0.0-phase1
```

---

## Phase 1 Summary

| Component | Status | Files Created |
|-----------|--------|---------------|
| Project Structure | ✅ | Full directory tree |
| Docker Setup | ✅ | docker-compose.yml, Dockerfiles, nginx.conf |
| Django Project | ✅ | settings, urls, celery, exceptions |
| Custom User Model | ✅ | 22 roles, JWT auth, permissions |
| Department Structure | ✅ | 11 departments, 14 units |
| School Model | ✅ | 95 schools support, LGA tracking |
| CI/CD | ✅ | GitHub Actions workflows |
| Frontend | ✅ | React + Material-UI + Redux |
| Seed Data | ✅ | Department and user seeding |

**Next Phase:** Phase 2 - Core Models & Admin (Staff, Students, Academic models)
