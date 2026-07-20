#!/bin/bash

# Education District IV Portal - Full Production Deployment
# This script handles complete production deployment

set -e

echo "=========================================="
echo "Education District IV Portal"
echo "Full Production Deployment"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root${NC}"
    exit 1
fi

# Configuration
DOMAIN=${1:-localhost}
DEPLOY_DIR="/opt/education-district-iv"

echo -e "${YELLOW}Deploying for domain: $DOMAIN${NC}"

# Step 1: Server Setup
echo -e "${YELLOW}Step 1: Server Setup${NC}"
./scripts/production/setup-server.sh

# Step 2: Clone Repository
echo -e "${YELLOW}Step 2: Cloning Repository${NC}"
cd $DEPLOY_DIR
if [ -d ".git" ]; then
    git pull origin main
else
    git clone https://github.com/your-org/education-district-iv-portal.git .
fi

# Step 3: Configure Environment
echo -e "${YELLOW}Step 3: Configuring Environment${NC}"
if [ ! -f ".env.production" ]; then
    cp .env.production.example .env.production
    
    # Generate Django secret key
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    sed -i "s/DJANGO_SECRET_KEY=.*/DJANGO_SECRET_KEY=$SECRET_KEY/" .env.production
    
    # Generate secure passwords
    POSTGRES_PASSWORD=$(openssl rand -base64 32)
    REDIS_PASSWORD=$(openssl rand -base64 32)
    ELASTIC_PASSWORD=$(openssl rand -base64 32)
    RABBITMQ_PASSWORD=$(openssl rand -base64 32)
    GRAFANA_PASSWORD=$(openssl rand -base64 16)
    
    sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" .env.production
    sed -i "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$REDIS_PASSWORD/" .env.production
    sed -i "s/ELASTIC_PASSWORD=.*/ELASTIC_PASSWORD=$ELASTIC_PASSWORD/" .env.production
    sed -i "s/RABBITMQ_PASSWORD=.*/RABBITMQ_PASSWORD=$RABBITMQ_PASSWORD/" .env.production
    sed -i "s/GRAFANA_PASSWORD=.*/GRAFANA_PASSWORD=$GRAFANA_PASSWORD/" .env.production
    
    # Configure domain
    if [ "$DOMAIN" != "localhost" ]; then
        ./scripts/production/setup-domain.sh $DOMAIN
    fi
    
    echo -e "${YELLOW}Please review and update .env.production${NC}"
    echo -e "${YELLOW}Press Enter to continue after updating...${NC}"
    read
fi

# Step 4: SSL Setup (if not localhost)
if [ "$DOMAIN" != "localhost" ]; then
    echo -e "${YELLOW}Step 4: SSL Setup${NC}"
    ./scripts/production/setup-ssl.sh $DOMAIN
fi

# Step 5: Build and Start Services
echo -e "${YELLOW}Step 5: Building and Starting Services${NC}"
docker-compose -f docker/docker-compose.prod.yml build --no-cache
docker-compose -f docker/docker-compose.prod.yml up -d

# Step 6: Wait for Services
echo -e "${YELLOW}Step 6: Waiting for Services${NC}"
sleep 60

# Step 7: Database Setup
echo -e "${YELLOW}Step 7: Database Setup${NC}"
docker-compose -f docker/docker-compose.prod.yml exec -T backend python manage.py migrate
docker-compose -f docker/docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput

# Step 8: Seed Data
echo -e "${YELLOW}Step 8: Seeding Data${NC}"
docker-compose -f docker/docker-compose.prod.yml exec -T backend python manage.py seed_departments
docker-compose -f docker/docker-compose.prod.yml exec -T backend python manage.py seed_users

# Step 9: Setup Monitoring
echo -e "${YELLOW}Step 9: Setting Up Monitoring${NC}"
./scripts/production/setup-monitoring.sh
docker-compose -f docker/docker-compose.prod.yml -f docker/docker-compose.monitoring.yml up -d

# Step 10: Health Check
echo -e "${YELLOW}Step 10: Health Check${NC}"
sleep 30

if [ "$DOMAIN" = "localhost" ]; then
    HEALTH_URL="http://localhost/health"
else
    HEALTH_URL="https://$DOMAIN/health"
fi

curl -f $HEALTH_URL || {
    echo -e "${RED}Health check failed!${NC}"
    docker-compose -f docker/docker-compose.prod.yml logs
    exit 1
}

# Step 11: Setup Backup Cron
echo -e "${YELLOW}Step 11: Setting Up Backup Schedule${NC}"
cat > /etc/cron.d/education-district-backup << EOF
# Daily backup at 2:00 AM
0 2 * * * root $DEPLOY_DIR/scripts/backup/backup.sh >> /var/log/education-district-iv/backup.log 2>&1
EOF

# Step 12: Setup Log Rotation
echo -e "${YELLOW}Step 12: Setting Up Log Rotation${NC}"
cat > /etc/logrotate.d/education-district-iv << EOF
/var/log/education-district-iv/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        docker kill --signal=USR1 ediv_backend 2>/dev/null || true
    endscript
}
EOF

echo -e "${GREEN}=========================================="
echo "Production Deployment Completed!"
echo "=========================================="
echo ""
echo "Application URLs:"
if [ "$DOMAIN" = "localhost" ]; then
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000/api/"
    echo "  Admin: http://localhost:8000/admin/"
    echo "  Prometheus: http://localhost:9090"
    echo "  Grafana: http://localhost:3001"
else
    echo "  Frontend: https://$DOMAIN"
    echo "  Backend API: https://$DOMAIN/api/"
    echo "  Admin: https://$DOMAIN/admin/"
    echo "  Prometheus: http://localhost:9090"
    echo "  Grafana: http://localhost:3001"
fi
echo ""
echo "Default Admin Credentials:"
echo "  Email: admin@ediv.gov.ng"
echo "  Password: Admin@12345678"
echo ""
echo "Important:"
echo "  1. Change default passwords immediately"
echo "  2. Review security settings"
echo "  3. Test all functionality"
echo "  4. Monitor system health"
echo ""
echo "Documentation:"
echo "  - API Docs: docs/API_DOCS.md"
echo "  - Deployment Guide: docs/DEPLOYMENT.md"
echo "  - User Manual: docs/USER_MANUAL.md"
echo "=========================================="
