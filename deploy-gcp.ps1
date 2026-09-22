# Deploy ediv-portal to Google Cloud Always Free (e2-micro VM, Container-Optimized OS)
# Requires: gcloud authenticated + a billing-enabled project (Always Free still needs billing attached).
#
#   gcloud auth login
#   gcloud projects create ediv-portal --name="Ediv Portal"   # or pick an existing one
#   gcloud config set project ediv-portal
#   gcloud billing projects link ediv-portal --billing-account=XXXXXX-XXXXXX-XXXXXX
#   .\deploy-gcp.ps1
#
# Free-tier-eligible e2-micro zones: us-west1, us-central1, us-east1, us-east5, us-south1

param(
    [string]$Project   = "ediv-portal",
    [string]$Region    = "us-central1",
    [string]$Zone      = "us-central1-a",
    [string]$Instance  = "ediv-portal",
    [string]$ImageName = "ediv-gcp"
)

$ErrorActionPreference = "Stop"

if ((gcloud config get-value project 2>$null) -ne $Project) {
    throw "No active gcloud project. Run: gcloud config set project $Project"
}
if (-not (Test-Path ".env.production")) { throw ".env.production not found in repo root." }

Write-Host "== Building image $ImageName =="
docker build -t $ImageName . | Out-Host
if ($LASTEXITCODE -ne 0) { throw "docker build failed" }

Write-Host "== Saving image to tar =="
docker save -o "$env:TEMP\ediv-gcp.tar" $ImageName
if ($LASTEXITCODE -ne 0) { throw "docker save failed" }

# Reserve a static IP (free while attached to a running instance)
$ip = gcloud compute addresses describe $Instance --region=$Region --format="value(address)" 2>$null
if ($LASTEXITCODE -ne 0) {
    gcloud compute addresses create $Instance --region=$Region | Out-Host
    Start-Sleep -Seconds 3
    $ip = gcloud compute addresses describe $Instance --region=$Region --format="value(address)"
}

$exists = gcloud compute instances list --filter="name=$Instance" --format="value(name)" 2>$null
if (-not $exists) {
    Write-Host "== Creating e2-micro instance (free tier) =="
    gcloud compute instances create $Instance `
        --zone=$Zone `
        --machine-type=e2-micro `
        --image-family=cos-stable `
        --image-project=cos-cloud `
        --boot-disk-size=30GB `
        --boot-disk-type=pd-standard `
        --address=$ip `
        --tags=ediv-portal | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "instance create failed" }
} else {
    Write-Host "Instance $Instance already exists (skip create)."
}

Write-Host "== Opening firewall for port 8000 =="
gcloud compute firewall-rules create allow-ediv-8000 --allow=tcp:8000 --target-tags=ediv-portal 2>$null | Out-Null

# Ensure SSH keys work before scp
Write-Host "== Setting up SSH access =="
gcloud compute ssh --zone=$Zone $Instance --command="echo ok" | Out-Host

Write-Host "== Copying image tar + run script to instance =="
gcloud compute scp --zone=$Zone "$env:TEMP\ediv-gcp.tar" "${Instance}:/tmp/ediv-gcp.tar" | Out-Host

# Read .env.production key=value pairs (keeps secrets out of this script / git)
$envVars = @{}
foreach ($line in Get-Content ".env.production") {
    if ($line -match '^([A-Z_]+)=(.+)$') {
        $envVars[$matches[1]] = $matches[2].Trim('"').Trim("'")
    }
}

$dbMatch  = [regex]::Match($envVars["DATABASE_URL"], 'postgres(?:ql)?://([^:]+):([^@]+)@[^/]+/([^/]+)')
$dbUser   = if ($dbMatch.Success) { $dbMatch.Groups[1].Value } else { "ediv_user" }
$dbPass   = if ($dbMatch.Success) { $dbMatch.Groups[2].Value } else { "ediv_password" }
$dbName   = if ($dbMatch.Success) { $dbMatch.Groups[3].Value } else { "ediv_db" }

