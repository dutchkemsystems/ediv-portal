# Education District IV Portal - Quick Start Guide

## Prerequisites

- Ubuntu 22.04 LTS server
- 4+ CPU cores
- 8+ GB RAM
- 100+ GB storage
- Domain name (optional)

## Quick Deployment (5 minutes)

### Option 1: Local Development

```bash
# Clone repository
git clone https://github.com/your-org/education-district-iv-portal.git
cd education-district-iv-portal

# Start development server
docker-compose up -d

# Access application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Admin: http://localhost:8000/admin
```

### Option 2: Production Deployment

```bash
# SSH into server
ssh root@your-server-ip

# Clone and deploy
git clone https://github.com/your-org/education-district-iv-portal.git /opt/education-district-iv
cd /opt/education-district-iv

# Run production setup
chmod +x scripts/production/*.sh
./scripts/production/deploy-production.sh your-domain.com
```

## Default Credentials

| Role | Email | Password |
|------|-------|----------|
| System Admin | admin@ediv.gov.ng | Admin@12345678 |
| Tutor General | tg@ediv.gov.ng | TutorGen@12345 |
| HR Head | hr@ediv.gov.ng | DeptHead@12345 |
| Finance Director | finance@ediv.gov.ng | DeptHead@12345 |

## First Steps After Deployment

### 1. Change Default Passwords

```bash
# Access Django shell
docker-compose -f docker/docker-compose.prod.yml exec backend python manage.py shell

# Change admin password
from apps.users.models import User
admin = User.objects.get(email='admin@ediv.gov.ng')
admin.set_password('your-new-secure-password')
admin.save()
```

### 2. Configure Email Settings

Edit `.env.production`:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
```

### 3. Configure SMS (Optional)

Edit `.env.production`:

```env
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890
```

### 4. Import Initial Data

```bash
# Import schools
docker-compose -f docker/docker-compose.prod.yml exec backend python manage.py seed_schools

# Import staff
docker-compose -f docker/docker-compose.prod.yml exec backend python manage.py seed_staff

# Import students
docker-compose -f docker/docker-compose.prod.yml exec backend python manage.py seed_students
```

## Common Commands

### Start Services

```bash
docker-compose -f docker/docker-compose.prod.yml up -d
```

### Stop Services

```bash
docker-compose -f docker/docker-compose.prod.yml down
```

### View Logs

```bash
# All services
docker-compose -f docker/docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker/docker-compose.prod.yml logs -f backend
```

### Run Migrations

```bash
docker-compose -f docker/docker-compose.prod.yml exec backend python manage.py migrate
```

### Create Superuser

```bash
docker-compose -f docker/docker-compose.prod.yml exec backend python manage.py createsuperuser
```

### Backup Database

```bash
./scripts/backup/backup.sh
```

### Restore Database

```bash
./scripts/backup/restore.sh /backups/education-district-iv/backup_YYYYMMDD_HHMMSS.tar.gz
```

## Troubleshooting

### Services Not Starting

```bash
# Check service status
docker-compose -f docker/docker-compose.prod.yml ps

# Check logs
docker-compose -f docker/docker-compose.prod.yml logs

# Restart services
docker-compose -f docker/docker-compose.prod.yml restart
```

### Database Connection Issues

```bash
# Check PostgreSQL
docker-compose -f docker/docker-compose.prod.yml exec postgres psql -U ediv_user education_district_iv

# Test connection
docker-compose -f docker/docker-compose.prod.yml exec backend python manage.py dbshell
```

### Memory Issues

```bash
# Check memory usage
docker stats

# Increase swap
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Disk Space Issues

```bash
# Check disk usage
df -h

# Clean Docker
docker system prune -a

# Clean logs
sudo journalctl --vacuum-time=7d
```

## Monitoring

### Access Monitoring Tools

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001

### View Metrics

```bash
# Check application metrics
curl http://localhost:8000/metrics

# Check system metrics
curl http://localhost:9100/metrics
```

## Support

- **Documentation**: `/docs` folder
- **API Reference**: `docs/API_DOCS.md`
- **Deployment Guide**: `docs/DEPLOYMENT.md`
- **User Manual**: `docs/USER_MANUAL.md`

## Next Steps

1. Review [Security Checklist](DEPLOYMENT.md#security-checklist)
2. Configure [Backup Schedule](DEPLOYMENT.md#backup--restore)
3. Set up [Monitoring Alerts](DEPLOYMENT.md#monitoring)
4. Train users using [Training Manual](TRAINING_MANUAL.md)
