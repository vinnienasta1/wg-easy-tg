#!/bin/bash

# WG-Easy Telegram Bot Installation Script
# For Linux/macOS

set -e

echo "🚀 Installing WG-Easy Telegram Bot..."
echo ""

# Check if we're already in the project directory
if [ -f "scripts/install.sh" ] && [ -f "docker-compose.yml" ]; then
    echo "✅ Already in the project directory"
    echo ""
else
    echo "❌ Please run this script from the project directory or use the full installation command:"
    echo "   bash -lc 'rm -rf wg-easy-tg && git clone https://github.com/vinnienasta1/wg-easy-tg.git && cd wg-easy-tg && bash scripts/install.sh'"
    exit 1
fi

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

аляешь все контейнеры?# Clean up any existing bot containers only
echo "🧹 Cleaning up existing bot containers..."
docker stop wg-telegram-bot 2>/dev/null || true
docker rm wg-telegram-bot 2>/dev/null || true
echo "✅ Bot cleanup completed"
echo ""

# Interactive configuration
echo "📝 Please provide the following configuration:"
echo ""

# Telegram Bot Token
while true; do
    read -p "🤖 Enter your Telegram Bot Token (from @BotFather): " TG_BOT_TOKEN
    if [[ $TG_BOT_TOKEN =~ ^[0-9]+:[A-Za-z0-9_-]+$ ]]; then
        break
    else
        echo "❌ Invalid bot token format. Please try again."
    fi
done

# Admin IDs
echo ""
echo "👤 Enter admin Telegram IDs (comma-separated, e.g., 123456789,987654321):"
read -p "Admin IDs: " ADMIN_IDS

# Server IP
while true; do
    read -p "🌐 Enter your server IP address: " SERVER_IP
    if [[ $SERVER_IP =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        break
    else
        echo "❌ Invalid IP address format. Please try again."
    fi
done

# WG-Easy Port
read -p "🔌 Enter WG-Easy web interface port (default: 51821): " WG_PORT
WG_PORT=${WG_PORT:-51821}

# WG-Easy Username
read -p "👤 Enter WG-Easy username (default: admin): " WG_USERNAME
WG_USERNAME=${WG_USERNAME:-admin}

# WG-Easy Password
while true; do
    read -s -p "🔐 Enter WG-Easy password: " WG_PASSWORD
    echo ""
    if [ -n "$WG_PASSWORD" ]; then
        break
    else
        echo "❌ Password cannot be empty. Please try again."
    fi
done

# SSL Verification
echo ""
read -p "🔒 Use SSL verification? (y/n, default: y): " SSL_VERIFY
SSL_VERIFY=${SSL_VERIFY:-y}

if [[ $SSL_VERIFY =~ ^[Yy]$ ]]; then
    WG_VERIFY_SSL="true"
else
    WG_VERIFY_SSL="false"
fi

# Create .env file
echo ""
echo "📝 Creating .env file..."
cat > .env << EOF
TG_BOT_TOKEN=$TG_BOT_TOKEN
ADMINS=$ADMIN_IDS
WG_EASY_BASE_URL=http://$SERVER_IP:$WG_PORT
WG_EASY_USERNAME=$WG_USERNAME
WG_EASY_PASSWORD=$WG_PASSWORD
WG_EASY_VERIFY_SSL=$WG_VERIFY_SSL
DB_PATH=./data/bot.db
LOG_LEVEL=INFO
EOF

# Docker-compose.yml is ready to use

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data

# Make scripts executable
echo "🔧 Setting up scripts..."
chmod +x start_bot.sh stop_bot.sh

echo ""
echo "✅ Installation completed!"
echo ""
echo "📋 Configuration saved:"
echo "   Bot Token: ${TG_BOT_TOKEN:0:10}..."
echo "   Admin IDs: $ADMIN_IDS"
echo "   Server IP: $SERVER_IP"
echo "   WG-Easy Port: $WG_PORT"
echo "   WG-Easy Username: $WG_USERNAME"
echo "   SSL Verification: $WG_VERIFY_SSL"
echo ""
echo "🚀 Starting bot..."
docker compose up -d --build

echo ""
echo "✅ Bot started successfully!"
echo ""
echo "📊 Useful commands:"
echo "   View logs: docker compose logs -f wg-telegram-bot"
echo "   Stop bot: ./stop_bot.sh"
echo "   Restart: docker compose restart"
echo ""
echo "🎉 Your WG-Easy Telegram Bot is ready to use!"
