#!/bin/bash
# ================================================================
#  DRAVIS Installer for macOS
#  Double-click or run: bash install-dravis-mac.sh
# ================================================================

set -e

echo ""
echo "  ========================================"
echo "       DRAVIS — AI Study Assistant"
echo "       One-click offline installer"
echo "  ========================================"
echo ""

# ─── Check Docker ────────────────────────────────
echo "[1/4] Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo ""
    echo "  Docker Desktop is required but not installed."
    echo "  Opening download page..."
    open "https://www.docker.com/products/docker-desktop" 2>/dev/null
    echo ""
    echo "  After installing Docker Desktop:"
    echo "    1. Open Docker Desktop and wait for it to start"
    echo "    2. Run this script again"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo ""
    echo "  Docker Desktop is installed but NOT running."
    echo "  Please open Docker Desktop, wait until ready, then re-run this script."
    exit 1
fi
echo "  [OK] Docker is running."

# ─── Check Git ───────────────────────────────────
echo "[2/4] Checking Git..."
if ! command -v git &> /dev/null; then
    echo "  Git not found. Installing via Xcode tools..."
    xcode-select --install 2>/dev/null || true
    echo "  After Git installs, re-run this script."
    exit 1
fi
echo "  [OK] Git found."

# ─── Clone DRAVIS ────────────────────────────────
echo "[3/4] Setting up DRAVIS..."
INSTALL_DIR="$HOME/DRAVIS"

if [ -f "$INSTALL_DIR/docker-compose.yml" ]; then
    echo "  DRAVIS already installed. Updating..."
    cd "$INSTALL_DIR"
    git pull origin main 2>/dev/null || true
else
    echo "  Downloading DRAVIS..."
    git clone --depth 1 https://github.com/Khushi0231/major.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# ─── Start DRAVIS ────────────────────────────────
echo "[4/4] Starting DRAVIS..."
echo ""
echo "  First launch downloads the Mistral 7B AI model (~4.5 GB)."
echo "  This is a one-time download. Please be patient!"
echo ""

docker compose up --build -d

echo ""
echo "  Waiting for services..."
sleep 20

echo ""
echo "  ========================================"
echo "   DRAVIS is starting!"
echo ""
echo "   Open:  http://localhost:8080"
echo "   Stop:  cd ~/DRAVIS && docker compose down"
echo "  ========================================"
echo ""

open http://localhost:8080 2>/dev/null || true
