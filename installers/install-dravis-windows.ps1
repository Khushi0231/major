# DRAVIS Installer for Windows (PowerShell)
# Run: Right-click this file → "Run with PowerShell"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "      DRAVIS AI Installer for Windows     " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check for Docker
Write-Host "Checking for Docker..." -ForegroundColor Yellow
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Docker Desktop not found." -ForegroundColor Red
    Write-Host "Opening the Docker download page..." -ForegroundColor Yellow
    Start-Process "https://www.docker.com/products/docker-desktop"
    Write-Host "Please install Docker Desktop, restart your computer, then re-run this script." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Docker found." -ForegroundColor Green
Write-Host ""

# Check for Git
Write-Host "Checking for Git..." -ForegroundColor Yellow
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Git not found." -ForegroundColor Red
    Write-Host "Opening the Git download page..." -ForegroundColor Yellow
    Start-Process "https://git-scm.com/download/win"
    Write-Host "Please install Git, then re-run this script." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Git found." -ForegroundColor Green
Write-Host ""

# Clone or update the repo
$TARGET_DIR = "$env:USERPROFILE\dravis"

if (Test-Path $TARGET_DIR) {
    Write-Host "DRAVIS folder already exists. Updating to latest version..." -ForegroundColor Yellow
    Set-Location $TARGET_DIR
    git pull
} else {
    Write-Host "Cloning DRAVIS repository..." -ForegroundColor Green
    git clone https://github.com/Khushi0231/major.git $TARGET_DIR
    Set-Location $TARGET_DIR
}

Write-Host ""
Write-Host "Starting DRAVIS..." -ForegroundColor Green
Write-Host "(First launch downloads the Mistral AI model — about 4.5GB. Please be patient!)" -ForegroundColor Yellow
Write-Host ""

# Start the application
docker-compose up -d

Write-Host ""
Write-Host "Waiting for DRAVIS to come online..."
Start-Sleep -Seconds 15

# Open in browser
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " SUCCESS! DRAVIS is running!" -ForegroundColor Green
Write-Host " Open your browser to: http://localhost:8080" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Start-Process "http://localhost:8080"

Read-Host "Press Enter to exit"
