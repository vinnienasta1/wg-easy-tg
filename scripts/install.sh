#!/bin/bash

# WG-Easy Telegram Bot Installation Script
# For Linux/macOS

set -e

echo "🚀 Installing WG-Easy Telegram Bot..."

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

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration before running the bot."
    echo "   Required: TG_BOT_TOKEN, ADMINS, WG_EASY_BASE_URL, WG_EASY_PASSWORD"
    exit 1
fi

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data

# Make scripts executable
echo "🔧 Setting up scripts..."
chmod +x start_bot.sh stop_bot.sh

echo "✅ Installation completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run: ./start_bot.sh"
echo "3. Check logs: docker compose logs -f wg-telegram-bot"
echo ""
echo "🛑 To stop: ./stop_bot.sh"
