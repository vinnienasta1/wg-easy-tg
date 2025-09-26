#!/bin/bash

# WG-Easy Telegram Bot - Скрипт остановки

set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Проверяем наличие docker-compose.yml
if [[ ! -f "docker-compose.yml" ]]; then
    print_warning "docker-compose.yml не найден!"
    exit 1
fi

print_message "Остановка WG-Easy Telegram Bot..."

# Останавливаем через docker-compose
docker-compose down

print_message "Бот остановлен!"
