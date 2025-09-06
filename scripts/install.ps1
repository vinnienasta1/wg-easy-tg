# WG-Easy Telegram Bot Installation Script
# For Windows PowerShell

param(
    [switch]$RunCompose
)

Write-Host "🚀 Installing WG-Easy Telegram Bot..." -ForegroundColor Green
Write-Host ""

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    Write-Host "   Visit: https://docs.docker.com/desktop/windows/install/" -ForegroundColor Yellow
    exit 1
}

# Check if Docker Compose is available
try {
    docker compose version | Out-Null
    Write-Host "✅ Docker Compose is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not available. Please update Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🧹 Cleaning up existing bot containers..." -ForegroundColor Yellow
try {
    docker stop wg-telegram-bot 2>$null
    docker rm wg-telegram-bot 2>$null
    Write-Host "✅ Bot cleanup completed" -ForegroundColor Green
} catch {
    Write-Host "ℹ️  No existing bot containers to clean up" -ForegroundColor Cyan
}
Write-Host ""

Write-Host "📝 Please provide the following configuration:" -ForegroundColor Cyan
Write-Host ""

# Telegram Bot Token
do {
    $TG_BOT_TOKEN = Read-Host "🤖 Enter your Telegram Bot Token (from @BotFather)"
    if ($TG_BOT_TOKEN -match '^\d+:[A-Za-z0-9_-]+$') {
        break
    } else {
        Write-Host "❌ Invalid bot token format. Please try again." -ForegroundColor Red
    }
} while ($true)

# Admin IDs
Write-Host ""
$ADMIN_IDS = Read-Host "👤 Enter admin Telegram IDs (comma-separated, e.g., 123456789,987654321)"

# Server IP
do {
    $SERVER_IP = Read-Host "🌐 Enter your server IP address"
    if ($SERVER_IP -match '^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$') {
        break
    } else {
        Write-Host "❌ Invalid IP address format. Please try again." -ForegroundColor Red
    }
} while ($true)

# WG-Easy Port
$WG_PORT = Read-Host "🔌 Enter WG-Easy web interface port (default: 51821)"
if ([string]::IsNullOrEmpty($WG_PORT)) {
    $WG_PORT = "51821"
}

# WG-Easy Username
$WG_USERNAME = Read-Host "👤 Enter WG-Easy username (default: admin)"
if ([string]::IsNullOrEmpty($WG_USERNAME)) {
    $WG_USERNAME = "admin"
}

# WG-Easy Password
do {
    $WG_PASSWORD = Read-Host "🔐 Enter WG-Easy password" -AsSecureString
    $WG_PASSWORD_PLAIN = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($WG_PASSWORD))
    if (-not [string]::IsNullOrEmpty($WG_PASSWORD_PLAIN)) {
        break
    } else {
        Write-Host "❌ Password cannot be empty. Please try again." -ForegroundColor Red
    }
} while ($true)

# SSL Verification
Write-Host ""
$SSL_VERIFY = Read-Host "🔒 Use SSL verification? (y/n, default: y)"
if ([string]::IsNullOrEmpty($SSL_VERIFY)) {
    $SSL_VERIFY = "y"
}

if ($SSL_VERIFY -match '^[Yy]$') {
    $WG_VERIFY_SSL = "true"
} else {
    $WG_VERIFY_SSL = "false"
}

# Create .env file
Write-Host ""
Write-Host "📝 Creating .env file..." -ForegroundColor Yellow
$envContent = @"
TG_BOT_TOKEN=$TG_BOT_TOKEN
ADMINS=$ADMIN_IDS
WG_EASY_BASE_URL=http://$SERVER_IP:$WG_PORT
WG_EASY_USERNAME=$WG_USERNAME
WG_EASY_PASSWORD=$WG_PASSWORD_PLAIN
WG_EASY_VERIFY_SSL=$WG_VERIFY_SSL
DB_PATH=./data/bot.db
LOG_LEVEL=INFO
"@
$envContent | Out-File -FilePath ".env" -Encoding UTF8

# Docker-compose.yml is ready to use

# Create data directory
Write-Host "📁 Creating data directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "data" | Out-Null

Write-Host ""
Write-Host "✅ Installation completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Configuration saved:" -ForegroundColor Cyan
Write-Host "   Bot Token: $($TG_BOT_TOKEN.Substring(0, 10))..." -ForegroundColor White
Write-Host "   Admin IDs: $ADMIN_IDS" -ForegroundColor White
Write-Host "   Server IP: $SERVER_IP" -ForegroundColor White
Write-Host "   WG-Easy Port: $WG_PORT" -ForegroundColor White
Write-Host "   WG-Easy Username: $WG_USERNAME" -ForegroundColor White
Write-Host "   SSL Verification: $WG_VERIFY_SSL" -ForegroundColor White
Write-Host ""

if ($RunCompose) {
    Write-Host "🚀 Starting bot..." -ForegroundColor Green
    docker compose up -d --build
    
    Write-Host ""
    Write-Host "✅ Bot started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Useful commands:" -ForegroundColor Cyan
    Write-Host "   View logs: docker compose logs -f wg-telegram-bot" -ForegroundColor White
    Write-Host "   Stop bot: docker compose down" -ForegroundColor White
    Write-Host "   Restart: docker compose restart" -ForegroundColor White
    Write-Host ""
    Write-Host "🎉 Your WG-Easy Telegram Bot is ready to use!" -ForegroundColor Green
} else {
    Write-Host "📋 Next steps:" -ForegroundColor Cyan
    Write-Host "1. Run: docker compose up -d" -ForegroundColor White
    Write-Host "2. Check logs: docker compose logs -f wg-telegram-bot" -ForegroundColor White
    Write-Host ""
    Write-Host "🎉 Configuration completed! Run the bot when ready." -ForegroundColor Green
}
