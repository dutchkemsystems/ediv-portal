#!/usr/bin/env bash
set -e
export DJANGO_SETTINGS_MODULE='config.settings.production'
export PORT=8000
export DJANGO_ALLOWED_HOSTS='34.10.179.156'
export DATABASE_URL='postgresql://user:PASSWORD@ediv-db:5432/education_district_iv'
export PYTHONPATH='/app/backend'
export REGISTRY_AUTO_TASK=true
export AUTO_ASSIGN_RULES=true
IMAGE='gcr.io/ediv-portal/ediv-backend'

# GCR auth via VM metadata service account (COS helper)
sudo /usr/share/google/dockercfg_config.sh 2>/dev/null || true

sudo docker pull "$IMAGE"

sudo docker network create ediv 2>/dev/null || true
sudo docker rm -f ediv-db ediv-backend 2>/dev/null || true

sudo docker run -d --name ediv-db --network ediv --restart unless-stopped \
  -v ediv-pg:/var/lib/postgresql/data \
  -e POSTGRES_USER='user' -e POSTGRES_PASSWORD='PASSWORD' -e POSTGRES_DB='education_district_iv' \
  postgres:15

sleep 8

# Forward real secrets from .env.production via env block below (added by deploy)
sudo docker run -d --name ediv-backend --network ediv -p 8000:8000 --restart unless-stopped \
  --env-file /tmp/ediv.env "$IMAGE"

sleep 5
echo "--- container status ---"
sudo docker ps --filter name=ediv-
echo "--- backend logs (tail) ---"
sudo docker logs --tail 30 ediv-backend 2>&1 || true