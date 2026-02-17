import asyncio
import sys
from os import getenv
from pathlib import Path

# Ensure project root is on sys.path so `bot.*` imports work when run as a script
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Configure logging early
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

# Импортируем наши наработки
from bot.database.base import async_session, proceed_schemas
from bot.handlers.common import router as common_router
from bot.handlers.source_handlers import router as source_router
from bot.middlewares.session import DbSessionMiddleware
from bot.middlewares.throttle import ThrottleMiddleware
from core.logger import logger  # noqa: E402

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

# Ensure TOKEN is a valid string
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

# At this point, TOKEN is guaranteed to be a string
bot = Bot(token=TOKEN)

logger.info("BOT_TOKEN: {}", TOKEN)


async def main():
    """Application entrypoint: prepare DB, register middleware and start polling.

    This coroutine is executed when `bot/start.py` is run as a script and
    performs one-time initialization (schemas) before starting the aiogram
    dispatcher polling loop.
    """
    # Создаем таблицы, если их нет
    await proceed_schemas()

    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем Middleware (before routers so they wrap all handlers)
    dp.update.middleware(DbSessionMiddleware(session_pool=async_session))
    dp.update.middleware(ThrottleMiddleware(rate=1.0))

    dp.include_router(common_router)
    dp.include_router(source_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logger.info("Starting bot")
    asyncio.run(main())
