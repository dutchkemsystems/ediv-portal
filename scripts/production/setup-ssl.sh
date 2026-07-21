#!/bin/bash

# Education District IV Portal - SSL Certificate Setup
# This script sets up SSL certificates using Let's Encrypt

set -e

echo "=========================================="
echo "Education District IV Portal"
echo "SSL Certificate Setup"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if domain is provided
if [ -z "$1" ]; then
    echo -e "${RED}Usage: $0 <domain.com>${NC}"
    echo "Example: $0 portal.ediv.gov.ng"
    exit 1
fi

DOMAIN=$1
EMAIL=${2:-admin@$DOMAIN}

echo -e "${YELLOW}Setting up SSL for: $DOMAIN${NC}"

# Install Certbot
echo -e "${YELLOW}Installing Certbot...${NC}"
apt-get install -y certbot

# Stop nginx temporarily
echo -e "${YELLOW}Stopping Nginx...${NC}"
docker-compose -f docker/docker-compose.prod.yml stop nginx

# Obtain certificate
echo -e "${YELLOW}Obtaining SSL certificate...${NC}"
certbot certonly --standalone \
    -d $DOMAIN \
    -d www.$DOMAIN \
    --email $EMAIL \
    --agree-tos \
    --non-interactive

# Create SSL directory for Docker
echo -e "${YELLOW}Setting up SSL for Docker...${NC}"
mkdir -p docker/ssl

# Copy certificates
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem docker/ssl/cert.pem
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem docker/ssl/key.pem

# Set permissions
chmod 600 docker/ssl/key.pem
chmod 644 docker/ssl/cert.pem

# Create renewal script
echo -e "${YELLOW}Setting up automatic renewal...${NC}"
cat > /etc/cron.d/certbot-renew << EOF
# Renew SSL certificates twice daily
0 0,12 * * * root certbot renew --quiet --post-hook "cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /opt/education-district-iv/docker/ssl/cert.pem && cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /opt/education-district-iv/docker/ssl/key.pem && docker-compose -f /opt/education-district-iv/docker/docker-compose.prod.yml restart nginx"
EOF

# Start nginx
echo -e "${YELLOW}Starting Nginx...${NC}"
docker-compose -f docker/docker-compose.prod.yml start nginx

# Verify SSL
echo -e "${YELLOW}Verifying SSL certificate...${NC}"
curl -f https://$DOMAIN/health || {
    echo -e "${RED}SSL verification failed!${NC}"
    exit 1
}

echo -e "${GREEN}=========================================="
echo "SSL setup completed successfully!"
echo "=========================================="
echo ""
echo "Certificate installed for:"
echo "  - $DOMAIN"
echo "  - www.$DOMAIN"
echo ""
echo "Certificate will auto-renew via cron."
echo "=========================================="
