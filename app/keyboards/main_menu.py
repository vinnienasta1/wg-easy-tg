from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any


def client_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Скачать конфиг", callback_data="client:config")],
        [InlineKeyboardButton(text="🔳 QR-код", callback_data="client:qr")],
        [InlineKeyboardButton(text="📘 Инструкция", callback_data="client:guide")],
        [InlineKeyboardButton(text="⏳ Остаток времени", callback_data="client:expiry")],
    ])


def admin_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Мониторинг", callback_data="admin:monitor")],
        [InlineKeyboardButton(text="👥 Клиенты", callback_data="admin:clients")],
        [InlineKeyboardButton(text="💾 Бэкап", callback_data="admin:backup")],
        [InlineKeyboardButton(text="📣 Рассылка", callback_data="admin:broadcast")],
    ])


def clients_list_keyboard(clients: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Клавиатура со списком клиентов"""
    buttons = []
    for client in clients:
        name = client.get('name', 'Без имени')
        username = client.get('username', '')
        display_name = f"{name} (@{username})" if username else name
        buttons.append([InlineKeyboardButton(
            text=display_name,
            callback_data=f"admin:client:{client['peer_id']}"
        )])
    
    # Добавляем кнопку "Назад"
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin:back")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def client_management_keyboard(peer_id: str) -> InlineKeyboardMarkup:
    """Клавиатура управления конкретным клиентом"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Подписка", callback_data=f"admin:subscription:{peer_id}")],
        [InlineKeyboardButton(text="📢 Уведомить", callback_data=f"admin:notify:{peer_id}")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"admin:delete_client:{peer_id}")],
        [InlineKeyboardButton(text="🔙 Назад к списку", callback_data="admin:clients")],
    ])


def subscription_keyboard(peer_id: str) -> InlineKeyboardMarkup:
    """Клавиатура управления подпиской"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏰ Продлить на месяц", callback_data=f"admin:extend:{peer_id}:30")],
        [InlineKeyboardButton(text="⏰ Продлить на 3 месяца", callback_data=f"admin:extend:{peer_id}:90")],
        [InlineKeyboardButton(text="♾️ Без ограничений", callback_data=f"admin:unlimited:{peer_id}")],
        [InlineKeyboardButton(text="⏹️ Остановить", callback_data=f"admin:stop:{peer_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"admin:client:{peer_id}")],
    ])
