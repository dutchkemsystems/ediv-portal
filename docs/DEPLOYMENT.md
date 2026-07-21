# Education District IV Portal - Deployment Guide

## Prerequisites

- Docker 24+
- Docker Compose 2.20+
- Git
- Domain name (for production)
- SSL certificates (for production)

## Local Development

### Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/education-district-iv-portal.git
cd education-district-iv-portal

# Copy environment file
cp .env.example .env

# Start development server
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/
# Admin: http://localhost:8000/admin/
```

### Development Commands

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Seed data
docker-compose exec backend python manage.py seed_departments
docker-compose exec backend python manage.py seed_users

# Run tests
docker-compose exec backend python manage.py test

# Access Django shell
docker-compose exec backend python manage.py shell

# View logs
docker-compose logs -f backend
```

## Production Deployment

### Step 1: Server Setup

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 2: Configure Environment

```bash
# Copy production environment file
cp .env.production.example .env.production

# Edit with your settings
nano .env.production
```

Required settings:
- `DJANGO_SECRET_KEY` - Generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `POSTGRES_PASSWORD` - Secure database password
- `REDIS_PASSWORD` - Secure Redis password
- `ELASTIC_PASSWORD` - Secure Elasticsearch password
- `RABBITMQ_PASSWORD` - Secure RabbitMQ password

### Step 3: SSL certificates

```bash
# Create SSL directory
mkdir -p docker/ssl

# Copy your certificates
cp /path/to/cert.pem docker/ssl/cert.pem
cp /path/to/key.pem docker/ssl/key.pem

# Or generate self-signed (not recommended for production)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout docker/ssl/key.pem \
    -out docker/ssl/cert.pem
```

### Step 4: Deploy

```bash
# Make scripts executable
chmod +x scripts/deploy.sh
chmod +x scripts/backup/backup.sh
chmod +x scripts/backup/restore.sh

# Run deployment
./scripts/deploy.sh
```

### Step 5: Verify Deployment

```bash
# Check running containers
docker-compose -f docker/docker-compose.prod.yml ps

# Check logs
docker-compose -f docker/docker-compose.prod.yml logs -f

# Health check
curl -f http://localhost/health
```

## Backup & Restore

### Backup

```bash
# Run backup
./scripts/backup/backup.sh

# Backup location
ls -la /backups/education-district-iv/
```

### Restore

```bash
# Restore from backup
./scripts/backup/restore.sh /backups/education-district-iv/backup_20241201_120000.tar.gz
```

## Monitoring

### Access Monitoring Tools

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (default password from .env.production)

### View Metrics

```bash
# Prometheus metrics
curl http://localhost:9090/metrics

# Application health
curl http://localhost/health
```

## Troubleshooting

### Common Issues

**Database connection refused:**
```bash
# Check PostgreSQL container
docker-compose -f docker/docker-compose.prod.yml logs postgres

# Restart PostgreSQL
docker-compose -f docker/docker-compose.prod.yml restart postgres
```

**Redis connection refused:**
```bash
# Check Redis container
docker-compose -f docker/docker-compose.prod.yml logs redis

# Restart Redis
docker-compose -f docker/docker-compose.prod.yml restart redis
```

**Elasticsearch not starting:**
```bash
# Check Elasticsearch logs
docker-compose -f docker/docker-compose.prod.yml logs elasticsearch

# Increase vm.max_map_count
sudo sysctl -w vm.max_map_count=262144
```

**Nginx 502 Bad Gateway:**
```bash
# Check backend container
docker-compose -f docker/docker-compose.prod.yml logs backend

# Restart backend
docker-compose -f docker/docker-compose.prod.yml restart backend
```

### View Container Status

```bash
# All containers
docker-compose -f docker/docker-compose.prod.yml ps

# Specific container
docker-compose -f docker/docker-compose.prod.yml ps backend
```

### Access Container Shell

```bash
# Backend shell
docker-compose -f docker/docker-compose.prod.yml exec backend bash

# PostgreSQL shell
docker-compose -f docker/docker-compose.prod.yml exec postgres psql -U ediv_user education_district_iv
```

## Scaling

### Horizontal Scaling

```bash
# Scale backend
docker-compose -f docker/docker-compose.prod.yml up -d --scale backend=3

# Scale Celery workers
docker-compose -f docker/docker-compose.prod.yml up -d --scale celery_worker=3
```

### Vertical Scaling

Edit `docker-compose.prod.yml` to increase resources:

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Enable SSL/TLS
- [ ] Configure firewall
- [ ] Set up IP whitelisting for admin
- [ ] Enable rate limiting
- [ ] Configure audit logging
- [ ] Set up automated backups
- [ ] Monitor security alerts
