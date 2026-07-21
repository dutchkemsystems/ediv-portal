# Education District IV Portal - Development Start Script
# Run this script to start both backend and frontend

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Education District IV Portal" -ForegroundColor Cyan
Write-Host "Starting Development Servers..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Start backend server
Write-Host "`nStarting backend server on port 8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\Activate.ps1; python manage.py runserver 8000"

# Wait for backend to start
Start-Sleep -Seconds 3

# Start frontend server
Write-Host "Starting frontend server on port 3000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "Servers are starting..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend API: http://localhost:8000/api/" -ForegroundColor Yellow
Write-Host "Django Admin: http://localhost:8000/admin/" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Default Admin Credentials:" -ForegroundColor Yellow
Write-Host "  Email: admin@ediv.gov.ng" -ForegroundColor Cyan
Write-Host "  Password: Admin@12345678" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Green
