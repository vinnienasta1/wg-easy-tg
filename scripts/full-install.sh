#!/bin/bash

# WG-Easy Telegram Bot Full Installation Script
# For Linux/macOS - includes cloning from GitHub

set -e

echo "🚀 Full Installation of WG-Easy Telegram Bot..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Remove existing directory if it exists
if [ -d "wg-easy-tg" ]; then
    echo "🗑️  Removing existing wg-easy-tg directory..."
    rm -rf wg-easy-tg
fi

# Clone repository
echo "📥 Cloning repository from GitHub..."
git clone https://github.com/vinnienasta1/wg-easy-tg.git
cd wg-easy-tg

echo "✅ Repository cloned successfully"
echo ""

# Run the installation script
echo "🔧 Running installation script..."
bash scripts/install.sh
