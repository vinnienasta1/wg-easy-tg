import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from .config import settings
from .logger import setup_logging
from .handlers.common import router as common_router
from .handlers.client import router as client_router
from .handlers.admin import router as admin_router
from .db import init_db
from .migrate_db import migrate_database


async def main() -> None:
    setup_logging()
    logging.getLogger(__name__).info("Starting bot...")
    init_db()
    migrate_database()

    bot = Bot(
        token=settings.tg_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    
    # Используем MemoryStorage для FSM
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(common_router)
    dp.include_router(client_router)
    dp.include_router(admin_router)

    # В новой версии aiogram используется другой метод
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
