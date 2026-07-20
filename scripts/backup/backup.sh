#!/bin/bash

# Education District IV Portal Backup Script

set -e

echo "=========================================="
echo "Education District IV Portal Backup"
echo "=========================================="

# Configuration
BACKUP_DIR="/backups/education-district-iv"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/backup_${DATE}.tar.gz"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo -e "${GREEN}Starting backup...${NC}"

# Backup PostgreSQL database
echo -e "${YELLOW}Backing up PostgreSQL database...${NC}"
docker-compose -f docker/docker-compose.prod.yml exec -T postgres pg_dump -U ediv_user education_district_iv > "${BACKUP_DIR}/db_${DATE}.sql"

# Backup media files
echo -e "${YELLOW}Backing up media files...${NC}"
docker-compose -f docker/docker-compose.prod.yml exec -T backend tar -czf /tmp/media_backup.tar.gz /app/media
docker cp ediv_backend:/tmp/media_backup.tar.gz "${BACKUP_DIR}/media_${DATE}.tar.gz"

# Backup configuration files
echo -e "${YELLOW}Backing up configuration files...${NC}"
tar -czf "${BACKUP_DIR}/config_${DATE}.tar.gz" \
    .env.production \
    docker/docker-compose.prod.yml \
    docker/nginx.prod.conf

# Create combined backup
echo -e "${YELLOW}Creating combined backup...${NC}"
tar -czf "$BACKUP_FILE" \
    -C "$BACKUP_DIR" \
    "db_${DATE}.sql" \
    "media_${DATE}.tar.gz" \
    "config_${DATE}.tar.gz"

# Clean up individual files
rm -f "${BACKUP_DIR}/db_${DATE}.sql"
rm -f "${BACKUP_DIR}/media_${DATE}.tar.gz"
rm -f "${BACKUP_DIR}/config_${DATE}.tar.gz"

# Keep only last 7 backups
echo -e "${YELLOW}Cleaning old backups...${NC}"
ls -t "$BACKUP_DIR"/backup_*.tar.gz | tail -n +8 | xargs -r rm

# Calculate backup size
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)

echo -e "${GREEN}=========================================="
echo "Backup completed successfully!"
echo "=========================================="
echo ""
echo "Backup file: $BACKUP_FILE"
echo "Backup size: $BACKUP_SIZE"
echo "=========================================="
