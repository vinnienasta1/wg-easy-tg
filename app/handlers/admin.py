import logging
import subprocess
import os
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from ..config import settings
from ..keyboards.main_menu import admin_menu, clients_list_keyboard, client_management_keyboard, subscription_keyboard
from ..services.wg_easy_client import WGEasyClient
from ..db import upsert_client, get_client_by_tg, get_all_clients, get_client_by_peer_id, delete_client, now_ts


router = Router()
logger = logging.getLogger(__name__)


class AdminStates(StatesGroup):
    pass


def is_admin(user_id: int) -> bool:
    return user_id in settings.admins


async def check_admin_rights(call: CallbackQuery) -> bool:
    """Проверка прав администратора"""
    if not is_admin(call.from_user.id):
        await call.answer("Нет прав доступа", show_alert=True)
        return False
    return True


@router.callback_query(F.data == "admin:monitor")
async def admin_monitor(call: CallbackQuery) -> None:
    if not await check_admin_rights(call):
        return
    
    try:
        async with WGEasyClient() as api:
            await api.login()
            status = await api.get_status()
            
            # Проверяем обновления
            current_version = status.get("version", "unknown")
            update_info = await api.check_for_updates(current_version)
            
    except Exception as e:
        logger.error(f"Ошибка получения статуса WG-Easy: {e}")
        await call.message.edit_text(
            f"❌ Не удалось получить статус WG-Easy:\n<code>{str(e)}</code>",
            reply_markup=admin_menu(),
        )
        await call.answer()
        return
    
    # Обработка разных форматов ответа
    if status.get("status") == "online":
        version = status.get("version", "unknown")
        update_available = status.get("updateAvailable", False)
        insecure = status.get("insecure", False)
        
        text = (
            "📊 <b>Статус WG-Easy</b>\n\n"
            f"✅ Сервер: Онлайн\n"
            f"🔢 Версия: {version}\n"
        )
        
        # Добавляем информацию об обновлениях
        if update_info.get("is_update_available"):
            text += f"🔄 Обновления: Доступно обновление\n"
            text += f"📦 Последняя версия: {update_info.get('latest_version', 'Неизвестно')}\n"
        else:
            text += f"✅ Обновления: Актуальная версия\n"
            text += f"📦 Последняя версия: {update_info.get('latest_version', 'Неизвестно')}\n"
        
        text += f"🌐 URL: {status.get('url', '-')}\n"
        
        if update_available:
            text += "🔄 Доступно обновление (встроенная проверка)\n"
        if insecure:
            text += "⚠️ Небезопасное соединение\n"
        
        text += f"💬 {status.get('message', 'Сервер работает')}\n"
        
        # Добавляем ссылку на релиз, если есть обновление
        if update_info.get("is_update_available") and update_info.get("release_url"):
            text += f"\n🔗 [Скачать обновление]({update_info['release_url']})"
            
    else:
        peers = status.get("peers", []) if isinstance(status, dict) else []
        iface = status.get("interface", {}) if isinstance(status, dict) else {}
        
        text = (
            "📊 <b>Статус WG-Easy</b>\n\n"
            f"👥 Подключений: {len(peers)}\n"
            f"🌐 Адрес: <code>{iface.get('address', '-')}</code>\n"
            f"🔌 Порт: <code>{iface.get('listenPort', '-')}</code>\n"
        )
    
    await call.message.edit_text(text, reply_markup=admin_menu(), parse_mode="Markdown")
    await call.answer()


@router.callback_query(F.data == "admin:extend")
async def admin_extend(call: CallbackQuery) -> None:
    if not await check_admin_rights(call):
        return
    
    await call.message.edit_text(
        "🔁 <b>Продление срока действия</b>\n\n"
        "Функция в разработке...",
        reply_markup=admin_menu()
    )
    await call.answer()


