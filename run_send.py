import os
import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import bot.setup_logging
from configs.send_config import Config
from configs.config_classes import SendBaseConfig

from dotenv import load_dotenv
load_dotenv()


logger = logging.getLogger(__name__)
config = Config()
bot = Bot(
    token=os.getenv('BOT_TOKEN'),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()


async def send_from_configs(
        send_configs: list[SendBaseConfig],
        bot: Bot,
        disable_notification: bool,
        ) -> None:
    '''Получение и отправка рассылок из конфигов'''
    for send_config in send_configs:
        try:
            parse_result = await send_config.parse_func(send_config)
        except Exception as ex:
            logger.error(f'Ошибка при получении рассылки: {ex}')
            continue
        if isinstance(parse_result, str):
            for chat in send_config.chats:
                try:
                    await bot.send_message(
                        chat_id=chat.chat_id,
                        text=parse_result,
                        disable_notification=disable_notification,
                    )
                except Exception as ex:
                    logger.error(f'Ошибка при отправке рассылки в чат {chat}: {ex}')



async def main():
    try:
        logger.info('Старт получения и отправки рассылки')
        await send_from_configs(config.get_email_configs(), bot, disable_notification=True)
        await asyncio.sleep(5)
        await send_from_configs(config.get_reminder_configs(), bot, disable_notification=False)
    except Exception as ex:
        logger.error(f'Ошибка при получении и отпраки рассылки: {ex}')
    finally:
        await bot.session.close()
        logger.info('Бот завершил работу')


if __name__ == '__main__':
    asyncio.run(main())