import os
import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from apscheduler.schedulers.asyncio import AsyncIOScheduler

import bot.setup_logging
from bot.validation import validate_all
from configs.send_config import Config
from configs.chats_settings import TIMEZONE

from bot.middlewares import BotMiddleware
from bot.scheduler import start_scheduler
from bot.handlers import router

from dotenv import load_dotenv
load_dotenv()


logger = logging.getLogger(__name__)
bot = Bot(
    token=os.getenv('BOT_TOKEN'),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()
router.message.middleware(BotMiddleware(bot))
dp.include_router(router)

config = Config()
config.bot = bot
scheduler = AsyncIOScheduler(timezone=TIMEZONE)


async def main():
    try:
        await validate_all()
        await bot.delete_webhook(drop_pending_updates=True)
        await start_scheduler(scheduler, config)
        await dp.start_polling(bot)
    except Exception as ex:
        logger.error(f'Ошибка при запуске бота: {ex}')
    finally:
        if scheduler.running:
            scheduler.shutdown(wait=False)
            logger.info('Шедулер завершил работу')
        await bot.session.close()
        logger.info('Бот завершил работу')


if __name__ == '__main__':
    asyncio.run(main())