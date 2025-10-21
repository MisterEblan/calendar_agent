from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.api.handlers import dp
from src.config import app_config
from src.db.engine import init_db

import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)-20s | %(levelname)-7s| %(name)-20s :: %(message)s"
)

logger = logging.getLogger(__name__)

async def main() -> None:
    await init_db()
    bot = Bot(
        token=app_config.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )

    await dp.start_polling(bot)

if __name__ == "__main__":
    logger.info("Starting polling")
    asyncio.run(main())
