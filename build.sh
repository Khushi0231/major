#!/bin/bash

# Docker build script for dravis-app
# This script builds the Docker image
# NOTE: Must be run on a system with Docker daemon running (not in GitHub Codespace)

set -e

echo "Building dravis-app Docker image..."
echo "Note: This command must be run on your local machine or a system with Docker available."
echo ""

if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    echo "Please install Docker Desktop or Docker Engine to build this image"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "Error: Docker daemon is not running"
    echo "Please start Docker and try again"
    exit 1
fi

echo "Building Docker image..."
docker build -t dravis-app .

echo ""
echo "✓ Build complete! Image 'dravis-app' is ready."
echo ""
echo "Next steps:"
echo "1. Run the container: docker run -p 8000:8000 dravis-app"
echo "2. Access the app at: http://localhost:8000"
echo ""
echo "Or use Docker Compose:"
echo "  docker-compose up --build"
