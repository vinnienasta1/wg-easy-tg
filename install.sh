#!/bin/bash

# WG-Easy Telegram Bot - Установка одной командой
# Автоматическое клонирование и установка бота

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Функции для вывода сообщений
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  WG-Easy Telegram Bot Installer${NC}"
    echo -e "${BLUE}================================${NC}"
    echo
}

print_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# Функция проверки операционной системы
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="debian"
        elif [ -f /etc/redhat-release ]; then
            OS="redhat"
        elif [ -f /etc/arch-release ]; then
            OS="arch"
        else
            OS="linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        OS="unknown"
    fi
    print_message "Обнаружена ОС: $OS"
}

# Функция установки зависимостей
install_dependencies() {
    print_step "Установка системных зависимостей..."
    
    case $OS in
        "debian")
            print_message "Обновление пакетов для Debian/Ubuntu..."
            apt-get update
            
            print_message "Установка необходимых пакетов..."
            apt-get install -y curl wget git python3 python3-pip python3-venv docker.io docker-compose-plugin
            
            # Запуск Docker
            systemctl start docker
            systemctl enable docker
            ;;
        "redhat")
            print_message "Обновление пакетов для CentOS/RHEL..."
            yum update -y
            
            print_message "Установка необходимых пакетов..."
            yum install -y curl wget git python3 python3-pip docker docker-compose-plugin
            
            # Запуск Docker
            systemctl start docker
            systemctl enable docker
            ;;
        "arch")
            print_message "Обновление пакетов для Arch Linux..."
            pacman -Syu --noconfirm
            
            print_message "Установка необходимых пакетов..."
            pacman -S --noconfirm curl wget git python python-pip docker docker-compose
            
            # Запуск Docker
            systemctl start docker
            systemctl enable docker
            ;;
        "macos")
            print_message "Для macOS установите Docker Desktop с официального сайта"
            print_message "https://www.docker.com/products/docker-desktop/"
            ;;
        *)
            print_error "Неподдерживаемая операционная система!"
            exit 1
            ;;
    esac
}

# Функция проверки зависимостей
check_dependencies() {
    print_step "Проверка зависимостей..."
    
    # Проверяем Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 не установлен! Устанавливаем..."
        install_dependencies
    else
        print_message "Python 3 найден ✓"
    fi
    
    # Проверяем Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker не установлен! Устанавливаем..."
        install_dependencies
    else
        print_message "Docker найден ✓"
    fi
    
    # Проверяем Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose не установлен! Устанавливаем..."
        install_dependencies
    else
        print_message "Docker Compose найден ✓"
    fi
    
    # Проверяем права на Docker
    if ! docker ps &> /dev/null; then
        print_warning "Нет прав для работы с Docker!"
        print_message "Добавляем текущего пользователя в группу docker..."
        usermod -aG docker $USER
        print_warning "Пожалуйста, перезайдите в систему или выполните: newgrp docker"
        print_message "Затем запустите установщик снова"
        exit 1
    fi
    
    print_message "Все зависимости установлены ✓"
}

