import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from ..config import settings
from ..keyboards.main_menu import admin_menu, clients_list_keyboard, client_management_keyboard, subscription_keyboard
from ..services.wg_easy_client import WGEasyClient
from ..db import upsert_client, get_client_by_tg, get_all_clients, get_client_by_peer_id, delete_client, now_ts


router = Router()
logger = logging.getLogger(__name__)


class AdminStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_username = State()
    waiting_for_peer_id = State()


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
            f"✅ Сервер: <b>Онлайн</b>\n"
            f"🔢 Версия: <code>{version}</code>\n"
            f"🌐 URL: <code>{status.get('url', '-')}</code>\n"
        )
        
        if update_available:
            text += "🔄 Доступно обновление\n"
        if insecure:
            text += "⚠️ Небезопасное соединение\n"
        
        text += f"💬 {status.get('message', 'Сервер работает')}\n"
    else:
        peers = status.get("peers", []) if isinstance(status, dict) else []
        iface = status.get("interface", {}) if isinstance(status, dict) else {}
        
        text = (
            "📊 <b>Статус WG-Easy</b>\n\n"
            f"👥 Подключений: {len(peers)}\n"
            f"🌐 Адрес: <code>{iface.get('address', '-')}</code>\n"
            f"🔌 Порт: <code>{iface.get('listenPort', '-')}</code>\n"
        )
    
    await call.message.edit_text(text, reply_markup=admin_menu())
    await call.answer()


@router.callback_query(F.data == "admin:add")
async def admin_add_start(call: CallbackQuery, state: FSMContext) -> None:
    if not await check_admin_rights(call):
        return
    
    await call.message.edit_text(
        "➕ <b>Добавление нового клиента</b>\n\n"
        "Введите имя для нового клиента:",
        reply_markup=None
    )
    await state.set_state(AdminStates.waiting_for_name)
    await call.answer()


@router.message(AdminStates.waiting_for_name)
async def admin_add_name(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        await message.answer("❌ Нет прав доступа")
        await state.clear()
        return
    
    name = message.text.strip()
    if not name:
        await message.answer("❌ Имя не может быть пустым. Попробуйте еще раз:")
        return
    
    try:
        async with WGEasyClient() as api:
            await api.login()
            peer_data = await api.add_peer(name)
        
        peer_id = peer_data.get("id") or peer_data.get("peer_id")
        if not peer_id:
            await message.answer("❌ Не удалось получить ID нового клиента")
            await state.clear()
            return
        
        await state.update_data(peer_id=peer_id, name=name)
        await message.answer(
            f"✅ Клиент <b>{name}</b> создан!\n\n"
            f"ID: <code>{peer_id}</code>\n\n"
            "Теперь введите username пользователя (например: username или @username):"
        )
        await state.set_state(AdminStates.waiting_for_username)
        
    except Exception as e:
        logger.error(f"Ошибка создания клиента: {e}")
        await message.answer(f"❌ Ошибка создания клиента:\n<code>{str(e)}</code>")
        await state.clear()


@router.message(AdminStates.waiting_for_username)
async def admin_add_username(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        await message.answer("❌ Нет прав доступа")
        await state.clear()
        return
    
    username = message.text.strip()
    if username.startswith('@'):
        username = username[1:]  # Убираем @ если есть
    
    if not username:
        await message.answer("❌ Username не может быть пустым. Попробуйте еще раз:")
        return
    
    data = await state.get_data()
    peer_id = data.get("peer_id")
    name = data.get("name")
    
    if not peer_id or not name:
        await message.answer("❌ Ошибка данных. Начните заново.")
        await state.clear()
        return
    
    try:
        # Связываем клиента с username (tg_id будет получен позже при первом использовании)
        upsert_client(0, peer_id, name, None, username)
        
        await message.answer(
            f"✅ <b>Клиент успешно добавлен!</b>\n\n"
            f"👤 Имя: <b>{name}</b>\n"
            f"🆔 Peer ID: <code>{peer_id}</code>\n"
            f"📱 Username: <code>@{username}</code>\n\n"
            "Пользователь теперь может использовать бота для получения конфигурации.",
            reply_markup=admin_menu()
        )
        await state.clear()
        
    except Exception as e:
        logger.error(f"Ошибка связывания клиента: {e}")
        await message.answer(f"❌ Ошибка связывания клиента:\n<code>{str(e)}</code>")
        await state.clear()


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


@router.callback_query(F.data == "admin:backup")
async def admin_backup(call: CallbackQuery) -> None:
    if not await check_admin_rights(call):
        return
    
    clients = get_all_clients()
    if not clients:
        await call.message.edit_text(
            "💾 <b>Бэкап клиентов</b>\n\n"
            "Клиенты не найдены.",
            reply_markup=admin_menu()
        )
        await call.answer()
        return
    
    # Создаем бэкап
    import json
    from datetime import datetime
    
    backup_data = {
        "timestamp": datetime.now().isoformat(),
        "clients": clients
    }
    
    backup_text = f"💾 <b>Бэкап клиентов</b>\n\n"
    backup_text += f"📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
    backup_text += f"👥 Клиентов: {len(clients)}\n\n"
    backup_text += f"📄 <b>Данные бэкапа:</b>\n"
    backup_text += f"<code>{json.dumps(backup_data, ensure_ascii=False, indent=2)}</code>"
    
    await call.message.edit_text(backup_text, reply_markup=admin_menu())
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
