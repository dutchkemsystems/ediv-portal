# Education District IV Portal - Windows Local Setup
# This script sets up the development environment on Windows

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Education District IV Portal" -ForegroundColor Cyan
Write-Host "Windows Local Development Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check prerequisites
Write-Host "`nChecking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Check npm
try {
    $npmVersion = npm --version 2>&1
    Write-Host "✓ npm: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ npm not found" -ForegroundColor Red
    exit 1
}

# Setup backend
Write-Host "`nSetting up backend..." -ForegroundColor Yellow

# Create virtual environment
Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
cd backend
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
pip install -r requirements/dev.txt

# Create local settings
Write-Host "Creating local settings..." -ForegroundColor Cyan
if (!(Test-Path "config\settings\local.py")) {
    @"
from .development import *

# Local development settings
DEBUG = True

# Use SQLite for local development (no PostgreSQL required)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Disable Elasticsearch for local development
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': '',
    },
}

# Use console email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable CORS for local development
CORS_ALLOW_ALL_ORIGINS = True
"@ | Out-File -FilePath "config\settings\local.py" -Encoding UTF8
}

# Update manage.py to use local settings
Write-Host "Updating manage.py..." -ForegroundColor Cyan
$manageContent = Get-Content "manage.py" -Raw
$manageContent = $manageContent.Replace(
    "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')",
    "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')"
)
$manageContent | Out-File -FilePath "manage.py" -Encoding UTF8

# Run migrations
Write-Host "Running database migrations..." -ForegroundColor Cyan
python manage.py migrate

# Create superuser
Write-Host "Creating superuser..." -ForegroundColor Cyan
$env:DJANGO_SUPERUSER_PASSWORD = "Admin@12345678"
python manage.py createsuperuser --noinput --email admin@ediv.gov.ng --first_name Admin --last_name User

# Seed data
Write-Host "Seeding initial data..." -ForegroundColor Cyan
python manage.py seed_departments 2>$null
python manage.py seed_users 2>$null

cd ..

# Setup frontend
Write-Host "`nSetting up frontend..." -ForegroundColor Yellow

cd frontend

# Install dependencies
Write-Host "Installing Node.js dependencies..." -ForegroundColor Cyan
npm install

cd ..

# Create startup script
Write-Host "`nCreating startup script..." -ForegroundColor Yellow
@'
# Education District IV Portal - Start Script
# Run this script to start both backend and frontend

Write-Host "Starting Education District IV Portal..." -ForegroundColor Cyan

# Start backend in new window
Write-Host "Starting backend server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-Command", "cd backend; .\venv\Scripts\Activate.ps1; python manage.py runserver 8000"

# Wait for backend to start
Start-Sleep -Seconds 5

# Start frontend in new window
Write-Host "Starting frontend server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-Command", "cd frontend; npm run dev"

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "Servers starting..." -ForegroundColor Cyan
Write-Host "Backend: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host "Admin: http://localhost:8000/admin" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
'@ | Out-File -FilePath "start-dev.ps1" -Encoding UTF8

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Yellow
Write-Host "  .\start-dev.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "Or start manually:" -ForegroundColor Yellow
Write-Host "  Backend: cd backend; .\venv\Scripts\Activate.ps1; python manage.py runserver 8000" -ForegroundColor Cyan
Write-Host "  Frontend: cd frontend; npm run dev" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Yellow
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Backend API: http://localhost:8000/api/" -ForegroundColor Cyan
Write-Host "  Admin: http://localhost:8000/admin" -ForegroundColor Cyan
Write-Host ""
Write-Host "Default Admin Credentials:" -ForegroundColor Yellow
Write-Host "  Email: admin@ediv.gov.ng" -ForegroundColor Cyan
Write-Host "  Password: Admin@12345678" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Green
