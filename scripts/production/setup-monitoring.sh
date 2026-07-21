#!/bin/bash

# Education District IV Portal - Monitoring Setup
# This script sets up comprehensive monitoring

set -e

echo "=========================================="
echo "Education District IV Portal"
echo "Monitoring Setup"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create monitoring directory
echo -e "${YELLOW}Creating monitoring directories...${NC}"
mkdir -p /opt/education-district-iv/monitoring
mkdir -p /opt/education-district-iv/monitoring/grafana/dashboards
mkdir -p /opt/education-district-iv/monitoring/grafana/provisioning

# Create Grafana dashboard
echo -e "${YELLOW}Creating Grafana dashboard...${NC}"
cat > /opt/education-district-iv/monitoring/grafana/dashboards/education-district.json << 'EOF'
{
  "dashboard": {
    "title": "Education District IV Portal",
    "panels": [
      {
        "title": "API Requests",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{status}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~'5..'}[5m]) / rate(http_requests_total[5m]) * 100",
            "legendFormat": "Error %"
          }
        ]
      },
      {
        "title": "Active Users",
        "type": "stat",
        "targets": [
          {
            "expr": "count(active_users)",
            "legendFormat": "Active Users"
          }
        ]
      }
    ]
  }
}
EOF

# Create Grafana datasource provisioning
echo -e "${YELLOW}Creating Grafana datasource...${NC}"
cat > /opt/education-district-iv/monitoring/grafana/provisioning/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

# Create Prometheus alert rules
echo -e "${YELLOW}Creating Prometheus alerts...${NC}"
cat > /opt/education-district-iv/monitoring/prometheus/alerts.yml << EOF
groups:
  - name: education_district_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100 > 5
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is above 5% for more than 5 minutes"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time"
          description: "95th percentile response time is above 2 seconds"

      - alert: LowDiskSpace
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 15
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space"
          description: "Disk space is below 15%"

      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is above 85%"
EOF

# Create monitoring docker-compose override
echo -e "${YELLOW}Creating monitoring configuration...${NC}"
cat > /opt/education-district-iv/docker/docker-compose.monitoring.yml << EOF
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: ediv_prometheus
    restart: always
    volumes:
      - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./monitoring/prometheus/alerts.yml:/etc/prometheus/alerts.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - ediv_network

  grafana:
    image: grafana/grafana:latest
    container_name: ediv_grafana
    restart: always
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=\${GRAFANA_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
    ports:
      - "3001:3000"
    depends_on:
      - prometheus
    networks:
      - ediv_network

  node-exporter:
    image: prom/node-exporter:latest
    container_name: ediv_node_exporter
    restart: always
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--path.rootfs=/rootfs'
    ports:
      - "9100:9100"
    networks:
      - ediv_network

  redis-exporter:
    image: oliver006/redis_exporter:latest
    container_name: ediv_redis_exporter
    restart: always
    environment:
      - REDIS_ADDR=redis://redis:6379
      - REDIS_PASSWORD=\${REDIS_PASSWORD}
    ports:
      - "9121:9121"
    networks:
      - ediv_network

  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    container_name: ediv_postgres_exporter
    restart: always
    environment:
      - DATA_SOURCE_NAME=postgresql://\${POSTGRES_USER}:\${POSTGRES_PASSWORD}@postgres:5432/\${POSTGRES_DB}?sslmode=disable
    ports:
      - "9187:9187"
    networks:
      - ediv_network

volumes:
  prometheus_data:
  grafana_data:
EOF

echo -e "${GREEN}=========================================="
echo "Monitoring setup completed!"
echo "=========================================="
echo ""
echo "Monitoring endpoints:"
echo "  Prometheus: http://localhost:9090"
echo "  Grafana: http://localhost:3001"
echo "  Node Exporter: http://localhost:9100"
echo ""
echo "Default Grafana credentials:"
echo "  Username: admin"
echo "  Password: (from .env.production)"
echo "=========================================="
