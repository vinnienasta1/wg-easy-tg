# WG-Easy Telegram Bot - Установка одной командой

## 🚀 Установка одной командой через curl:

### Linux/macOS:
```bash
curl -fsSL https://raw.githubusercontent.com/vinnienasta1/wg-easy-tg/main/install.sh | sudo bash
```

### Windows (PowerShell):
```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/vinnienasta1/wg-easy-tg/main/install.sh" -OutFile "install.sh"; bash install.sh
```

## 📋 Что делает команда:

1. **Скачивает установщик** с GitHub
2. **Автоматически определяет ОС** (Debian/Ubuntu, CentOS/RHEL, Arch Linux, macOS)
3. **Устанавливает зависимости** (Python, Docker, Docker Compose)
4. **Проверяет WG-Easy** и дает инструкции по установке
5. **Интерактивно запрашивает настройки**:
   - Токен Telegram бота
   - ID администратора
   - URL WG-Easy сервера
   - Интервал мониторинга
6. **Тестирует бота** перед запуском
7. **Запускает бота** через Docker Compose
8. **Создает скрипты управления**

## 🎯 Альтернативные способы установки:

### Через git clone:
```bash
git clone https://github.com/vinnienasta1/wg-easy-tg.git
cd wg-easy-tg
sudo bash install.sh
```

### Через wget:
```bash
wget -O install.sh https://raw.githubusercontent.com/vinnienasta1/wg-easy-tg/main/install.sh
sudo bash install.sh
```

## ⚙️ После установки:

### Управление ботом:
```bash
./start_bot.sh    # Запуск
./stop_bot.sh     # Остановка
./restart_bot.sh  # Перезапуск
./logs_bot.sh     # Просмотр логов
```

### Команды бота:
- `/start` - Главное меню
- `/status` - Статус сервера WG-Easy
- `/speed` - Проверка скорости интернета
- `/restart` - Перезапуск контейнера WG-Easy
- `/monitoring` - Переключение мониторинга

## 🔧 Требования:

- Linux/macOS/Windows с Docker
- Права root/sudo
- Запущенный WG-Easy сервер (или инструкции по установке)
- Telegram Bot Token (от @BotFather)
- Telegram ID администратора (от @userinfobot)

## 📝 Лицензия:

MIT License
