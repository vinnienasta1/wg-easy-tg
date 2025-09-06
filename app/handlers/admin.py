import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from ..config import settings
from ..keyboards.main_menu import admin_menu
from ..services.wg_easy_client import WGEasyClient
from ..db import upsert_client, get_client_by_tg


router = Router()
logger = logging.getLogger(__name__)


class AdminStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_tg_id = State()
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
            "Теперь введите Telegram ID пользователя:"
        )
        await state.set_state(AdminStates.waiting_for_tg_id)
        
    except Exception as e:
        logger.error(f"Ошибка создания клиента: {e}")
        await message.answer(f"❌ Ошибка создания клиента:\n<code>{str(e)}</code>")
        await state.clear()


@router.message(AdminStates.waiting_for_tg_id)
async def admin_add_tg_id(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        await message.answer("❌ Нет прав доступа")
        await state.clear()
        return
    
    try:
        tg_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Неверный формат Telegram ID. Введите число:")
        return
    
    data = await state.get_data()
    peer_id = data.get("peer_id")
    name = data.get("name")
    
    if not peer_id or not name:
        await message.answer("❌ Ошибка данных. Начните заново.")
        await state.clear()
        return
    
    try:
        # Связываем клиента с Telegram ID
        upsert_client(tg_id, peer_id, name, None)
        
        await message.answer(
            f"✅ <b>Клиент успешно добавлен!</b>\n\n"
            f"👤 Имя: <b>{name}</b>\n"
            f"🆔 Peer ID: <code>{peer_id}</code>\n"
            f"📱 Telegram ID: <code>{tg_id}</code>\n\n"
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
