#!/usr/bin/env python3
"""
WG-Easy Telegram Bot с мониторингом (финальная версия)
Управление сервером wg-easy через Telegram + автоматический мониторинг
Оптимизировано для слабых машин
"""

import subprocess
import requests
import time
import json
import logging
import threading
import os
from typing import Optional, Dict, Any
from datetime import datetime

# Настройки из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
WG_EASY_URL = os.getenv("WG_EASY_URL", "http://localhost:1228")
MONITOR_INTERVAL = int(os.getenv("MONITOR_INTERVAL", "10"))

# Настройка логирования (только ошибки)
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class WGEasyBot:
    """Класс для управления WG-Easy через Telegram с мониторингом"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 3  # Очень короткий таймаут
        self.monitoring_enabled = True
        self.last_status = None
        self.monitor_thread = None
        self.stop_monitoring = False
        
    def send_message(self, chat_id: int, text: str, reply_markup: Optional[Dict] = None) -> bool:
        """Отправить сообщение в Telegram"""
        try:
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            if reply_markup:
                data["reply_markup"] = json.dumps(reply_markup)
            
            response = self.session.post(f"{BASE_URL}/sendMessage", data=data, timeout=5)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            return False
    
    def check_wg_easy_status(self) -> tuple[bool, str]:
        """Проверить статус wg-easy сервера (только контейнер)"""
        try:
            # Проверяем только статус контейнера (быстро и надежно)
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=wg-easy", "--format", "{{.Status}}"], 
                capture_output=True, text=True, timeout=2
            )
            container_status = result.stdout.strip()
            
            if not container_status or "up" not in container_status.lower():
                return False, "Контейнер не запущен"
            
            # Дополнительная проверка - есть ли процесс wg-easy
            result2 = subprocess.run(
                ["docker", "exec", "wg-easy", "ps", "aux"], 
                capture_output=True, text=True, timeout=2
            )
            
            if result2.returncode != 0:
                return False, "Контейнер не отвечает"
            
            return True, "Сервер работает нормально"
            
        except Exception as e:
            logger.error(f"Ошибка проверки статуса: {e}")
            return False, f"Ошибка проверки: {str(e)}"
    
    def get_server_status(self) -> str:
        """Получить подробный статус сервера"""
        try:
            # Проверяем статус контейнера
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=wg-easy", "--format", "{{.Status}}"], 
                capture_output=True, text=True, timeout=3
            )
            container_status = result.stdout.strip() or "Не запущен"
            
            # Проверяем доступность веб-интерфейса (с таймаутом)
            web_status = "❌ Недоступен"
            try:
                response = requests.get(f"{WG_EASY_URL}/", timeout=2)
                if response.status_code == 200:
                    web_status = "✅ Доступен"
            except:
                pass
            
            # Проверяем использование ресурсов
            memory_usage = self._get_memory_usage()
            disk_usage = self._get_disk_usage()
            
            # Проверяем мониторинг
            monitor_status = "✅ Активен" if self.monitoring_enabled else "❌ Отключен"
            
            return f"""🖥️ *Статус сервера wg-easy*

🐳 *Контейнер*: {container_status}
🌐 *Веб-интерфейс*: {web_status}
📊 *Память*: {memory_usage}
💾 *Диск*: {disk_usage}
🔔 *Мониторинг*: {monitor_status}
🔗 *URL*: {WG_EASY_URL}"""
            
        except Exception as e:
            logger.error(f"Ошибка получения статуса: {e}")
            return f"❌ Ошибка получения статуса: {str(e)}"
    
    def get_speed_test(self) -> str:
        """Проверить скорость интернета (упрощенная версия)"""
        try:
            # Простая проверка через ping
            result = subprocess.run(
                ["ping", "-c", "2", "8.8.8.8"], 
                capture_output=True, text=True, timeout=8
            )
            if result.returncode == 0:
                return """🚀 *Тест скорости*

