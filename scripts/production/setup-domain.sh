#!/bin/bash

# Education District IV Portal - Domain Configuration
# This script configures DNS and domain settings

set -e

echo "=========================================="
echo "Education District IV Portal"
echo "Domain Configuration"
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
SERVER_IP=$(curl -s ifconfig.me)

echo -e "${YELLOW}Configuring domain: $DOMAIN${NC}"
echo -e "${YELLOW}Server IP: $SERVER_IP${NC}"

# Create DNS configuration instructions
echo -e "${GREEN}=========================================="
echo "DNS Configuration Required"
echo "=========================================="
echo ""
echo "Please add the following DNS records:"
echo ""
echo "Type    Name                    Value"
echo "----    ----                    -----"
echo "A       $DOMAIN                $SERVER_IP"
echo "A       www.$DOMAIN            $SERVER_IP"
echo "MX      $DOMAIN                mail.$DOMAIN (priority 10)"
echo "TXT     $DOMAIN                v=spf1 mx a ~all"
echo ""
echo "For email (optional):"
echo "CNAME   mail.$DOMAIN           $SERVER_IP"
echo "CNAME   smtp.$DOMAIN           $SERVER_IP"
echo "CNAME   imap.$DOMAIN           $SERVER_IP"
echo ""
echo "=========================================="

# Update Nginx configuration with domain
echo -e "${YELLOW}Updating Nginx configuration...${NC}"
sed -i "s/server_name localhost;/server_name $DOMAIN www.$DOMAIN;/g" docker/nginx.prod.conf

# Update environment file with domain
echo -e "${YELLOW}Updating environment file...${NC}"
sed -i "s/DJANGO_ALLOWED_HOSTS=.*/DJANGO_ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,localhost/" .env.production
sed -i "s|REACT_APP_API_URL=.*|REACT_APP_API_URL=https://$DOMAIN/api|" .env.production
sed -i "s|REACT_APP_WS_URL=.*|REACT_APP_WS_URL=wss://$DOMAIN/ws|" .env.production

# Update CORS settings
echo -e "${YELLOW}Updating CORS settings...${NC}"
cat >> .env.production << EOF

# CORS
CORS_ALLOWED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN
EOF

echo -e "${GREEN}=========================================="
echo "Domain configuration completed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Add DNS records as shown above"
echo "2. Wait for DNS propagation (24-48 hours)"
echo "3. Run SSL setup: ./scripts/production/setup-ssl.sh $DOMAIN"
echo "4. Deploy application: ./scripts/deploy.sh"
echo "=========================================="
