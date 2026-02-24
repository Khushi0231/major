# ============================================================
# DRAVIS — Windows Installer
# Right-click → Run with PowerShell
# ============================================================

$ErrorActionPreference = "Stop"
$DRAVIS_DIR = "$env:USERPROFILE\DRAVIS"
$COMPOSE_URL = "https://raw.githubusercontent.com/Khushi0231/major/main/docker-compose.prod.yml"

# Admin check
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    exit
}

Clear-Host
Write-Host "`n  DRAVIS — AI Study Assistant Installer" -ForegroundColor Blue
Write-Host "  ======================================`n"

# Step 1: Docker
Write-Host "  Checking Docker..." -ForegroundColor Cyan
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "  Installing Docker Desktop via winget..." -ForegroundColor Yellow
    winget install --id Docker.DockerDesktop -e --source winget --silent
    Write-Host "`n  Docker installed. Please:" -ForegroundColor Yellow
    Write-Host "  1. Open Docker Desktop from Start Menu"
    Write-Host "  2. Accept the license"
    Write-Host "  3. Run this installer again"
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe" -ErrorAction SilentlyContinue
    Read-Host "`n  Press ENTER to exit"
    exit 0
}

$w = 0
while ($true) {
    $r = docker info 2>&1
    if ($LASTEXITCODE -eq 0) { break }
    if ($w -ge 30) { Write-Host "  Docker not running. Start Docker Desktop." -ForegroundColor Red; exit 1 }
    Start-Sleep 2; $w += 2
}
Write-Host "  [OK] Docker running" -ForegroundColor Green

# Step 2: Download compose file
New-Item -ItemType Directory -Force -Path $DRAVIS_DIR | Out-Null
Write-Host "  Downloading DRAVIS config..." -ForegroundColor Cyan
Invoke-WebRequest -Uri $COMPOSE_URL -OutFile "$DRAVIS_DIR\docker-compose.yml"
Write-Host "  [OK] Config ready" -ForegroundColor Green

# Step 3: Pull & start
Set-Location $DRAVIS_DIR
Write-Host "`n  Downloading DRAVIS images (~1.5 GB first time)..." -ForegroundColor Cyan
docker compose pull

Write-Host "`n  Starting DRAVIS..." -ForegroundColor Cyan
docker compose up -d

Write-Host "`n  First run: AI model download (~4.5 GB, 5-15 min)" -ForegroundColor Yellow
Write-Host "  After that, starts are instant.`n"

Write-Host "  Waiting for DRAVIS..." -ForegroundColor Cyan
for ($i = 0; $i -lt 120; $i++) {
    try { $r = Invoke-WebRequest -Uri "http://localhost" -TimeoutSec 2 -ErrorAction Stop; if ($r.StatusCode -eq 200) { break } } catch {}
    Start-Sleep 3
}

Write-Host "`n  =================================" -ForegroundColor Green
Write-Host "  DRAVIS is installed!" -ForegroundColor Green
Write-Host "  Open: http://localhost" -ForegroundColor Green
Write-Host "  =================================`n" -ForegroundColor Green
Write-Host "  Stop:  cd ~\DRAVIS; docker compose down"
Write-Host "  Start: cd ~\DRAVIS; docker compose up -d`n"
Start-Process "http://localhost"
Read-Host "  Press ENTER to close"
