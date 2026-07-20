#!/bin/bash

# Education District IV Portal Deployment Script

set -e

echo "=========================================="
echo "Education District IV Portal Deployment"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Check for .env.production file
if [ ! -f .env.production ]; then
    echo -e "${YELLOW}.env.production file not found. Creating from template...${NC}"
    cp .env.example .env.production
    echo -e "${YELLOW}Please edit .env.production with your production settings.${NC}"
    exit 1
fi

echo -e "${GREEN}Starting deployment...${NC}"

# Stop existing containers
echo -e "${YELLOW}Stopping existing containers...${NC}"
docker-compose -f docker/docker-compose.prod.yml down

# Build images
echo -e "${YELLOW}Building Docker images...${NC}"
docker-compose -f docker/docker-compose.prod.yml build --no-cache

# Start services
echo -e "${YELLOW}Starting services...${NC}"
docker-compose -f docker/docker-compose.prod.yml up -d

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 30

# Run migrations
echo -e "${YELLOW}Running database migrations...${NC}"
docker-compose -f docker/docker-compose.prod.yml exec backend python manage.py migrate

# Collect static files
echo -e "${YELLOW}Collecting static files...${NC}"
docker-compose -f docker/docker-compose.prod.yml exec backend python manage.py collectstatic --noinput

# Seed data
echo -e "${YELLOW}Seeding initial data...${NC}"
docker-compose -f docker/docker-compose.prod.yml exec backend python manage.py seed_departments
docker-compose -f docker/docker-compose.prod.yml exec backend python manage.py seed_users

# Create superuser
echo -e "${YELLOW}Creating superuser...${NC}"
docker-compose -f docker/docker-compose.prod.yml exec backend python manage.py createsuperuser --noinput || true

# Health check
echo -e "${YELLOW}Performing health check...${NC}"
curl -f http://localhost/health || {
    echo -e "${RED}Health check failed!${NC}"
    exit 1
}

echo -e "${GREEN}=========================================="
echo "Deployment completed successfully!"
echo "=========================================="
echo ""
echo "Frontend: http://localhost"
echo "Backend API: http://localhost/api/"
echo "Admin: http://localhost/admin/"
echo ""
echo "Monitoring:"
echo "Prometheus: http://localhost:9090"
echo "Grafana: http://localhost:3001"
echo "=========================================="