# Функция проверки WG-Easy
check_wg_easy() {
    print_step "Проверка WG-Easy..."
    
    # Проверяем, запущен ли контейнер wg-easy
    if ! docker ps --format "{{.Names}}" | grep -q "wg-easy"; then
        print_error "Контейнер wg-easy не найден или не запущен!"
        echo
        print_message "Для установки WG-Easy выполните:"
        echo "docker run -d \\"
        echo "  --name=wg-easy \\"
        echo "  -e WG_HOST=\$(curl -s ifconfig.me) \\"
        echo "  -e PASSWORD=\$(openssl rand -base64 32) \\"
        echo "  -v \$(pwd)/wg-easy:/etc/wireguard \\"
        echo "  -p 51820:51820/udp \\"
        echo "  -p 51821:51821/tcp \\"
        echo "  --cap-add=NET_ADMIN \\"
        echo "  --cap-add=SYS_MODULE \\"
        echo "  --sysctl=\"net.ipv4.conf.all.src_valid_mark=1\" \\"
        echo "  --sysctl=\"net.ipv4.ip_forward=1\" \\"
        echo "  --restart unless-stopped \\"
        echo "  weejewel/wg-easy"
        echo
        read -p "Продолжить установку бота? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_message "Установка отменена."
            exit 0
        fi
    else
        print_message "WG-Easy найден и запущен ✓"
    fi
    
    # Проверяем доступность веб-интерфейса
    WG_EASY_URL="http://localhost:51821"
    if curl -s --connect-timeout 5 "$WG_EASY_URL" > /dev/null; then
        print_message "Веб-интерфейс WG-Easy доступен ✓"
    else
        print_warning "Веб-интерфейс WG-Easy недоступен по адресу $WG_EASY_URL"
        echo
        read -p "Введите правильный URL для WG-Easy (например: http://IP:51821): " WG_EASY_URL
        if [[ -z "$WG_EASY_URL" ]]; then
            WG_EASY_URL="http://localhost:51821"
        fi
    fi
}

# Функция получения настроек от пользователя
get_user_settings() {
    print_step "Настройка бота..."
    echo
    
    # Telegram Bot Token
    while true; do
        echo -e "${CYAN}Для получения токена бота:${NC}"
        echo "1. Напишите @BotFather в Telegram"
        echo "2. Отправьте команду /newbot"
        echo "3. Следуйте инструкциям"
        echo
        read -p "Введите токен Telegram бота: " TELEGRAM_TOKEN
        if [[ -n "$TELEGRAM_TOKEN" ]]; then
            break
        else
            print_error "Токен не может быть пустым!"
        fi
    done
    
    # Admin ID
    while true; do
        echo -e "${CYAN}Для получения вашего Telegram ID:${NC}"
        echo "1. Напишите @userinfobot в Telegram"
        echo "2. Отправьте любое сообщение"
        echo "3. Скопируйте ваш ID"
        echo
        read -p "Введите ваш Telegram ID: " ADMIN_ID
        if [[ "$ADMIN_ID" =~ ^[0-9]+$ ]]; then
            break
        else
            print_error "ID должен быть числом!"
        fi
    done
    
    # WG-Easy URL
    read -p "URL WG-Easy сервера [$WG_EASY_URL]: " USER_WG_EASY_URL
    if [[ -n "$USER_WG_EASY_URL" ]]; then
        WG_EASY_URL="$USER_WG_EASY_URL"
    fi
    
    # Интервал мониторинга
    read -p "Интервал мониторинга в секундах [10]: " MONITOR_INTERVAL
    if [[ -z "$MONITOR_INTERVAL" ]]; then
        MONITOR_INTERVAL="10"
    fi
    
    echo
    print_message "Настройки сохранены ✓"
}

# Функция создания .env файла
create_env_file() {
    print_step "Создание файла конфигурации..."
    
    cat > .env << EOF
# WG-Easy Telegram Bot Configuration
TELEGRAM_TOKEN=$TELEGRAM_TOKEN
ADMIN_ID=$ADMIN_ID
WG_EASY_URL=$WG_EASY_URL
MONITOR_INTERVAL=$MONITOR_INTERVAL

# Docker настройки
COMPOSE_PROJECT_NAME=wg-easy-tg
EOF
    
    print_message "Файл .env создан ✓"
}

# Функция тестирования бота
test_bot() {
    print_step "Тестирование бота..."
    
    # Проверяем токен
    if curl -s "https://api.telegram.org/bot$TELEGRAM_TOKEN/getMe" | grep -q '"ok":true'; then
        print_message "Токен бота валидный ✓"
    else
        print_error "Неверный токен бота!"
        exit 1
    fi
    
    # Отправляем тестовое сообщение
    print_message "Отправка тестового сообщения..."
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage" \
        -d "chat_id=$ADMIN_ID" \
        -d "text=🤖 WG-Easy Bot успешно установлен и готов к работе!" \
        -d "parse_mode=Markdown" > /dev/null
    
    if [ $? -eq 0 ]; then
        print_message "Тестовое сообщение отправлено ✓"
    else
        print_warning "Не удалось отправить тестовое сообщение"
    fi
}

