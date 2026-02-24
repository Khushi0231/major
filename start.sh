#!/bin/bash
# DRAVIS — Start Script (Linux / macOS / Codespaces)
set -e

G='\033[0;32m'; B='\033[0;34m'; Y='\033[0;33m'; R='\033[0;31m'; NC='\033[0m'

echo -e "${B}"
echo "  ██████╗ ██████╗  █████╗ ██╗   ██╗██╗███████╗"
echo "  ██╔══██╗██╔══██╗██╔══██╗██║   ██║██║██╔════╝"
echo "  ██║  ██║██████╔╝███████║██║   ██║██║███████╗"
echo "  ██║  ██║██╔══██╗██╔══██║╚██╗ ██╔╝██║╚════██║"
echo "  ██████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║"
echo "  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝"
echo -e "${NC}"
echo "  Offline AI Study Assistant"
echo ""

# Check Docker
if ! command -v docker &>/dev/null; then
    echo -e "${R}  Docker not found! Install: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi
if ! docker info &>/dev/null 2>&1; then
    echo -e "${R}  Docker daemon not running. Start Docker Desktop and try again.${NC}"
    exit 1
fi
echo -e "${G}  ✓ Docker running${NC}"

# Detect compose command
if docker compose version &>/dev/null; then
    DC="docker compose"
elif docker-compose version &>/dev/null; then
    DC="docker-compose"
else
    echo -e "${R}  Docker Compose not found!${NC}"
    exit 1
fi

# First run?
if ! docker volume ls -q | grep -q ollama_data 2>/dev/null; then
    echo ""
    echo -e "${Y}  First run — Mistral 7B (~4.5 GB) will download automatically.${NC}"
    echo "  Takes 5-15 min. After that, starts are instant."
    echo ""
fi

echo -e "${B}  Starting DRAVIS...${NC}"
$DC up --build -d

echo ""
echo -e "${B}  Waiting for services...${NC}"
for i in $(seq 1 90); do
    if curl -sf http://localhost/ &>/dev/null; then break; fi
    printf "."; sleep 2
done
echo ""

echo ""
echo -e "${G}  ✅ DRAVIS is ready!${NC}"
echo ""
echo "  App:    http://localhost"
echo "  API:    http://localhost:8000"
echo "  Ollama: http://localhost:11434"
echo ""
echo "  Stop:   $DC down"
echo "  Update: git pull && $DC up --build -d"
echo ""

# Try to open browser
if command -v open &>/dev/null; then
    open http://localhost
elif command -v xdg-open &>/dev/null; then
    xdg-open http://localhost
fi
