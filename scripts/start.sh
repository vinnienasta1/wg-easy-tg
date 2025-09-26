#!/bin/bash

# WG-Easy Telegram Bot - Скрипт запуска

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
    print_message "Запустите сначала скрипт установки: ./scripts/install.sh"
    exit 1
fi

# Проверяем наличие .env файла
if [[ ! -f ".env" ]]; then
    print_warning ".env файл не найден!"
    print_message "Запустите сначала скрипт установки: ./scripts/install.sh"
    exit 1
fi

print_message "Запуск WG-Easy Telegram Bot..."

# Запускаем через docker-compose
docker-compose up -d

print_message "Бот запущен!"
print_message "Проверьте статус: docker-compose ps"
print_message "Просмотр логов: docker-compose logs -f wg-easy-tg-bot"
