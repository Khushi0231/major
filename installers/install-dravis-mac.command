#!/bin/bash
# ============================================================
# DRAVIS — macOS Installer (double-click this file)
# ============================================================
set -e

G='\033[0;32m'; B='\033[0;34m'; Y='\033[0;33m'; R='\033[0;31m'; NC='\033[0m'
DRAVIS_DIR="$HOME/DRAVIS"
COMPOSE_URL="https://raw.githubusercontent.com/Khushi0231/major/main/docker-compose.prod.yml"

clear
echo -e "${B}"
echo "  ██████╗ ██████╗  █████╗ ██╗   ██╗██╗███████╗"
echo "  ██╔══██╗██╔══██╗██╔══██╗██║   ██║██║██╔════╝"
echo "  ██║  ██║██████╔╝███████║██║   ██║██║███████╗"
echo "  ██║  ██║██╔══██╗██╔══██║╚██╗ ██╔╝██║╚════██║"
echo "  ██████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║"
echo "  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝"
echo -e "${NC}"
echo "  AI Study Assistant — Installer"
echo ""
echo "  This will install DRAVIS on your Mac."
echo "  Requires ~6 GB disk space."
echo ""
echo -e "${Y}  Press ENTER to start, Ctrl+C to cancel.${NC}"
read -r

# ── Step 1: Docker ──
echo ""
if ! command -v docker &>/dev/null; then
    echo -e "${Y}  Docker not found. Installing via Homebrew...${NC}"
    if ! command -v brew &>/dev/null; then
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        [[ -f "/opt/homebrew/bin/brew" ]] && eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    brew install --cask docker
    echo ""
    echo -e "${Y}  Docker Desktop installed. Please:${NC}"
    echo "  1. Open Docker Desktop from Applications"
    echo "  2. Accept the license"
    echo "  3. Wait for it to start (whale icon in menu bar)"
    echo "  4. Run this installer again"
    open -a Docker 2>/dev/null || true
    echo ""; read -rp "  Press ENTER to exit" _; exit 0
fi

if ! docker info &>/dev/null 2>&1; then
    echo -e "${R}  Docker is installed but not running. Start Docker Desktop first.${NC}"
    open -a Docker 2>/dev/null || true
    echo ""; read -rp "  Press ENTER to exit" _; exit 1
fi
echo -e "${G}  ✓ Docker is running${NC}"

# ── Step 2: Download compose file ──
mkdir -p "$DRAVIS_DIR"
echo -e "${B}  Downloading DRAVIS config...${NC}"
curl -fsSL "$COMPOSE_URL" -o "$DRAVIS_DIR/docker-compose.yml"
echo -e "${G}  ✓ Config ready${NC}"

# ── Step 3: Pull & start ──
cd "$DRAVIS_DIR"

echo ""
echo -e "${B}  Downloading DRAVIS images (first time ~1.5 GB)...${NC}"
docker compose pull

echo ""
echo -e "${B}  Starting DRAVIS...${NC}"
docker compose up -d

echo ""
echo -e "${Y}  First run: downloading Mistral 7B AI model (~4.5 GB)${NC}"
echo "  This takes 5-15 min. After that, starts are instant."

echo ""
echo -e "${B}  Waiting for DRAVIS to be ready...${NC}"
for i in $(seq 1 120); do
    if curl -sf http://localhost/ &>/dev/null; then break; fi
    printf "."; sleep 3
done
echo ""

echo ""
echo -e "${G}  ╔════════════════════════════════════╗${NC}"
echo -e "${G}  ║  ✅ DRAVIS is installed!           ║${NC}"
echo -e "${G}  ║  Open: http://localhost             ║${NC}"
echo -e "${G}  ╚════════════════════════════════════╝${NC}"
echo ""
echo "  To stop:  cd ~/DRAVIS && docker compose down"
echo "  To start: cd ~/DRAVIS && docker compose up -d"
echo ""
open http://localhost 2>/dev/null || true
read -rp "  Press ENTER to close" _
