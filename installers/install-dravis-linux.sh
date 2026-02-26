#!/bin/bash
# ================================================================
#  DRAVIS Installer for Linux
#  Run: curl -fsSL https://raw.githubusercontent.com/Khushi0231/major/main/installers/install-dravis-linux.sh | bash
#  Or:  bash install-dravis-linux.sh
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
    echo "  Docker not found. Installing..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker "$USER"
    echo ""
    echo "  Docker installed! Please log out and log back in, then re-run this script."
    exit 0
fi

if ! docker info &> /dev/null; then
    echo "  Docker is installed but the daemon isn't running."
    echo "  Try: sudo systemctl start docker"
    echo "  Then re-run this script."
    exit 1
fi
echo "  [OK] Docker is running."

# ─── Check docker compose ────────────────────────
echo "[2/4] Checking docker compose..."
if ! docker compose version &> /dev/null; then
    echo "  docker compose plugin not found. Installing..."
    sudo apt-get update -qq && sudo apt-get install -y -qq docker-compose-plugin 2>/dev/null \
      || sudo dnf install -y docker-compose-plugin 2>/dev/null \
      || { echo "Please install docker compose manually."; exit 1; }
fi
echo "  [OK] docker compose found."

# ─── Check Git ───────────────────────────────────
echo "[3/4] Checking Git..."
if ! command -v git &> /dev/null; then
    sudo apt-get install -y git 2>/dev/null \
      || sudo dnf install -y git 2>/dev/null \
      || sudo pacman -S --noconfirm git 2>/dev/null
fi
echo "  [OK] Git found."

# ─── Clone DRAVIS ────────────────────────────────
echo "[4/4] Setting up DRAVIS..."
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
echo ""
echo "  Starting DRAVIS..."
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

xdg-open http://localhost:8080 2>/dev/null || echo "  Open http://localhost:8080 in your browser"
