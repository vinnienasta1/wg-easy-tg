#!/bin/bash

echo "🛑 Остановка WG-Easy Telegram Bot..."

# Остановить контейнеры
docker compose down

echo "✅ Бот остановлен!"