# Функция запуска бота
start_bot() {
    print_step "Запуск бота..."
    
    # Останавливаем существующий контейнер если есть
    docker-compose down 2>/dev/null || true
    
    # Собираем и запускаем
    docker-compose up -d --build
    
    if [ $? -eq 0 ]; then
        print_message "Бот успешно запущен ✓"
    else
        print_error "Ошибка запуска бота!"
        exit 1
    fi
}

# Функция создания скриптов управления
create_management_scripts() {
    print_step "Создание скриптов управления..."
    
    # Скрипт запуска
    cat > start_bot.sh << 'EOF'
#!/bin/bash
echo "Запуск WG-Easy Telegram Bot..."
docker-compose up -d
echo "Бот запущен!"
EOF
    
    # Скрипт остановки
    cat > stop_bot.sh << 'EOF'
#!/bin/bash
echo "Остановка WG-Easy Telegram Bot..."
docker-compose down
echo "Бот остановлен!"
EOF
    
    # Скрипт просмотра логов
    cat > logs_bot.sh << 'EOF'
#!/bin/bash
echo "Просмотр логов WG-Easy Telegram Bot..."
docker-compose logs -f wg-easy-tg-bot
EOF
    
    # Скрипт перезапуска
    cat > restart_bot.sh << 'EOF'
#!/bin/bash
echo "Перезапуск WG-Easy Telegram Bot..."
docker-compose restart wg-easy-tg-bot
echo "Бот перезапущен!"
EOF
    
    # Делаем скрипты исполняемыми
    chmod +x start_bot.sh stop_bot.sh logs_bot.sh restart_bot.sh
    
    print_message "Скрипты управления созданы ✓"
}

# Функция показа информации
show_info() {
    print_step "Информация об установке"
    echo
    echo -e "${GREEN}✅ Установка завершена успешно!${NC}"
    echo
    echo -e "${CYAN}Управление ботом:${NC}"
    echo "  ./start_bot.sh    - Запуск бота"
    echo "  ./stop_bot.sh     - Остановка бота"
    echo "  ./restart_bot.sh  - Перезапуск бота"
    echo "  ./logs_bot.sh     - Просмотр логов"
    echo
    echo -e "${CYAN}Команды бота:${NC}"
    echo "  /start      - Главное меню"
    echo "  /status     - Статус сервера"
    echo "  /speed      - Тест скорости"
    echo "  /restart    - Перезапуск WG-Easy"
    echo "  /monitoring - Управление мониторингом"
    echo
    echo -e "${CYAN}Настройки:${NC}"
    echo "  Файл конфигурации: .env"
    echo "  Логи: docker-compose logs -f wg-easy-tg-bot"
    echo
    echo -e "${YELLOW}Важно:${NC}"
    echo "  - Убедитесь, что WG-Easy запущен"
    echo "  - Проверьте настройки в файле .env"
    echo "  - Мониторинг работает автоматически"
    echo
}

# Основная функция
main() {
    print_header
    
    # Проверяем права root
    if [[ $EUID -ne 0 ]]; then
        print_error "Этот скрипт должен быть запущен с правами root!"
        print_message "Используйте: sudo $0"
        exit 1
    fi
    
    # Определяем ОС
    detect_os
    
    # Проверяем зависимости
    check_dependencies
    
    # Проверяем WG-Easy
    check_wg_easy
    
    # Получаем настройки
    get_user_settings
    
    # Создаем конфигурацию
    create_env_file
    
    # Тестируем бота
    test_bot
    
    # Запускаем бота
    start_bot
    
    # Создаем скрипты управления
    create_management_scripts
    
    # Показываем информацию
    show_info
}

# Запуск
main "$@"