@router.callback_query(F.data == "admin:delete")
async def admin_delete(call: CallbackQuery) -> None:
    if not await check_admin_rights(call):
        return
    
    await call.message.edit_text(
        "🗑 <b>Удаление клиента</b>\n\n"
        "Функция в разработке...",
        reply_markup=admin_menu()
    )
    await call.answer()


@router.callback_query(F.data == "admin:clients")
async def admin_clients(call: CallbackQuery) -> None:
    if not await check_admin_rights(call):
        return
    
    clients = get_all_clients()
    if not clients:
        await call.message.edit_text(
            "👥 <b>Список клиентов</b>\n\n"
            "Клиенты не найдены.",
            reply_markup=admin_menu()
        )
        await call.answer()
        return
    
    text = f"👥 <b>Список клиентов</b>\n\n"
    for i, client in enumerate(clients, 1):
        name = client.get('name', 'Без имени')
        username = client.get('username', '')
        expires_at = client.get('expires_at')
        
        if username:
            text += f"{i}. <b>{name}</b> (@{username})\n"
        else:
            text += f"{i}. <b>{name}</b>\n"
        
        if expires_at:
            from datetime import datetime
            dt = datetime.fromtimestamp(expires_at)
            text += f"   ⏳ До: {dt:%d.%m.%Y %H:%M}\n"
        else:
            text += f"   ♾️ Без ограничений\n"
        text += "\n"
    
    await call.message.edit_text(text, reply_markup=clients_list_keyboard(clients))
    await call.answer()


@router.callback_query(F.data.startswith("admin:client:"))
async def admin_client_detail(call: CallbackQuery) -> None:
    if not await check_admin_rights(call):
        return
    
    peer_id = call.data.split(":", 2)[2]
    client = get_client_by_peer_id(peer_id)
    
    if not client:
        await call.answer("❌ Клиент не найден", show_alert=True)
        return
    
    name = client.get('name', 'Без имени')
    username = client.get('username', '')
    expires_at = client.get('expires_at')
    
    text = f"👤 <b>Клиент: {name}</b>\n\n"
    if username:
        text += f"📱 Username: @{username}\n"
    text += f"🆔 Peer ID: <code>{peer_id}</code>\n"
    
    if expires_at:
        from datetime import datetime
        dt = datetime.fromtimestamp(expires_at)
        text += f"⏳ Действует до: {dt:%d.%m.%Y %H:%M}\n"
    else:
        text += f"♾️ Без ограничений\n"
    
    await call.message.edit_text(text, reply_markup=client_management_keyboard(peer_id))
    await call.answer()


@router.callback_query(F.data.startswith("admin:subscription:"))
async def admin_subscription(call: CallbackQuery) -> None:
    if not await check_admin_rights(call):
        return
    
    peer_id = call.data.split(":", 2)[2]
    client = get_client_by_peer_id(peer_id)
    
    if not client:
        await call.answer("❌ Клиент не найден", show_alert=True)
        return
    
    name = client.get('name', 'Без имени')
    expires_at = client.get('expires_at')
    
    text = f"📅 <b>Управление подпиской</b>\n\n"
    text += f"👤 Клиент: {name}\n"
    
    if expires_at:
        from datetime import datetime
        dt = datetime.fromtimestamp(expires_at)
        text += f"⏳ Текущий срок: {dt:%d.%m.%Y %H:%M}\n"
    else:
        text += f"♾️ Текущий статус: Без ограничений\n"
    
    await call.message.edit_text(text, reply_markup=subscription_keyboard(peer_id))
    await call.answer()