✅ *Соединение стабильное*
📡 *Сервер*: {WG_EASY_URL}
🏓 *Ping до Google DNS*: OK"""
            else:
                return "❌ Ошибка проверки скорости"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def restart_container(self) -> str:
        """Перезапустить контейнер"""
        try:
            logger.error("Перезапуск контейнера wg-easy")
            subprocess.run(["docker", "restart", "wg-easy"], check=True, timeout=30)
            time.sleep(2)
            
            # Проверяем статус после перезапуска
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=wg-easy", "--format", "{{.Status}}"], 
                capture_output=True, text=True, timeout=3
            )
            status = result.stdout.strip() or "Статус неизвестен"
            
            return f"✅ *Контейнер перезапущен!*\n\nСтатус: {status}"
            
        except Exception as e:
            logger.error(f"Ошибка перезапуска: {e}")
            return f"❌ Ошибка перезапуска: {str(e)}"
    
    def toggle_monitoring(self) -> str:
        """Переключить мониторинг"""
        self.monitoring_enabled = not self.monitoring_enabled
        status = "включен" if self.monitoring_enabled else "отключен"
        return f"🔔 Мониторинг {status}"
    
    def _get_memory_usage(self) -> str:
        """Получить использование памяти"""
        try:
            result = subprocess.run(["free", "-h"], capture_output=True, text=True, timeout=2)
            lines = result.stdout.split('\n')[1].split()
            used = lines[2]
            total = lines[1]
            return f"{used}/{total}"
        except:
            return "N/A"
    
    def _get_disk_usage(self) -> str:
        """Получить использование диска"""
        try:
            result = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, timeout=2)
            lines = result.stdout.split('\n')[1].split()
            used = lines[2]
            total = lines[1]
            return f"{used}/{total}"
        except:
            return "N/A"
    
    def start_monitoring(self):
        """Запустить мониторинг в отдельном потоке"""
        if self.monitor_thread and self.monitor_thread.is_alive():
            return
        
        self.stop_monitoring = False
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("Мониторинг запущен")
    
    def stop_monitoring_thread(self):
        """Остановить мониторинг"""
        self.stop_monitoring = True
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print("Мониторинг остановлен")
    
    def _monitor_loop(self):
        """Основной цикл мониторинга"""
        print("Запуск цикла мониторинга")
        
        while not self.stop_monitoring and self.monitoring_enabled:
            try:
                is_healthy, status_msg = self.check_wg_easy_status()
                current_time = datetime.now().strftime("%H:%M:%S")
                
                # Если статус изменился с рабочего на нерабочий
                if self.last_status is True and not is_healthy:
                    alert_message = f"""🚨 *АЛЕРТ: WG-Easy недоступен!*

⏰ *Время*: {current_time}
❌ *Статус*: {status_msg}
🔧 *Рекомендация*: Проверьте контейнер и перезапустите при необходимости"""
                    
                    print(f"WG-Easy недоступен: {status_msg}")
                    self.send_message(ADMIN_ID, alert_message)
                
                # Если статус изменился с нерабочего на рабочий
                elif self.last_status is False and is_healthy:
                    recovery_message = f"""✅ *ВОССТАНОВЛЕНИЕ: WG-Easy работает!*

