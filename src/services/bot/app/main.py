import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from .config import settings
from .handlers import routers

dp = Dispatcher()

async def main():
    # просто чтобы видеть, что мы грузим правильные env
    print("BOT_TOKEN len:", len(settings.BOT_TOKEN))
    print("AUTH_SERVICE_URL:", settings.AUTH_SERVICE_URL)

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    
    for router in routers:
        dp.include_router(router)

    # здесь запускаем лонг-поллинг
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
