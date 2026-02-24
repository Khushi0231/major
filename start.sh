#!/bin/bash
# DRAVIS — Start Script (Linux / macOS / Codespaces)
set -e

GREEN='\033[0;32m'; BLUE='\033[0;34m'; YELLOW='\033[0;33m'; RED='\033[0;31m'; NC='\033[0m'

echo -e "${BLUE}"
echo "  ██████╗ ██████╗  █████╗ ██╗   ██╗██╗███████╗"
echo "  ██╔══██╗██╔══██╗██╔══██╗██║   ██║██║██╔════╝"
echo "  ██║  ██║██████╔╝███████║██║   ██║██║███████╗"
echo "  ██║  ██║██╔══██╗██╔══██║╚██╗ ██╔╝██║╚════██║"
echo "  ██████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║"
echo "  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝"
echo -e "${NC}"
echo "  Offline AI Study Assistant — Mistral 7B"
echo "  ============================================"
echo ""

# Check Docker
if ! command -v docker &>/dev/null; then
    echo -e "${RED}[ERROR] Docker not found!${NC}"
    echo "  Install: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker info &>/dev/null; then
    echo -e "${RED}[ERROR] Docker daemon is not running${NC}"
    echo "  Start Docker Desktop and try again."
    exit 1
fi

echo -e "${GREEN}✓ Docker is running${NC}"

# First run detection
if ! docker volume inspect dravis_ollama_data &>/dev/null 2>&1; then
    echo ""
    echo -e "${YELLOW}⚠️  First time setup detected.${NC}"
    echo "   Mistral 7B (~4.5 GB) will be downloaded automatically."
    echo "   This takes 5-15 min depending on your connection."
    echo "   All subsequent starts are instant."
    echo ""
fi

echo -e "${BLUE}▶ Starting DRAVIS stack...${NC}"
docker-compose up --build -d

echo ""
echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"

# Wait for frontend (last to come up)
for i in $(seq 1 60); do
    if curl -sf http://localhost/ &>/dev/null; then
        break
    fi
    printf "."
    sleep 2
done
echo ""

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  ✅ DRAVIS is ready!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "   🌐 App:      http://localhost"
echo "   🔧 API:      http://localhost/api"
echo "   📥 Download: http://localhost/download"
echo "   🤖 Ollama:   http://localhost:11434"
echo ""
echo "   Green indicator = Mistral 7B online"
echo ""
echo "   To stop:   docker-compose down"
echo "   To update: git pull && docker-compose up --build -d"
echo ""