# Names of vars to forward to the container
$forward = @(
    "DJANGO_SETTINGS_MODULE","DJANGO_SECRET_KEY","DJANGO_DEBUG","JWT_ACCESS_TOKEN_LIFETIME_MINUTES",
    "JWT_REFRESH_TOKEN_LIFETIME_DAYS","EMAIL_HOST","EMAIL_PORT","EMAIL_HOST_USER","EMAIL_HOST_PASSWORD",
    "EMAIL_USE_TLS","DEFAULT_FROM_EMAIL","KORA_PAY_PUBLIC_KEY","KORA_PAY_SECRET_KEY","FRONTEND_URL",
    "CLOUDINARY_URL","ADMIN_PASSWORD","TG_PASSWORD","HEAD_OFFICE_PASSWORD","SCHOOL_STAFF_PASSWORD",
    "TEACHER_PASSWORD","STUDENT_PASSWORD"
)

# Build bash env assignment lines with safe single-quote escaping
$remoteEnv = @()
foreach ($k in $forward) {
    if (-not $envVars.ContainsKey($k)) { continue }
    $v = $envVars[$k] -replace "'", "'\''"
    $remoteEnv += "export $k='$v'"
}
$remoteEnv += "export PORT=8000"
$remoteEnv += "export DJANGO_ALLOWED_HOSTS=$ip"
$remoteEnv += "export FRONTEND_URL=$($envVars['FRONTEND_URL'])"
$remoteEnv += "export DATABASE_URL='postgresql://${dbUser}:${dbPass}@ediv-db:5432/$dbName'"
$remoteEnv += "export PYTHONPATH=/app/backend"
$remoteEnv += "export REGISTRY_AUTO_TASK=true"
$remoteEnv += "export AUTO_ASSIGN_RULES=true"

$envText = $remoteEnv -join "`n"

$runBash = @"
#!/usr/bin/env bash
set -e
$envText

sudo docker load -i /tmp/ediv-gcp.tar
sudo docker network create ediv 2>/dev/null || true
sudo docker rm -f ediv-db ediv-backend 2>/dev/null || true

sudo docker run -d --name ediv-db --network ediv --restart unless-stopped \
  -v ediv-pg:/var/lib/postgresql/data \
  -e POSTGRES_USER="$dbUser" -e POSTGRES_PASSWORD="$dbPass" -e POSTGRES_DB="$dbName" \
  postgres:15

sleep 8

# Build env list from the exported variables
env_args=()
while IFS='=' read -r k v; do
  env_args+=(-e "$k=$v")
done < <(env | grep -E '^(DJANGO_|JWT_|EMAIL_|DEFAULT_FROM|KORA_PAY_|FRONTEND_URL|CLOUDINARY_URL|ADMIN_|TG_|HEAD_|SCHOOL_|TEACHER_|STUDENT_|PORT|DATABASE_URL|PYTHONPATH|REGISTRY_AUTO_TASK|AUTO_ASSIGN_RULES)=')

sudo docker run -d --name ediv-backend --network ediv -p 8000:8000 --restart unless-stopped \
  "\${env_args[@]}" \
  ediv-gcp

sleep 5
echo "--- container status ---"
sudo docker ps --filter name=ediv-
echo "--- backend logs (tail) ---"
sudo docker logs --tail 30 ediv-backend 2>&1 || true
"@

$runBash | Out-File -Encoding ascii "$env:TEMP\ediv-gcp-run.sh"

Write-Host "== Installing/starting containers on instance =="
gcloud compute scp --zone=$Zone "$env:TEMP\ediv-gcp-run.sh" "${Instance}:/tmp/ediv-gcp-run.sh" | Out-Host
gcloud compute ssh --zone=$Zone $Instance --command="bash /tmp/ediv-gcp-run.sh" | Out-Host

Write-Host ""
Write-Host "== Deployed =="
Write-Host "App:         http://$ip"
Write-Host "Health:      http://$ip/health/"
Write-Host "API health:  http://$ip/api/health/"
Write-Host ""
Write-Host "Smoke test:  Get-Content "http://$ip/api/health/" | ConvertFrom-Json"
Write-Host ""
Write-Host "Tear down:   gcloud compute instances delete $Instance --zone=$Zone  (and delete the address to avoid idle charges)"