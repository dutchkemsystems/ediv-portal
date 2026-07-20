#!/bin/bash

# Education District IV Portal Restore Script

set -e

echo "=========================================="
echo "Education District IV Portal Restore"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backup file is provided
if [ -z "$1" ]; then
    echo -e "${RED}Usage: $0 <backup_file>${NC}"
    echo "Example: $0 /backups/education-district-iv/backup_20241201_120000.tar.gz"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}WARNING: This will overwrite all existing data!${NC}"
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${YELLOW}Restore cancelled.${NC}"
    exit 0
fi

# Create temporary directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

echo -e "${GREEN}Starting restore from: $BACKUP_FILE${NC}"

# Extract backup
echo -e "${YELLOW}Extracting backup...${NC}"
tar -xzf "$BACKUP_FILE"

# Stop services
echo -e "${YELLOW}Stopping services...${NC}"
cd -
docker-compose -f docker/docker-compose.prod.yml down

# Start database service only
echo -e "${YELLOW}Starting database service...${NC}"
docker-compose -f docker/docker-compose.prod.yml up -d postgres
sleep 10

# Restore database
echo -e "${YELLOW}Restoring database...${NC}"
docker-compose -f docker/docker-compose.prod.yml exec -T postgres psql -U ediv_user -d education_district_iv < "$TEMP_DIR/db_"*.sql

# Restore media files
echo -e "${YELLOW}Restoring media files...${NC}"
docker-compose -f docker/docker-compose.prod.yml up -d backend
sleep 5
docker cp "$TEMP_DIR/media_"*.tar.gz ediv_backend:/tmp/
docker-compose -f docker/docker-compose.prod.yml exec -T backend tar -xzf /tmp/media_backup.tar.gz -C /

# Restore configuration
echo -e "${YELLOW}Restoring configuration...${NC}"
tar -xzf "$TEMP_DIR/config_"*.tar.gz -C /

# Start all services
echo -e "${YELLOW}Starting all services...${NC}"
docker-compose -f docker/docker-compose.prod.yml up -d

# Cleanup
echo -e "${YELLOW}Cleaning up...${NC}"
rm -rf "$TEMP_DIR"

echo -e "${GREEN}=========================================="
echo "Restore completed successfully!"
echo "=========================================="
echo ""
echo "Please verify the application is working correctly."
echo "=========================================="
