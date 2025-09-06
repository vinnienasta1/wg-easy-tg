# WG-Easy Telegram Bot

Telegram бот для управления WG-Easy VPN сервером. Поддерживает роли Админа и Клиента, красивые кнопки, запуск в отдельном контейнере Docker.

## 🚀 Возможности

### Для пользователей:
- 📥 Скачивание конфигурации WireGuard
- 🔳 Получение QR-кода для быстрого подключения
- 📘 Инструкция по подключению
- ⏳ Проверка срока действия

### Для администраторов:
- 📊 Мониторинг статуса WG-Easy сервера
- ➕ Добавление новых клиентов
- 🔁 Продление срока действия (в разработке)
- 🗑 Удаление клиентов (в разработке)
- 📣 Рассылка сообщений (в разработке)

## 🛠 Технологии

- **Python 3.12** - основной язык
- **aiogram 3.22** - Telegram Bot API
- **Docker & Docker Compose** - контейнеризация
- **SQLite** - база данных
- **httpx** - HTTP клиент для WG-Easy API
- **qrcode** - генерация QR-кодов

## 🚀 Быстрая установка

### Linux/macOS:
```bash
# Полная установка с клонированием (рекомендуется)
bash -lc 'rm -rf wg-easy-tg && git clone https://github.com/vinnienasta1/wg-easy-tg.git && cd wg-easy-tg && bash scripts/install.sh'

# Или используйте скрипт полной установки
curl -sSL https://raw.githubusercontent.com/vinnienasta1/wg-easy-tg/main/scripts/full-install.sh | bash
```

### Windows (PowerShell):
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command "if (Test-Path 'wg-easy-tg') { Remove-Item -Recurse -Force 'wg-easy-tg' }; git clone https://github.com/vinnienasta1/wg-easy-tg.git; Set-Location wg-easy-tg; powershell -File scripts/install.ps1 -RunCompose"
```

> **💡 Интерактивная установка:** Скрипты автоматически запросят у вас все необходимые данные:
> - 🤖 Токен Telegram бота (от @BotFather)
> - 👤 ID администраторов
> - 🌐 IP адрес сервера
> - 🔌 Порт веб-интерфейса WG-Easy (по умолчанию: 51821)
> - 🔐 Данные для подключения к WG-Easy
> - 🔒 Настройки SSL
> 
> **⚠️ Важно:** Убедитесь, что WG-Easy уже установлен и работает на вашем сервере!

## 📋 Ручная установка

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/vinnienasta1/wg-easy-tg.git
   cd wg-easy-tg
   ```

2. **Настройте переменные окружения:**
   ```bash
   cp env.example .env
   # Отредактируйте .env файл с вашими настройками
   ```

3. **Запустите бота:**
   ```bash
   chmod +x start_bot.sh
   ./start_bot.sh
   ```

## Управление

```bash
# Запуск
./start_bot.sh

# Остановка
./stop_bot.sh

# Просмотр логов
docker-compose logs -f wg-telegram-bot
```

## ⚙️ Переменные окружения

См. `env.example` для полного списка переменных.

### Обязательные:
- `TG_BOT_TOKEN` - токен Telegram бота (получить у [@BotFather](https://t.me/BotFather))
- `ADMINS` - список ID администраторов через запятую
- `WG_EASY_BASE_URL` - URL WG-Easy сервера (например: `http://IP:51821`)
- `WG_EASY_PASSWORD` - пароль WG-Easy

### Важные замечания:
- Указывайте `WG_EASY_BASE_URL` с протоколом: `http://IP:PORT` или `https://vpn.example.com`
- Порт 51820 — это порт WireGuard, а веб-интерфейс WG-Easy обычно на 51821 (но может быть любой)
- Если у WG-Easy самоподписанный сертификат, добавьте `WG_EASY_VERIFY_SSL=false`
- **WG-Easy должен быть установлен отдельно** - бот только подключается к нему

## 🏗 Структура проекта

```
app/
├── handlers/        # обработчики бота
│   ├── admin.py     # админские функции
│   ├── client.py    # клиентские функции
│   └── common.py    # общие команды
├── keyboards/       # клавиатуры и кнопки
├── services/        # интеграции
│   ├── wg_easy_client.py  # клиент WG-Easy API
│   └── qr.py        # генерация QR-кодов
├── config.py        # настройки из ENV
├── db.py           # работа с базой данных
├── logger.py       # логирование
└── main.py         # точка входа
```

## 🧪 Разработка без Docker

```bash
# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск бота
python -m app.main
```

## 🚀 Деплой на сервер

1. **Клонируйте репозиторий на сервер:**
   ```bash
   git clone https://github.com/vinnienasta1/wg-easy-tg.git
   cd wg-easy-tg
   ```

2. **Настройте переменные окружения:**
   ```bash
   cp env.example .env
   nano .env  # отредактируйте настройки
   ```

3. **Запустите через Docker Compose:**
   ```bash
   docker compose up -d
   ```

4. **Проверьте статус:**
   ```bash
   docker compose ps
   docker compose logs -f wg-telegram-bot
   docker compose logs -f tg_bot
   ```

## 📝 Лицензия

MIT License - см. файл [LICENSE](LICENSE) для деталей.

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/AmazingFeature`)
3. Зафиксируйте изменения (`git commit -m 'Add some AmazingFeature'`)
4. Отправьте в ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📞 Поддержка

Если у вас есть вопросы или проблемы:
- Создайте [Issue](https://github.com/vinnienasta1/wg-easy-tg/issues)
- Или свяжитесь с автором

---

⭐ **Если проект вам понравился, поставьте звезду!**
