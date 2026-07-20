#!/bin/bash

# Education District IV Portal - Production Deployment
# Run this from the project root directory

set -e

echo "=========================================="
echo "Education District IV Portal"
echo "Production Deployment"
echo "=========================================="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo -e "${RED}Error: .env.production file not found${NC}"
    echo "Copy .env.example to .env.production and configure it"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

# Step 1: Build images
echo -e "${YELLOW}Step 1: Building Docker images...${NC}"
docker compose -f docker/docker-compose.prod.yml build --no-cache

# Step 2: Stop existing containers
echo -e "${YELLOW}Step 2: Stopping existing containers...${NC}"
docker compose -f docker/docker-compose.prod.yml down

# Step 3: Start services
echo -e "${YELLOW}Step 3: Starting production services...${NC}"
docker compose -f docker/docker-compose.prod.yml up -d

# Step 4: Wait for services to be healthy
echo -e "${YELLOW}Step 4: Waiting for services to be healthy...${NC}"
sleep 15

# Step 5: Run migrations
echo -e "${YELLOW}Step 5: Running database migrations...${NC}"
docker compose -f docker/docker-compose.prod.yml exec -T backend python manage.py migrate --noinput

# Step 6: Collect static files
echo -e "${YELLOW}Step 6: Collecting static files...${NC}"
docker compose -f docker/docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput

# Step 7: Health check
echo -e "${YELLOW}Step 7: Running health check...${NC}"
sleep 5
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo -e "${GREEN}Health check passed!${NC}"
else
    echo -e "${YELLOW}Health check endpoint not ready yet (services may still be starting)${NC}"
fi

# Step 8: Show status
echo -e "${YELLOW}Step 8: Container status:${NC}"
docker compose -f docker/docker-compose.prod.yml ps

echo ""
echo -e "${GREEN}=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Application URLs:"
echo "  Frontend:  http://localhost"
echo "  Backend:   http://localhost/api/"
echo "  Admin:     http://localhost/admin/"
echo "  Health:    http://localhost/health"
echo "  Grafana:   http://localhost:3001"
echo ""
echo "Default Admin Credentials:"
echo "  Email:    admin@ediv.gov.ng"
echo "  Password: Admin@12345678"
echo ""
echo "IMPORTANT:"
echo "  1. Change default passwords immediately"
echo "  2. Configure KoraPay keys in .env.production"
echo "  3. Set up SSL for production (use Let's Encrypt)"
echo "  4. Update DJANGO_ALLOWED_HOSTS with your domain"
echo "=========================================="
