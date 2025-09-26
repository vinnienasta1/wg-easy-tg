# WG-Easy Telegram Bot

Telegram бот для мониторинга и управления сервером WG-Easy с автоматическими уведомлениями.

## 🚀 Возможности

- 📊 **Мониторинг статуса** - проверка состояния WG-Easy каждые 10 секунд
- 🚨 **Автоматические уведомления** - алерты при недоступности сервера
- 🔄 **Управление контейнером** - перезапуск WG-Easy через бота
- 🚀 **Проверка скорости** - тест соединения с интернетом
- 🔔 **Настройка мониторинга** - включение/отключение уведомлений

## 📋 Требования

- Linux/macOS/Windows с Docker
- Запущенный WG-Easy сервер
- Telegram Bot Token (получить у @BotFather)
- Telegram ID администратора (получить у @userinfobot)

## 🛠 Быстрая установка

### Автоматическая установка (рекомендуется):

```bash
# Клонируйте репозиторий
git clone https://github.com/vinnienasta1/wg-easy-tg.git
cd wg-easy-tg

# Запустите установщик (требует sudo)
sudo chmod +x scripts/install.sh
sudo ./scripts/install.sh
```

**Установщик автоматически:**
- ✅ Проверит и установит все зависимости (Python, Docker, Docker Compose)
- ✅ Проверит статус WG-Easy
- ✅ Запросит необходимые настройки (токен бота, ID администратора)
- ✅ Создаст все конфигурационные файлы
- ✅ Протестирует бота
- ✅ Запустит бота через Docker Compose
- ✅ Создаст скрипты управления

### Ручная установка:

1. **Установите зависимости:**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install -y docker.io docker-compose-plugin python3
   
   # CentOS/RHEL
   sudo yum install -y docker docker-compose-plugin python3
   
   # Запустите Docker
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

2. **Настройте переменные окружения:**
   ```bash
   cp env.example .env
   nano .env  # отредактируйте настройки
   ```

3. **Запустите бота:**
   ```bash
   docker-compose up -d --build
   ```

## 🎮 Использование

### Команды бота:
- `/start` - Главное меню
- `/status` - Статус сервера WG-Easy
- `/speed` - Проверка скорости интернета
- `/restart` - Перезапуск контейнера WG-Easy
- `/monitoring` - Переключение мониторинга

### Кнопки интерфейса:
- 📊 **Статус** - подробная информация о сервере
- 🚀 **Скорость** - тест скорости соединения
- 🔄 **Перезагрузка** - перезапуск WG-Easy
- 🔔 **Мониторинг** - настройка уведомлений

## ⚙️ Управление

### Скрипты управления:
```bash
./start_bot.sh    # Запуск бота
./stop_bot.sh     # Остановка бота
./restart_bot.sh  # Перезапуск бота
./logs_bot.sh     # Просмотр логов
```

### Docker команды:
```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Просмотр логов
docker-compose logs -f wg-easy-tg-bot

# Перезапуск
docker-compose restart wg-easy-tg-bot
```

## 🔧 Настройка

Все настройки хранятся в файле `.env`:

```env
TELEGRAM_TOKEN=your_bot_token
ADMIN_ID=your_telegram_id
WG_EASY_URL=http://localhost:51821
MONITOR_INTERVAL=10
```

### Получение токена бота:
1. Напишите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям
4. Скопируйте полученный токен

### Получение вашего Telegram ID:
1. Напишите @userinfobot в Telegram
2. Отправьте любое сообщение
3. Скопируйте ваш ID

## 🚀 Установка WG-Easy (если не установлен)

```bash
docker run -d \
  --name=wg-easy \
  -e WG_HOST=$(curl -s ifconfig.me) \
  -e PASSWORD=$(openssl rand -base64 32) \
  -v $(pwd)/wg-easy:/etc/wireguard \
  -p 51820:51820/udp \
  -p 51821:51821/tcp \
  --cap-add=NET_ADMIN \
  --cap-add=SYS_MODULE \
  --sysctl="net.ipv4.conf.all.src_valid_mark=1" \
  --sysctl="net.ipv4.ip_forward=1" \
  --restart unless-stopped \
  weejewel/wg-easy
```

## 📝 Лицензия

MIT License

## 🤝 Поддержка

Если у вас есть вопросы или проблемы:
- Создайте Issue в репозитории
- Свяжитесь с автором

---

⭐ **Если проект вам понравился, поставьте звезду!**
