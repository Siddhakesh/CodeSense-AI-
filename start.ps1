# Explain Any Codebase - Startup Script

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  Explain Any Codebase - Backend" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (Test-Path ".venv") {
    Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Green
    .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "[INFO] No virtual environment found. Using global Python..." -ForegroundColor Yellow
}

# Check if dependencies are installed
Write-Host "[INFO] Checking dependencies..." -ForegroundColor Green
$result = pip show fastapi 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] Dependencies not found. Installing..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

Write-Host ""
Write-Host "[INFO] Starting server..." -ForegroundColor Green
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Open your browser:" -ForegroundColor Cyan
Write-Host "  http://localhost:8000" -ForegroundColor Yellow
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Start the server
uvicorn app.main:app --reload
