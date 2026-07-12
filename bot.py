import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app import context
from app.config import load_config
from app.db import connect, init_schema
from app.handlers import setup_routers


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    config = load_config()
    await init_schema(config.database_path)
    db = await connect(config.database_path)

    context.config = config
    context.db = db

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_router(setup_routers())

    try:
        await dispatcher.start_polling(bot)
    finally:
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
