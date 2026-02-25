# ================================================================
#  DRAVIS Installer for Windows
#  Right-click this file → "Run with PowerShell"
# ================================================================

$ErrorActionPreference = "Stop"
$Host.UI.RawUI.WindowTitle = "DRAVIS Installer"

Write-Host ""
Write-Host "  ========================================" -ForegroundColor Cyan
Write-Host "       DRAVIS — AI Study Assistant        " -ForegroundColor Cyan
Write-Host "       One-click offline installer        " -ForegroundColor Cyan
Write-Host "  ========================================" -ForegroundColor Cyan
Write-Host ""

# ─── Check Docker ────────────────────────────────
Write-Host "[1/4] Checking Docker..." -ForegroundColor Yellow
$dockerPath = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerPath) {
    Write-Host ""
    Write-Host "  Docker Desktop is required but not installed." -ForegroundColor Red
    Write-Host "  Opening download page..." -ForegroundColor Yellow
    Start-Process "https://www.docker.com/products/docker-desktop"
    Write-Host ""
    Write-Host "  After installing Docker Desktop:" -ForegroundColor White
    Write-Host "    1. Restart your computer"
    Write-Host "    2. Open Docker Desktop and wait for it to start"
    Write-Host "    3. Right-click this script again → Run with PowerShell"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Docker is actually running
try {
    docker info 2>$null | Out-Null
} catch {
    Write-Host ""
    Write-Host "  Docker Desktop is installed but NOT running." -ForegroundColor Red
    Write-Host "  Please open Docker Desktop, wait for the green icon, then re-run this script." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "  [OK] Docker is running." -ForegroundColor Green

# ─── Check Git ───────────────────────────────────
Write-Host "[2/4] Checking Git..." -ForegroundColor Yellow
$gitPath = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitPath) {
    Write-Host "  Git not found. Opening download page..." -ForegroundColor Yellow
    Start-Process "https://git-scm.com/download/win"
    Write-Host "  Install Git, then re-run this script." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "  [OK] Git found." -ForegroundColor Green

# ─── Clone DRAVIS ────────────────────────────────
Write-Host "[3/4] Setting up DRAVIS..." -ForegroundColor Yellow
$installDir = "$env:USERPROFILE\DRAVIS"

if (Test-Path "$installDir\docker-compose.yml") {
    Write-Host "  DRAVIS already installed. Updating..." -ForegroundColor Yellow
    Push-Location $installDir
    git pull origin main 2>$null
} else {
    Write-Host "  Downloading DRAVIS..." -ForegroundColor Green
    git clone --depth 1 https://github.com/Khushi0231/major.git $installDir
    Push-Location $installDir
}

# ─── Start DRAVIS ────────────────────────────────
Write-Host "[4/4] Starting DRAVIS..." -ForegroundColor Yellow
Write-Host ""
Write-Host "  First launch downloads the Mistral 7B AI model (~4.5 GB)." -ForegroundColor Yellow
Write-Host "  This is a one-time download. Please be patient!" -ForegroundColor Yellow
Write-Host ""

docker compose up --build -d

Write-Host ""
Write-Host "  Waiting for services..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

Write-Host ""
Write-Host "  ========================================" -ForegroundColor Cyan
Write-Host "   DRAVIS is starting!" -ForegroundColor Green
Write-Host ""
Write-Host "   Open:  http://localhost:8080" -ForegroundColor White
Write-Host "   Stop:  docker compose down  (in $installDir)" -ForegroundColor Gray
Write-Host "  ========================================" -ForegroundColor Cyan
Write-Host ""

Start-Process "http://localhost:8080"
Pop-Location
Read-Host "Press Enter to close this window"
