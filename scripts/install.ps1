# WG-Easy Telegram Bot Installation Script
# For Windows PowerShell

param(
    [switch]$RunCompose
)

Write-Host "🚀 Installing WG-Easy Telegram Bot..." -ForegroundColor Green

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

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item "env.example" ".env"
    Write-Host "⚠️  Please edit .env file with your configuration before running the bot." -ForegroundColor Yellow
    Write-Host "   Required: TG_BOT_TOKEN, ADMINS, WG_EASY_BASE_URL, WG_EASY_PASSWORD" -ForegroundColor Yellow
    if (-not $RunCompose) {
        exit 1
    }
}

# Create data directory
Write-Host "📁 Creating data directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "data" | Out-Null

Write-Host "✅ Installation completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your configuration" -ForegroundColor White
Write-Host "2. Run: docker compose up -d" -ForegroundColor White
Write-Host "3. Check logs: docker compose logs -f wg-telegram-bot" -ForegroundColor White
Write-Host ""

if ($RunCompose) {
    Write-Host "🚀 Starting bot with Docker Compose..." -ForegroundColor Green
    docker compose up -d
    Write-Host "✅ Bot started! Check logs with: docker compose logs -f wg-telegram-bot" -ForegroundColor Green
}
