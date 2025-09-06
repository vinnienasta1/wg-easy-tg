from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


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
        [InlineKeyboardButton(text="➕ Добавить", callback_data="admin:add")],
        [InlineKeyboardButton(text="🔁 Продлить", callback_data="admin:extend")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data="admin:delete")],
        [InlineKeyboardButton(text="📣 Рассылка", callback_data="admin:broadcast")],
    ])
