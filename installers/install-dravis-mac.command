#!/bin/bash
# ============================================================
# DRAVIS — macOS One-Click Installer
# Double-click this file in Finder to install DRAVIS
# ============================================================
# This script:
#  1. Installs Homebrew (if needed)
#  2. Installs Docker Desktop (if needed)
#  3. Installs git (if needed)  
#  4. Clones the DRAVIS repository
#  5. Starts the full stack (Ollama + Mistral 7B + App)
#  6. Opens DRAVIS in your browser
# ============================================================

set -e

# Colors
R='\033[0;31m'; G='\033[0;32m'; B='\033[0;34m'; Y='\033[0;33m'; W='\033[1;37m'; NC='\033[0m'

DRAVIS_REPO="https://github.com/Khushi0231/major.git"
DRAVIS_DIR="$HOME/DRAVIS"
DRAVIS_URL="http://localhost"

clear
echo ""
echo -e "${B}  ██████╗ ██████╗  █████╗ ██╗   ██╗██╗███████╗${NC}"
echo -e "${B}  ██╔══██╗██╔══██╗██╔══██╗██║   ██║██║██╔════╝${NC}"
echo -e "${B}  ██║  ██║██████╔╝███████║██║   ██║██║███████╗${NC}"
echo -e "${B}  ██║  ██║██╔══██╗██╔══██║╚██╗ ██╔╝██║╚════██║${NC}"
echo -e "${B}  ██████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║${NC}"
echo -e "${B}  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝${NC}"
echo ""
echo -e "${W}  AI Study Assistant — macOS Installer${NC}"
echo -e "  ─────────────────────────────────────"
echo -e "  • Installs: Docker, Ollama, Mistral 7B"
echo -e "  • First run: ~5-10 min (model download)"
echo -e "  • After that: instant start every time"
echo ""
echo -e "${Y}  Press ENTER to start, or Ctrl+C to cancel.${NC}"
read -r

log()  { echo -e "${G}  ✓ $1${NC}"; }
warn() { echo -e "${Y}  ⚠ $1${NC}"; }
err()  { echo -e "${R}  ✗ $1${NC}"; exit 1; }
step() { echo -e "${B}  ▶ $1...${NC}"; }

# ── Step 1: Homebrew ─────────────────────────────────────────
step "Checking Homebrew"
if ! command -v brew &>/dev/null; then
    warn "Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || err "Failed to install Homebrew"
    # Add to PATH for Apple Silicon
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
fi
log "Homebrew ready"

# ── Step 2: Git ───────────────────────────────────────────────
step "Checking Git"
if ! command -v git &>/dev/null; then
    brew install git || err "Failed to install git"
fi
log "Git ready"

# ── Step 3: Docker Desktop ────────────────────────────────────
step "Checking Docker"
if ! command -v docker &>/dev/null; then
    warn "Docker not found. Installing Docker Desktop (~600 MB)..."
    brew install --cask docker || err "Failed to install Docker Desktop"
    echo ""
    warn "Docker Desktop installed. Please:"
    echo "  1. Open Docker Desktop from your Applications folder"
    echo "  2. Accept the license agreement"
    echo "  3. Wait for Docker to fully start (whale icon in menu bar)"
    echo "  4. Run this installer again"
    echo ""
    open -a "Docker" 2>/dev/null || open /Applications/Docker.app 2>/dev/null || true
    exit 0
fi

# Wait for Docker daemon
step "Waiting for Docker daemon"
DOCKER_WAIT=0
while ! docker info &>/dev/null; do
    if [ $DOCKER_WAIT -ge 30 ]; then
        err "Docker is not starting. Please open Docker Desktop and try again."
    fi
    printf "."
    sleep 2
    DOCKER_WAIT=$((DOCKER_WAIT + 2))
done
echo ""
log "Docker is running"

# ── Step 4: Clone DRAVIS ──────────────────────────────────────
step "Setting up DRAVIS"
if [ -d "$DRAVIS_DIR" ]; then
    warn "DRAVIS folder already exists at $DRAVIS_DIR"
    echo -e "  Options:"
    echo -e "  [1] Update existing installation (recommended)"
    echo -e "  [2] Fresh install (deletes existing)"
    echo -e "  [3] Keep existing and just start"
    printf "  Choose [1/2/3]: "
    read -r CHOICE
    case "$CHOICE" in
        1) 
            step "Updating DRAVIS"
            cd "$DRAVIS_DIR" && git pull origin main 2>&1 | tail -3
            log "Updated"
            ;;
        2)
            step "Fresh install"
            rm -rf "$DRAVIS_DIR"
            git clone "$DRAVIS_REPO" "$DRAVIS_DIR" || err "Failed to clone repository"
            log "Fresh clone complete"
            ;;
        3)
            log "Using existing installation"
            ;;
    esac
else
    step "Cloning DRAVIS repository"
    git clone "$DRAVIS_REPO" "$DRAVIS_DIR" || err "Failed to clone. Check your internet connection."
    log "Repository cloned to $DRAVIS_DIR"
fi

cd "$DRAVIS_DIR"

# ── Step 5: docker-compose up ─────────────────────────────────
echo ""
echo -e "${W}  ─────────────────────────────────────${NC}"
echo -e "${W}  Starting DRAVIS...${NC}"
echo -e "${W}  ─────────────────────────────────────${NC}"
echo ""

# Check if this is a first run (no Ollama model cached)
if ! docker volume inspect major_ollama_data &>/dev/null 2>&1; then
    echo -e "${Y}  📥 First time: Downloading Mistral 7B AI model (~4.5 GB)${NC}"
    echo -e "     This takes 5-15 minutes depending on your internet."
    echo -e "     Subsequent starts will be instant."
    echo ""
fi

step "Building and starting all services"
docker compose up --build -d 2>&1 | grep -E "(Building|Started|Created|Error|error)" || \
  docker-compose up --build -d 2>&1 | grep -E "(Building|Started|Created|Error|error)"

echo ""
step "Waiting for DRAVIS to be ready"
for i in $(seq 1 90); do
    if curl -sf "$DRAVIS_URL/" &>/dev/null; then
        break
    fi
    printf "."
    sleep 3
done
echo ""

# Final status
if curl -sf "$DRAVIS_URL/" &>/dev/null; then
    echo ""
    echo -e "${G}  ╔══════════════════════════════════════╗${NC}"
    echo -e "${G}  ║  ✅  DRAVIS is ready!                ║${NC}"
    echo -e "${G}  ╚══════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  🌐 Open in browser: ${W}http://localhost${NC}"
    echo ""
    echo -e "  📌 To stop:   ${Y}cd ~/DRAVIS && docker compose down${NC}"
    echo -e "  📌 To start:  ${Y}cd ~/DRAVIS && docker compose up -d${NC}"
    echo ""
    # Open in default browser
    open "$DRAVIS_URL" 2>/dev/null || true
else
    warn "DRAVIS may still be starting (model download takes time)."
    echo -e "  Open ${W}http://localhost${NC} in your browser."
    echo -e "  The green indicator will appear when AI is ready."
    open "$DRAVIS_URL" 2>/dev/null || true
fi

echo ""
echo -e "  Press ENTER to close this window."
read -r
