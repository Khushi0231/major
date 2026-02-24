#!/bin/bash
# ============================================================
# DRAVIS — Linux One-Click Installer (Ubuntu / Debian / Fedora)
# curl -fsSL https://raw.githubusercontent.com/Khushi0231/major/main/installers/install-dravis-linux.sh | bash
# ============================================================

set -e
DRAVIS_REPO="https://github.com/Khushi0231/major.git"
DRAVIS_DIR="$HOME/DRAVIS"
DRAVIS_URL="http://localhost"

R='\033[0;31m'; G='\033[0;32m'; B='\033[0;34m'; Y='\033[0;33m'; W='\033[1;37m'; NC='\033[0m'

clear
echo -e "${B}"
echo "  ██████╗ ██████╗  █████╗ ██╗   ██╗██╗███████╗"
echo "  ██╔══██╗██╔══██╗██╔══██╗██║   ██║██║██╔════╝"
echo "  ██║  ██║██████╔╝███████║██║   ██║██║███████╗"
echo "  ██║  ██║██╔══██╗██╔══██║╚██╗ ██╔╝██║╚════██║"
echo "  ██████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║"
echo "  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝"
echo -e "${NC}"
echo -e "${W}  AI Study Assistant — Linux Installer${NC}"
echo "  ─────────────────────────────────────"
echo "  • Installs: Docker, Ollama, Mistral 7B, DRAVIS"
echo "  • First run: 5-15 min  |  After that: instant"
echo ""
echo -e "${Y}  Press ENTER to start, or Ctrl+C to cancel.${NC}"
read -r

log()  { echo -e "${G}  ✓ $1${NC}"; }
warn() { echo -e "${Y}  ⚠ $1${NC}"; }
step() { echo -e "${B}  ▶ $1...${NC}"; }
err()  { echo -e "${R}  ✗ $1${NC}"; exit 1; }

# Detect OS
if command -v apt-get &>/dev/null; then
    PKG_MGR="apt"
elif command -v dnf &>/dev/null; then
    PKG_MGR="dnf"
elif command -v yum &>/dev/null; then
    PKG_MGR="yum"
else
    err "Unsupported Linux distribution. Install Docker manually and re-run."
fi

# ── Step 1: Git ───────────────────────────────────────────────
step "Checking Git"
if ! command -v git &>/dev/null; then
    sudo $PKG_MGR install -y git
fi
log "Git ready"

# ── Step 2: Docker Engine ─────────────────────────────────────
step "Checking Docker"
if ! command -v docker &>/dev/null; then
    warn "Installing Docker Engine..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker "$USER"
    warn "Docker installed. You may need to log out and back in for group permissions."
    warn "For now, using sudo for Docker commands."
fi

# Start Docker if not running
if ! sudo docker info &>/dev/null; then
    sudo systemctl start docker 2>/dev/null || sudo service docker start 2>/dev/null || true
    sleep 3
fi
log "Docker ready"

# ── Step 3: Docker Compose ────────────────────────────────────
step "Checking Docker Compose"
if ! docker compose version &>/dev/null && ! docker-compose version &>/dev/null; then
    warn "Installing Docker Compose..."
    sudo apt-get install -y docker-compose-plugin 2>/dev/null || \
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose && sudo chmod +x /usr/local/bin/docker-compose
fi
log "Docker Compose ready"

# ── Step 4: Clone DRAVIS ──────────────────────────────────────
step "Setting up DRAVIS"
if [ -d "$DRAVIS_DIR" ]; then
    warn "DRAVIS already installed at $DRAVIS_DIR"
    echo "  [1] Update  [2] Fresh install  [3] Just start"
    read -rp "  Choose [1/2/3]: " CHOICE
    case "$CHOICE" in
        1) cd "$DRAVIS_DIR" && git pull origin main; log "Updated" ;;
        2) rm -rf "$DRAVIS_DIR"; git clone "$DRAVIS_REPO" "$DRAVIS_DIR"; log "Fresh clone" ;;
        3) log "Using existing" ;;
    esac
else
    git clone "$DRAVIS_REPO" "$DRAVIS_DIR"
    log "Cloned to $DRAVIS_DIR"
fi
cd "$DRAVIS_DIR"

# ── Step 5: Launch ────────────────────────────────────────────
echo ""
echo -e "${W}  Starting DRAVIS (first run downloads ~4.5 GB AI model)...${NC}"
echo ""

sudo docker compose up --build -d 2>&1 || sudo docker-compose up --build -d 2>&1

step "Waiting for DRAVIS"
for i in $(seq 1 90); do
    if curl -sf "$DRAVIS_URL/" &>/dev/null; then break; fi
    printf "."; sleep 3
done
echo ""

echo ""
echo -e "${G}  ╔══════════════════════════════════════╗${NC}"
echo -e "${G}  ║  ✅ DRAVIS is ready!                 ║${NC}"
echo -e "${G}  ║     http://localhost                 ║${NC}"
echo -e "${G}  ╚══════════════════════════════════════╝${NC}"
echo ""
echo -e "  Stop:  ${Y}cd ~/DRAVIS && docker compose down${NC}"
echo -e "  Start: ${Y}cd ~/DRAVIS && docker compose up -d${NC}"
echo ""

# Try to open browser
xdg-open "$DRAVIS_URL" 2>/dev/null || echo "  Open $DRAVIS_URL in your browser"
