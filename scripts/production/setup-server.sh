#!/bin/bash

# Education District IV Portal - Production Server Setup
# This script sets up a fresh Ubuntu server for production deployment

set -e

echo "=========================================="
echo "Education District IV Portal"
echo "Production Server Setup"
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

# Update system
echo -e "${YELLOW}Updating system packages...${NC}"
apt-get update
apt-get upgrade -y

# Install essential packages
echo -e "${YELLOW}Installing essential packages...${NC}"
apt-get install -y \
    curl \
    wget \
    git \
    vim \
    htop \
    net-tools \
    ufw \
    fail2ban \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# Install Docker
echo -e "${YELLOW}Installing Docker...${NC}"
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Add user to docker group
usermod -aG docker $SUDO_USER

# Install Docker Compose
echo -e "${YELLOW}Installing Docker Compose...${NC}"
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Verify installations
echo -e "${YELLOW}Verifying installations...${NC}"
docker --version
docker-compose --version

# Configure firewall
echo -e "${YELLOW}Configuring firewall...${NC}"
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 3000/tcp  # Frontend (development)
ufw allow 8000/tcp  # Backend (development)
ufw allow 9090/tcp  # Prometheus
ufw allow 3001/tcp  # Grafana
ufw --force enable

# Configure fail2ban
echo -e "${YELLOW}Configuring fail2ban...${NC}"
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
EOF

systemctl enable fail2ban
systemctl start fail2ban

# Create deployment directory
echo -e "${YELLOW}Creating deployment directory...${NC}"
mkdir -p /opt/education-district-iv
mkdir -p /var/log/education-district-iv
mkdir -p /backups/education-district-iv

# Set up log rotation
echo -e "${YELLOW}Setting up log rotation...${NC}"
cat > /etc/logrotate.d/education-district-iv << EOF
/var/log/education-district-iv/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        /usr/bin/docker kill --signal=USR1 ediv_backend 2>/dev/null || true
    endscript
}
EOF

# Optimize kernel parameters
echo -e "${YELLOW}Optimizing kernel parameters...${NC}"
cat >> /etc/sysctl.conf << EOF
# Education District IV Portal Optimizations
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.ip_local_port_range = 1024 65535
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 15
vm.max_map_count = 262144
fs.file-max = 2097152
EOF

sysctl -p

# Set up automatic security updates
echo -e "${YELLOW}Setting up automatic security updates...${NC}"
apt-get install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades

# Create swap file (4GB)
echo -e "${YELLOW}Creating swap file...${NC}"
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
echo 'vm.swappiness=10' >> /etc/sysctl.conf
sysctl -p

echo -e "${GREEN}=========================================="
echo "Server setup completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Clone the repository:"
echo "   cd /opt/education-district-iv"
echo "   git clone https://github.com/your-org/education-district-iv-portal.git ."
echo ""
echo "2. Configure environment:"
echo "   cp .env.production.example .env.production"
echo "   nano .env.production"
echo ""
echo "3. Run deployment:"
echo "   ./scripts/deploy.sh"
echo "=========================================="