@router.callback_query(F.data.startswith("admin:extend:"))
async def admin_extend_client(call: CallbackQuery) -> None:
    if not await check_admin_rights(call):
        return
    
    parts = call.data.split(":")
    peer_id = parts[2]
    days = int(parts[3])
    
    client = get_client_by_peer_id(peer_id)
    if not client:
        await call.answer("❌ Клиент не найден", show_alert=True)
        return
    
    # Продлеваем подписку
    current_time = now_ts()
    if client.get('expires_at'):
        new_expires = client['expires_at'] + (days * 24 * 60 * 60)
    else:
        new_expires = current_time + (days * 24 * 60 * 60)
    
    upsert_client(client['tg_id'], peer_id, client['name'], new_expires, client.get('username'))
    
    from datetime import datetime
    dt = datetime.fromtimestamp(new_expires)
    
    await call.message.edit_text(
        f"✅ <b>Подписка продлена!</b>\n\n"
        f"👤 Клиент: {client['name']}\n"
        f"⏰ Продлено на: {days} дней\n"
        f"📅 Новый срок: {dt:%d.%m.%Y %H:%M}",
        reply_markup=subscription_keyboard(peer_id)
    )
    await call.answer()


@router.callback_query(F.data.startswith("admin:unlimited:"))
async def admin_unlimited(call: CallbackQuery) -> None:
    if not await check_admin_rights(call):
        return
    
    peer_id = call.data.split(":", 2)[2]
    client = get_client_by_peer_id(peer_id)
    
    if not client:
        await call.answer("❌ Клиент не найден", show_alert=True)
        return
    
    # Устанавливаем без ограничений
    upsert_client(client['tg_id'], peer_id, client['name'], None, client.get('username'))
    
    await call.message.edit_text(
        f"✅ <b>Подписка без ограничений!</b>\n\n"
        f"👤 Клиент: {client['name']}\n"
        f"♾️ Статус: Без ограничений",
        reply_markup=subscription_keyboard(peer_id)
    )
    await call.answer()


@router.callback_query(F.data.startswith("admin:stop:"))
async def admin_stop_client(call: CallbackQuery) -> None:
    if not await check_admin_rights(call):
        return
    
    peer_id = call.data.split(":", 2)[2]
    client = get_client_by_peer_id(peer_id)
    
    if not client:
        await call.answer("❌ Клиент не найден", show_alert=True)
        return
    
    # Останавливаем подписку (устанавливаем прошедшую дату)
    upsert_client(client['tg_id'], peer_id, client['name'], 0, client.get('username'))
    
    await call.message.edit_text(
        f"⏹️ <b>Подписка остановлена!</b>\n\n"
        f"👤 Клиент: {client['name']}\n"
        f"❌ Статус: Остановлена",
        reply_markup=subscription_keyboard(peer_id)
    )
    await call.answer()


@router.callback_query(F.data.startswith("admin:delete_client:"))
async def admin_delete_client(call: CallbackQuery) -> None:
    if not await check_admin_rights(call):
        return
    
    peer_id = call.data.split(":", 2)[2]
    client = get_client_by_peer_id(peer_id)
    
    if not client:
        await call.answer("❌ Клиент не найден", show_alert=True)
        return
    
    # Удаляем клиента
    delete_client(peer_id)
    
    await call.message.edit_text(
        f"🗑️ <b>Клиент удален!</b>\n\n"
        f"👤 Клиент: {client['name']}\n"
        f"❌ Статус: Удален",
        reply_markup=admin_menu()
    )
    await call.answer()


@router.callback_query(F.data == "admin:back")
async def admin_back(call: CallbackQuery) -> None:
    if not await check_admin_rights(call):
        return
    
    await call.message.edit_text(
        "🔧 <b>Админ панель</b>\n\n"
        "Выберите действие:",
        reply_markup=admin_menu()
    )
    await call.answer()


