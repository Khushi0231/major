# ============================================================
# DRAVIS — Windows One-Click Installer
# Right-click this file → "Run with PowerShell"
# ============================================================
# This script:
#  1. Installs Docker Desktop (via winget or direct download)
#  2. Installs git (if needed)
#  3. Clones the DRAVIS repository
#  4. Starts the full stack (Ollama + Mistral 7B + App)
#  5. Opens DRAVIS in your browser
# ============================================================

$ErrorActionPreference = "Stop"

$DRAVIS_REPO  = "https://github.com/Khushi0231/major.git"
$DRAVIS_DIR   = "$env:USERPROFILE\DRAVIS"
$DRAVIS_URL   = "http://localhost"

# Run as admin check
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "`n  [DRAVIS] Requesting administrator privileges..." -ForegroundColor Yellow
    Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    exit
}

Clear-Host
Write-Host ""
Write-Host "  ██████╗ ██████╗  █████╗ ██╗   ██╗██╗███████╗" -ForegroundColor Blue
Write-Host "  ██╔══██╗██╔══██╗██╔══██╗██║   ██║██║██╔════╝" -ForegroundColor Blue
Write-Host "  ██║  ██║██████╔╝███████║██║   ██║██║███████╗" -ForegroundColor Blue
Write-Host "  ██║  ██║██╔══██╗██╔══██║╚██╗ ██╔╝██║╚════██║" -ForegroundColor Blue
Write-Host "  ██████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║" -ForegroundColor Blue
Write-Host "  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝" -ForegroundColor Blue
Write-Host ""
Write-Host "  AI Study Assistant — Windows Installer" -ForegroundColor White
Write-Host "  -----------------------------------------------"
Write-Host "  . Installs: Docker Desktop, Git, Ollama, Mistral 7B"
Write-Host "  . First run: 5-15 min (AI model download)"
Write-Host "  . After that: instant start every time"
Write-Host ""
Write-Host "  Press ENTER to start, or Ctrl+C to cancel." -ForegroundColor Yellow
Read-Host

function Log  { Write-Host "  [OK] $args" -ForegroundColor Green }
function Warn { Write-Host "  [!]  $args" -ForegroundColor Yellow }
function Step { Write-Host "  [...] $args" -ForegroundColor Cyan }
function Err  { Write-Host "  [ERR] $args" -ForegroundColor Red; Read-Host "Press ENTER to exit"; exit 1 }

# ── Step 1: WSL2 Check ───────────────────────────────────────
Step "Checking WSL2 (required for Docker)"
$wslStatus = wsl --status 2>&1
if ($LASTEXITCODE -ne 0) {
    Warn "WSL2 not set up. Installing..."
    wsl --install --no-distribution
    Warn "WSL2 installed. Please RESTART your computer and run this installer again."
    Read-Host "Press ENTER to restart now (recommended)"
    Restart-Computer -Force
}
Log "WSL2 ready"

# ── Step 2: Git ───────────────────────────────────────────────
Step "Checking Git"
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Warn "Git not found. Installing via winget..."
    winget install --id Git.Git -e --source winget --silent
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}
Log "Git ready"

# ── Step 3: Docker Desktop ────────────────────────────────────
Step "Checking Docker Desktop"
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Warn "Docker not found. Installing Docker Desktop..."
    winget install --id Docker.DockerDesktop -e --source winget --silent
    Warn "Docker Desktop installed."
    Write-Host ""
    Write-Host "  Please:" -ForegroundColor White
    Write-Host "  1. Open Docker Desktop from Start Menu"
    Write-Host "  2. Accept the license agreement"
    Write-Host "  3. Wait for the whale icon in the system tray"
    Write-Host "  4. Run this installer again"
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe" -ErrorAction SilentlyContinue
    Read-Host "Press ENTER to exit (re-run after Docker starts)"
    exit 0
}

# Wait for Docker daemon
Step "Waiting for Docker daemon"
$dockerWait = 0
while ($true) {
    $result = docker info 2>&1
    if ($LASTEXITCODE -eq 0) { break }
    if ($dockerWait -ge 60) { Err "Docker is not starting. Open Docker Desktop and try again." }
    Write-Host "." -NoNewline
    Start-Sleep 3
    $dockerWait += 3
}
Write-Host ""
Log "Docker is running"

# ── Step 4: Clone DRAVIS ──────────────────────────────────────
Step "Setting up DRAVIS"
if (Test-Path $DRAVIS_DIR) {
    Warn "DRAVIS already installed at $DRAVIS_DIR"
    Write-Host "  [1] Update existing (recommended)"
    Write-Host "  [2] Fresh install"
    Write-Host "  [3] Just start"
    $choice = Read-Host "  Choose [1/2/3]"
    switch ($choice) {
        "1" { Set-Location $DRAVIS_DIR; git pull origin main; Log "Updated" }
        "2" { Remove-Item -Recurse -Force $DRAVIS_DIR; git clone $DRAVIS_REPO $DRAVIS_DIR; Log "Fresh clone done" }
        "3" { Log "Using existing install" }
    }
} else {
    git clone $DRAVIS_REPO $DRAVIS_DIR
    Log "Repository cloned to $DRAVIS_DIR"
}

Set-Location $DRAVIS_DIR

# ── Step 5: Start DRAVIS ──────────────────────────────────────
Write-Host ""
Write-Host "  -----------------------------------------------" -ForegroundColor White
Write-Host "  Starting DRAVIS..." -ForegroundColor White
Write-Host "  -----------------------------------------------" -ForegroundColor White
Write-Host ""

$volumeExists = docker volume inspect major_ollama_data 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [i] First run: Downloading Mistral 7B AI model (~4.5 GB)" -ForegroundColor Yellow
    Write-Host "      This takes 5-15 minutes. Subsequent starts are instant." -ForegroundColor Gray
    Write-Host ""
}

Step "Building and starting all Docker services"
docker compose up --build -d
if ($LASTEXITCODE -ne 0) {
    docker-compose up --build -d
}

Write-Host ""
Step "Waiting for DRAVIS to be ready"
for ($i = 0; $i -lt 90; $i++) {
    try {
        $r = Invoke-WebRequest -Uri $DRAVIS_URL -TimeoutSec 2 -ErrorAction Stop
        if ($r.StatusCode -eq 200) { break }
    } catch {}
    Write-Host "." -NoNewline
    Start-Sleep 3
}
Write-Host ""

# Final status
try {
    Invoke-WebRequest -Uri $DRAVIS_URL -TimeoutSec 3 | Out-Null
    Write-Host ""
    Write-Host "  +--------------------------------------+" -ForegroundColor Green
    Write-Host "  |  DRAVIS is ready!                   |" -ForegroundColor Green
    Write-Host "  +--------------------------------------+" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Open: http://localhost" -ForegroundColor White
} catch {
    Warn "DRAVIS is still starting (model may still be downloading)."
    Write-Host "  Open http://localhost - green indicator = AI ready."
}

Write-Host ""
Write-Host "  To stop:   cd ~\DRAVIS; docker compose down" -ForegroundColor Yellow
Write-Host "  To start:  cd ~\DRAVIS; docker compose up -d" -ForegroundColor Yellow
Write-Host ""
Start-Process $DRAVIS_URL
Read-Host "Press ENTER to close"
