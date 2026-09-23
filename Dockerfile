# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
ARG VITE_REGISTRY_AUTO_TASK=true
ENV VITE_REGISTRY_AUTO_TASK=$VITE_REGISTRY_AUTO_TASK
RUN npm run build

# Stage 2: Python backend
FROM python:3.11-slim AS backend

ENV PYTHONDICTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (cached layer)
COPY backend/requirements/ /app/requirements/
RUN pip install --no-cache-dir -r /app/requirements/prod.txt

# Copy backend code
COPY backend/ /app/backend/

# Copy built frontend into backend static serve path
RUN mkdir -p /app/backend/staticfiles/frontend
COPY --from=frontend-builder /app/frontend/dist/ /app/backend/staticfiles/frontend/

# Collect static files
RUN DJANGO_SETTINGS_MODULE=config.settings.production \
    DJANGO_SECRET_KEY=build-time-only \
    python backend/manage.py collectstatic --noinput --no-default-ignore

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["sh", "-c", "cd /app/backend && python manage.py migrate --noinput && python manage.py ensure_admin && python manage.py seed_departments && python manage.py seed_schools && python manage.py seed_users && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120"]
