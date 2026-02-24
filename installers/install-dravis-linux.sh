#!/bin/bash
# ============================================================
# DRAVIS — Linux Installer
# curl -fsSL https://raw.githubusercontent.com/Khushi0231/major/main/installers/install-dravis-linux.sh | bash
# ============================================================
set -e

G='\033[0;32m'; B='\033[0;34m'; Y='\033[0;33m'; R='\033[0;31m'; NC='\033[0m'
DRAVIS_DIR="$HOME/DRAVIS"
COMPOSE_URL="https://raw.githubusercontent.com/Khushi0231/major/main/docker-compose.prod.yml"

echo -e "${B}  DRAVIS — AI Study Assistant Installer${NC}"
echo ""

# Docker
if ! command -v docker &>/dev/null; then
    echo -e "${Y}  Installing Docker...${NC}"
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker "$USER"
fi
if ! docker info &>/dev/null 2>&1; then
    sudo systemctl start docker 2>/dev/null || sudo service docker start 2>/dev/null
fi
echo -e "${G}  ✓ Docker ready${NC}"

# Compose
if ! docker compose version &>/dev/null && ! docker-compose version &>/dev/null; then
    sudo apt-get install -y docker-compose-plugin 2>/dev/null || true
fi

# Download & start
mkdir -p "$DRAVIS_DIR"
curl -fsSL "$COMPOSE_URL" -o "$DRAVIS_DIR/docker-compose.yml"
cd "$DRAVIS_DIR"

echo -e "${B}  Pulling images...${NC}"
docker compose pull 2>/dev/null || sudo docker compose pull

echo -e "${B}  Starting DRAVIS...${NC}"
docker compose up -d 2>/dev/null || sudo docker compose up -d

echo ""
echo -e "${G}  ✅ DRAVIS installed! Open: http://localhost${NC}"
echo "  First run downloads AI model (~4.5 GB, 5-15 min)."
echo "  Stop:  cd ~/DRAVIS && docker compose down"
echo "  Start: cd ~/DRAVIS && docker compose up -d"

xdg-open http://localhost 2>/dev/null || true
