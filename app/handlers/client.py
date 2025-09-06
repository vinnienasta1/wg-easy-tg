import logging
import os
from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, BufferedInputFile

from ..keyboards.main_menu import client_menu
from ..services.wg_easy_client import WGEasyClient
from ..services.qr import config_to_qr_png_bytes
from ..db import get_client_by_tg


router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "client:config")
async def client_get_config(call: CallbackQuery) -> None:
    record = get_client_by_tg(call.from_user.id)
    if not record:
        await call.answer("❌ Профиль не найден. Обратитесь к администратору.", show_alert=True)
        return
    
    peer_id = record["peer_id"]
    try:
        async with WGEasyClient() as api:
            await api.login()
            config_text = await api.get_peer_config(peer_id)
    except Exception as e:
        logger.error(f"Ошибка получения конфига для {peer_id}: {e}")
        await call.answer("❌ Ошибка получения конфигурации", show_alert=True)
        return

    # Отправим как файл
    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, f"{peer_id}.conf")
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(config_text)
        await call.message.answer_document(
            FSInputFile(file_path, filename=f"{peer_id}.conf"),
            caption=f"📁 Конфигурация для {record.get('name', peer_id)}"
        )
        # Удаляем временный файл
        os.remove(file_path)
    except Exception as e:
        logger.error(f"Ошибка создания файла конфига: {e}")
        await call.answer("❌ Ошибка создания файла", show_alert=True)
    finally:
        await call.answer()


@router.callback_query(F.data == "client:qr")
async def client_get_qr(call: CallbackQuery) -> None:
    record = get_client_by_tg(call.from_user.id)
    if not record:
        await call.answer("❌ Профиль не найден. Обратитесь к администратору.", show_alert=True)
        return
    
    peer_id = record["peer_id"]
    try:
        async with WGEasyClient() as api:
            await api.login()
            config_text = await api.get_peer_config(peer_id)
        png_bytes = config_to_qr_png_bytes(config_text)
        await call.message.answer_photo(
            BufferedInputFile(png_bytes, filename=f"{peer_id}.png"), 
            caption=f"🔳 QR-код для {record.get('name', peer_id)}"
        )
    except Exception as e:
        logger.error(f"Ошибка создания QR-кода для {peer_id}: {e}")
        await call.answer("❌ Ошибка создания QR-кода", show_alert=True)
    finally:
        await call.answer()


@router.callback_query(F.data == "client:expiry")
async def client_get_expiry(call: CallbackQuery) -> None:
    record = get_client_by_tg(call.from_user.id)
    if not record:
        await call.answer("❌ Профиль не найден. Обратитесь к администратору.", show_alert=True)
        return
    
    if not record.get("expires_at"):
        await call.message.edit_text(
            "⏳ <b>Срок действия</b>\n\n"
            "Срок действия не установлен (бессрочно).",
            reply_markup=client_menu()
        )
        await call.answer()
        return
    
    from datetime import datetime
    dt = datetime.fromtimestamp(record["expires_at"])
    await call.message.edit_text(
        f"⏳ <b>Срок действия</b>\n\n"
        f"Действует до: <b>{dt:%d.%m.%Y %H:%M}</b>",
        reply_markup=client_menu(),
    )
    await call.answer()
