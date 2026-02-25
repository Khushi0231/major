#!/bin/bash
# DRAVIS Installer for Linux
# Run: bash install-dravis-linux.sh

set -e

echo "=========================================="
echo "    DRAVIS AI Installer for Linux         "
echo "=========================================="
echo ""

# Check for Docker
echo "Checking for Docker..."
if ! command -v docker &> /dev/null; then
    echo "[INFO] Docker not found. Attempting to install..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "[OK] Docker installed. Please log out and log back in, then re-run this script."
    exit 0
fi
echo "[OK] Docker found."

# Check for docker-compose
echo "Checking for docker-compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "[INFO] docker-compose not found. Installing..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
         -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi
echo "[OK] docker-compose found."

# Check for Git
echo "Checking for Git..."
if ! command -v git &> /dev/null; then
    sudo apt-get install -y git 2>/dev/null || sudo yum install -y git 2>/dev/null || sudo dnf install -y git 2>/dev/null
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

# Try to open browser
xdg-open http://localhost:8080 2>/dev/null || echo "Open your browser to: http://localhost:8080"

echo ""
echo "=========================================="
echo " SUCCESS! DRAVIS is running!"
echo " Visit: http://localhost:8080"
echo "=========================================="
