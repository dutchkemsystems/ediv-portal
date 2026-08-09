# Wire Root Django Scaffold to Backend — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use SKILL:subagent-dev (recommended) or SKILL:execute-plan to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire the root-level `ediv_portal/` Django project to import and use the full backend at `backend/`, enabling Render and Docker deployment from the project root.

**Architecture:** Root `ediv_portal/settings.py` adds `backend/` to `sys.path` and imports from `config.settings.production`. Root `urls.py` and `wsgi.py` delegate to the backend modules. Dockerfile and render.yaml are updated to build and run from root.

**Tech Stack:** Django 4.2, DRF, PostgreSQL, Redis, Gunicorn, Docker, Render

---

### Task 1: Wire root settings.py to backend config

**Covers:** [S1]

**Files:**
- Modify: `ediv_portal/settings.py`

- [x] **Step 1: Rewrite ediv_portal/settings.py**

Replace the entire contents of `ediv_portal/settings.py` with:

```python
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
```

- [x] **Step 2: Verify the file is syntactically correct**

Run: `cd C:\educationdistrictivportal && python -c "import ast; ast.parse(open('ediv_portal/settings.py').read()); print('Syntax OK')"`

- [x] **Step 3: Commit**

```bash
git add ediv_portal/settings.py
git commit -m "fix: wire root settings.py to import from backend config.settings.production"
```

---

### Task 2: Wire root urls.py to backend URLs

**Covers:** [S2]

**Files:**
- Modify: `ediv_portal/urls.py`

- [x] **Step 1: Rewrite ediv_portal/urls.py**

Replace the entire contents of `ediv_portal/urls.py` with:

```python
"""
URL configuration for ediv_portal — delegates to backend URL config.
"""
from config.urls import urlpatterns  # noqa: F401

# Re-export the backend's urlpatterns as the root URL configuration
```

- [x] **Step 2: Commit**

```bash
git add ediv_portal/urls.py
git commit -m "fix: wire root urls.py to delegate to backend URL config"
```

---

### Task 3: Verify root wsgi.py is correct

**Covers:** [S2]

**Files:**
- Verify: `ediv_portal/wsgi.py`

- [x] **Step 1: Read and verify ediv_portal/wsgi.py**

The existing `ediv_portal/wsgi.py` should already set `DJANGO_SETTINGS_MODULE` to `ediv_portal.settings`. Verify it contains:

```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ediv_portal.settings')

application = get_wsgi_application()
```

If it doesn't match, update it.

- [x] **Step 2: Commit if changed**

```bash
git add ediv_portal/wsgi.py
git commit -m "fix: ensure wsgi.py points to ediv_portal.settings"
```

---

### Task 4: Update requirements.txt with all dependencies

**Covers:** [S3]

**Files:**
- Modify: `requirements.txt`

- [x] **Step 1: Rewrite requirements.txt**

Replace the entire contents of `requirements.txt` with the Render-compatible dependencies (matching `backend/requirements/render.txt`):

```
Django>=4.2,<5.0
djangorestframework>=3.14,<4.0
django-cors-headers>=4.3,<5.0
django-filter>=23.5,<24.0
psycopg2-binary>=2.9,<3.0
redis>=5.0,<6.0
PyJWT>=2.8,<3.0
python-decouple>=3.8,<4.0
gunicorn>=21.2,<22.0
whitenoise>=6.6,<7.0
openpyxl>=3.1,<4.0
python-docx>=1.1,<2.0
PyPDF2>=3.0,<4.0
djangorestframework-simplejwt[crypto]>=5.3,<6.0
channels>=4.0,<5.0
django-storages>=1.14,<2.0
python-dateutil>=2.8,<3.0
pytz>=2023.3
pyotp>=2.9,<3.0
requests>=2.31,<3.0
sentry-sdk>=1.39,<2.0
django-redis>=5.4,<6.0
reportlab>=4.0,<5.0
pdfplumber>=0.10,<1.0
Pillow>=10.0,<11.0
dj-database-url>=2.1,<3.0
```

Note: `dj-database-url` is added for parsing `DATABASE_URL` in production.

- [x] **Step 2: Commit**

```bash
git add requirements.txt
git commit -m "feat: update root requirements.txt with full Render-compatible deps"
```

---

### Task 5: Update Dockerfile for root-level deployment

**Covers:** [S4]

**Files:**
- Modify: `Dockerfile`

- [x] **Step 1: Rewrite Dockerfile**

Replace the entire contents of `Dockerfile` with:

```dockerfile
FROM python:3.11-slim

ENV PYTHONDICTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=ediv_portal.settings
ENV PYTHONPATH=/app/backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Install and build frontend if present
RUN if [ -d "frontend" ]; then \
    cd frontend && npm install && npm run build && cd ..; \
    fi

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py ensure_admin && python manage.py seed_departments && python manage.py seed_schools && python manage.py seed_users ; gunicorn ediv_portal.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120"]
```

