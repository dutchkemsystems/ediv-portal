FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=ediv_portal.settings
ENV PYTHONPATH=/app/backend

# Build-time secret so collectstatic can run; runtime env must override with a real key.
ARG DJANGO_SECRET_KEY=django-insecure-build-time-only
ENV DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY

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
