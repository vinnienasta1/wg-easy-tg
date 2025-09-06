#!/bin/bash

echo "🚀 Запуск WG-Easy Telegram Bot..."

# Остановить существующие контейнеры
echo "Остановка существующих контейнеров..."
docker compose down

# Создать директорию для данных
mkdir -p data

# Запустить контейнеры
echo "Запуск контейнеров..."
docker compose up -d --build

# Показать статус
echo "Статус контейнеров:"
docker compose ps

echo "✅ Бот запущен!"
echo "📊 Логи бота: docker compose logs -f wg-telegram-bot"
echo "🛑 Остановка: docker compose down"