- [x] **Step 2: Commit**

```bash
git add Dockerfile
git commit -m "fix: update Dockerfile for root-level deployment with PYTHONPATH"
```

---

### Task 6: Update render.yaml

**Covers:** [S5]

**Files:**
- Modify: `render.yaml`

- [x] **Step 1: Rewrite render.yaml**

Replace the entire contents of `render.yaml` with:

```yaml
services:
  - type: web
    name: ediv-portal-backend
    runtime: python
    plan: free
    buildCommand: |
      pip install -r requirements.txt
      cd frontend && npm install && npm run build && cd ..
      python manage.py collectstatic --noinput
    startCommand: python manage.py migrate --noinput && python manage.py ensure_admin && python manage.py seed_departments && python manage.py seed_schools && python manage.py seed_users ; gunicorn ediv_portal.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120
    envVars:
      - key: DJANGO_SETTINGS_MODULE
        value: ediv_portal.settings
      - key: PYTHONPATH
        value: /opt/render/project/src/backend
      - key: DATABASE_URL
        fromDatabase:
          name: ediv-db
          property: connectionString
      - key: DJANGO_SECRET_KEY
        generateValue: true
      - key: DJANGO_DEBUG
        value: "False"
      - key: DJANGO_ALLOWED_HOSTS
        value: "ediv-portal-backend.onrender.com,localhost,127.0.0.1"
      - key: REDIS_URL
        sync: false
      - key: KORA_PAY_PUBLIC_KEY
        sync: false
      - key: KORA_PAY_SECRET_KEY
        sync: false
      - key: EMAIL_HOST_USER
        sync: false
      - key: EMAIL_HOST_PASSWORD
        sync: false
      - key: ADMIN_PASSWORD
        sync: false
      - key: FRONTEND_URL
        value: https://ediv-frontend-static.onrender.com
    healthCheckPath: /health/
    autoDeploy: true

databases:
  - name: ediv-db
    plan: free
    databaseName: education_district_iv
    ipAllowList: []
```

- [x] **Step 2: Commit**

```bash
git add render.yaml
git commit -m "fix: update render.yaml for root-level deployment with PYTHONPATH"
```

---

### Task 7: Update docker-compose.yml for dev deployment

**Covers:** [S6]

**Files:**
- Modify: `docker-compose.yml`

- [x] **Step 1: Rewrite docker-compose.yml**

Replace the entire contents of `docker-compose.yml` with:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ediv_db
      POSTGRES_USER: ediv_user
      POSTGRES_PASSWORD: ediv_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ediv_user -d ediv_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      - DJANGO_SETTINGS_MODULE=ediv_portal.settings
      - PYTHONPATH=/app/backend
      - DATABASE_URL=postgresql://ediv_user:ediv_password@db:5432/ediv_db
      - REDIS_URL=redis://redis:6379
      - DJANGO_DEBUG=True
      - DJANGO_SECRET_KEY=dev-secret-key-change-in-production
      - DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

volumes:
  postgres_data:
```

- [x] **Step 2: Commit**

```bash
git add docker-compose.yml
git commit -m "fix: update docker-compose.yml for root-level dev deployment"
```

---

### Task 8: End-to-end verification

**Covers:** [S1, S2, S3, S4, S5, S6]

**Files:** None (verification only)

- [x] **Step 1: Verify Python imports work**

Run: `cd C:\educationdistrictivportal && python -c "import sys; sys.path.insert(0, 'backend'); from config.settings.base import INSTALLED_APPS; print(f'Found {len(INSTALLED_APPS)} installed apps')"`

Expected: `Found 37 installed apps` (approximately)

- [x] **Step 2: Verify settings import chain works**

Run: `cd C:\educationdistrictivportal && python -c "import sys; sys.path.insert(0, 'backend'); from config.settings.production import *; print('Production settings loaded OK')"`

Expected: `Production settings loaded OK`

- [x] **Step 3: Verify syntax of all modified files**

Run: `cd C:\educationdistrictivportal && python -c "import ast; [ast.parse(open(f).read()) for f in ['ediv_portal/settings.py', 'ediv_portal/urls.py', 'ediv_portal/wsgi.py']]; print('All Python files parse OK')"`

Expected: `All Python files parse OK`

- [x] **Step 4: Final commit with all changes**

```bash
git add -A
git commit -m "feat: wire root Django scaffold to backend for deployment

- Root settings.py imports from backend config.settings.production
- Root urls.py delegates to backend URL config
- Requirements.txt updated with full Render-compatible deps
- Dockerfile updated for root-level build with PYTHONPATH
- render.yaml updated for root-level deployment
- docker-compose.yml updated for root-level dev deployment"
```
