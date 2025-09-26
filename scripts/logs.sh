#!/bin/bash

# WG-Easy Telegram Bot - Скрипт просмотра логов

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

print_message "Просмотр логов WG-Easy Telegram Bot..."
print_message "Для выхода нажмите Ctrl+C"

# Показываем логи
docker-compose logs -f wg-easy-tg-bot
