#!/bin/bash
# DRAVIS Installer for macOS
# Run: Open Terminal, then run: bash install-dravis-mac.sh

set -e

echo "=========================================="
echo "    DRAVIS AI Installer for macOS         "
echo "=========================================="
echo ""

# Check for Docker
echo "Checking for Docker..."
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker Desktop not found."
    echo "Opening Docker download page..."
    open "https://www.docker.com/products/docker-desktop"
    echo "Please install Docker Desktop, then re-run this script."
    exit 1
fi
echo "[OK] Docker found."

# Check for Git
echo "Checking for Git..."
if ! command -v git &> /dev/null; then
    echo "[ERROR] Git not found. Installing via Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew first..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install git
fi
echo "[OK] Git found."
echo ""

# Clone or update the repo
TARGET_DIR="$HOME/dravis"

if [ -d "$TARGET_DIR" ]; then
    echo "DRAVIS folder already exists. Updating to latest version..."
    cd "$TARGET_DIR"
    git pull
else
    echo "Cloning DRAVIS repository..."
    git clone https://github.com/Khushi0231/major.git "$TARGET_DIR"
    cd "$TARGET_DIR"
fi

echo ""
echo "Starting DRAVIS..."
echo "(First launch downloads the Mistral AI model — about 4.5GB. Please be patient!)"
echo ""

# Start the application
docker-compose up -d

echo ""
echo "Waiting for DRAVIS to come online..."
sleep 15

# Open in browser
open http://localhost:8080

echo ""
echo "=========================================="
echo " SUCCESS! DRAVIS is running!"
echo " Visit: http://localhost:8080"
echo "=========================================="