@router.callback_query(F.data == "admin:backup")
async def admin_backup(call: CallbackQuery) -> None:
    if not await check_admin_rights(call):
        return
    
    try:
        # Создаем временную директорию
        data_dir = os.path.join(os.getcwd(), "data")
        os.makedirs(data_dir, exist_ok=True)
        
        # Путь к базе данных WG-Easy (монтируется как read-only)
        wg_easy_db_path = "/etc/wireguard/wg-easy.db"
        backup_file = os.path.join(data_dir, "wg-easy-backup.db")
        
        # Копируем базу данных
        with open(wg_easy_db_path, "rb") as src:
            with open(backup_file, "wb") as dst:
                dst.write(src.read())
        
        # Отправляем файл пользователю
        await call.message.answer_document(
            FSInputFile(backup_file, filename="wg-easy-backup.db"),
            caption="💾 <b>Бэкап WG-Easy</b>\n\n"
                   "База данных содержит все настройки сервера и клиентов.\n"
                   "Для восстановления замените файл wg-easy.db в контейнере."
        )
        
        # Удаляем временный файл
        os.remove(backup_file)
        
        await call.answer("✅ Бэкап успешно создан!")
        
    except FileNotFoundError:
        logger.error("База данных WG-Easy не найдена")
        await call.message.edit_text(
            "❌ <b>Ошибка создания бэкапа</b>\n\n"
            "База данных WG-Easy не найдена. Убедитесь, что том правильно смонтирован.",
            reply_markup=admin_menu()
        )
        await call.answer()
    except Exception as e:
        logger.error(f"Неожиданная ошибка при создании бэкапа: {e}")
        await call.message.edit_text(
            f"❌ <b>Ошибка создания бэкапа</b>\n\n"
            f"<code>{str(e)}</code>",
            reply_markup=admin_menu()
        )
        await call.answer()


@router.callback_query(F.data.startswith("admin:notify:"))
async def admin_notify_client(call: CallbackQuery) -> None:
    if not await check_admin_rights(call):
        return
    
    peer_id = call.data.split(":", 2)[2]
    client = get_client_by_peer_id(peer_id)
    
    if not client:
        await call.answer("❌ Клиент не найден", show_alert=True)
        return
    
    username = client.get('username', '')
    name = client.get('name', 'Без имени')
    
    if not username:
        await call.answer("❌ У клиента не указан username", show_alert=True)
        return
    
    try:
        # Отправляем уведомление пользователю
        notification_text = (
            f"🎉 <b>Добро пожаловать в VPN!</b>\n\n"
            f"👤 Ваше имя: <b>{name}</b>\n"
            f"🆔 Ваш ID: <code>{peer_id}</code>\n\n"
            f"📱 <b>Как пользоваться ботом:</b>\n"
            f"• Нажмите /start для начала работы\n"
            f"• Используйте кнопку '📥 Скачать конфиг' для получения файла конфигурации\n"
            f"• Используйте кнопку '🔳 QR-код' для быстрого подключения\n"
            f"• Кнопка '📘 Инструкция' покажет подробное руководство\n"
            f"• Кнопка '⏳ Остаток времени' покажет срок действия подписки\n\n"
            f"🔧 <b>Подключение:</b>\n"
            f"1. Скачайте файл конфигурации\n"
            f"2. Установите приложение WireGuard на устройство\n"
            f"3. Импортируйте файл в приложение\n"
            f"4. Подключайтесь к VPN!\n\n"
            f"❓ Если возникнут вопросы, обращайтесь к администратору."
        )
        
        # Пытаемся отправить сообщение пользователю
        try:
            await call.bot.send_message(
                chat_id=f"@{username}",
                text=notification_text
            )
            await call.answer("✅ Уведомление отправлено!")
            
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления пользователю @{username}: {e}")
            await call.answer("❌ Не удалось отправить уведомление. Возможно, пользователь не запускал бота.", show_alert=True)
            
    except Exception as e:
        logger.error(f"Ошибка уведомления клиента: {e}")
        await call.answer("❌ Ошибка отправки уведомления", show_alert=True)


@router.callback_query(F.data == "admin:broadcast")
async def admin_broadcast(call: CallbackQuery) -> None:
    if not await check_admin_rights(call):
        return
    
    await call.message.edit_text(
        "📣 <b>Рассылка сообщений</b>\n\n"
        "Функция в разработке...",
        reply_markup=admin_menu()
    )
    await call.answer()
