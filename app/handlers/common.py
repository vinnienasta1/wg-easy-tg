from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from ..config import settings
from ..keyboards.main_menu import client_menu, admin_menu


router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in settings.admins


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    if is_admin(message.from_user.id):
        await message.answer("Добро пожаловать, админ! Выберите действие:", reply_markup=admin_menu())
    else:
        await message.answer("Добро пожаловать! Выберите действие:", reply_markup=client_menu())


@router.callback_query(F.data == "client:guide")
async def client_guide(call: CallbackQuery) -> None:
    await call.message.edit_text(
        "📘 <b>Инструкция по подключению</b>\n\n"
        "1️⃣ Установите приложение WireGuard на ваше устройство\n"
        "2️⃣ Получите конфигурацию или QR-код через бота\n"
        "3️⃣ Импортируйте конфиг в приложение WireGuard\n"
        "4️⃣ Включите VPN-подключение\n\n"
        "💡 <i>Если у вас возникли проблемы, обратитесь к администратору</i>",
        reply_markup=client_menu(),
    )
    await call.answer()