⏰ *Время*: {current_time}
✅ *Статус*: {status_msg}
🎉 *Сервер восстановлен*"""
                    
                    print(f"WG-Easy восстановлен: {status_msg}")
                    self.send_message(ADMIN_ID, recovery_message)
                
                self.last_status = is_healthy
                
                # Ждем перед следующей проверкой
                time.sleep(MONITOR_INTERVAL)
                
            except Exception as e:
                logger.error(f"Ошибка в цикле мониторинга: {e}")
                time.sleep(MONITOR_INTERVAL)

def create_main_menu() -> Dict[str, Any]:
    """Создать главное меню"""
    return {
        "inline_keyboard": [
            [{"text": "📊 Статус", "callback_data": "status"}],
            [{"text": "🚀 Скорость", "callback_data": "speed"}],
            [{"text": "🔄 Перезагрузка", "callback_data": "restart"}],
            [{"text": "🔔 Мониторинг", "callback_data": "monitoring"}]
        ]
    }

def create_restart_confirmation() -> Dict[str, Any]:
    """Создать меню подтверждения перезагрузки"""
    return {
        "inline_keyboard": [
            [{"text": "✅ Да, перезагрузить", "callback_data": "restart_confirm"}],
            [{"text": "❌ Отмена", "callback_data": "cancel"}]
        ]
    }

def handle_message(bot: WGEasyBot, message: Dict[str, Any]) -> None:
    """Обработать сообщение"""
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    
    if chat_id != ADMIN_ID:
        bot.send_message(chat_id, "❌ Доступ запрещен")
        return
    
    if text == "/start":
        keyboard = create_main_menu()
        bot.send_message(chat_id, "🤖 *WG-Easy Bot с мониторингом*\n\nВыберите действие:", keyboard)
    
    elif text == "/status":
        status = bot.get_server_status()
        bot.send_message(chat_id, status)
    
    elif text == "/speed":
        speed = bot.get_speed_test()
        bot.send_message(chat_id, speed)
    
    elif text == "/restart":
        result = bot.restart_container()
        bot.send_message(chat_id, result)
    
    elif text == "/monitoring":
        monitor_status = bot.toggle_monitoring()
        bot.send_message(chat_id, monitor_status)

def handle_callback(bot: WGEasyBot, callback_query: Dict[str, Any]) -> None:
    """Обработать нажатие кнопки"""
    chat_id = callback_query["message"]["chat"]["id"]
    data = callback_query["data"]
    
    if chat_id != ADMIN_ID:
        bot.send_message(chat_id, "❌ Доступ запрещен")
        return
    
    if data == "status":
        status = bot.get_server_status()
        bot.send_message(chat_id, status)
        
    elif data == "speed":
        speed = bot.get_speed_test()
        bot.send_message(chat_id, speed)
        
    elif data == "restart":
        keyboard = create_restart_confirmation()
        bot.send_message(
            chat_id, 
            "🔄 *Вы уверены?*\n\nЭто перезапустит контейнер wg-easy и временно прервет VPN соединения.", 
            keyboard
        )
        
    elif data == "restart_confirm":
        result = bot.restart_container()
        bot.send_message(chat_id, result)
        
    elif data == "cancel":
        bot.send_message(chat_id, "❌ Перезагрузка отменена")
    
    elif data == "monitoring":
        monitor_status = bot.toggle_monitoring()
        bot.send_message(chat_id, monitor_status)
    
    # Показываем главное меню после каждого действия
    keyboard = create_main_menu()
    bot.send_message(chat_id, "🤖 *WG-Easy Bot с мониторингом*\n\nВыберите действие:", keyboard)

def main():
    """Основная функция"""
    print("Запуск WG-Easy Telegram Bot с мониторингом...")
    
    # Проверяем обязательные переменные окружения
    if not TELEGRAM_TOKEN:
        print("ОШИБКА: TELEGRAM_TOKEN не установлен!")
        exit(1)
    
    if not ADMIN_ID:
        print("ОШИБКА: ADMIN_ID не установлен!")
        exit(1)
    
    bot = WGEasyBot()
    last_update_id = 0
    
    # Запускаем мониторинг
    bot.start_monitoring()
    
    try:
        while True:
            try:
                # Получаем обновления
                response = bot.session.get(
                    f"{BASE_URL}/getUpdates", 
                    params={"offset": last_update_id + 1, "timeout": 30}
                )
                response.raise_for_status()
                updates = response.json()
                
                if updates["ok"]:
                    for update in updates["result"]:
                        last_update_id = update["update_id"]
                        
                        if "message" in update:
                            handle_message(bot, update["message"])
                        elif "callback_query" in update:
                            handle_callback(bot, update["callback_query"])
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Ошибка в основном цикле: {e}")
                time.sleep(5)
                
    except KeyboardInterrupt:
        print("Получен сигнал остановки...")
    finally:
        bot.stop_monitoring_thread()
        print("Бот остановлен")

if __name__ == "__main__":
    main()
