import os
import sys
import logging
import asyncio
import datetime

import click
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import bot.setup_logging
from configs.send_config import Config
from configs.base import SendBaseConfig
from bot.message_sender import get_and_send_message
from bot.validation import EmailNotArrivedYet

from dotenv import load_dotenv
load_dotenv()


logger = logging.getLogger(__name__)
config = Config()
bot = Bot(
    token=os.getenv('BOT_TOKEN'),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()


def is_current_day_in_schedule(day_of_week: str) -> bool:
    """Проверяет, соответствует ли текущий день расписанию в cron-формате"""
    if day_of_week.strip() == '*':
        return True
    current_weekday = datetime.datetime.now().weekday()
    weekday_map = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat', 6: 'sun'}
    current_day_cron = weekday_map[current_weekday]
    scheduled_days = [day.strip().lower() for day in day_of_week.split(',')]
    return current_day_cron in scheduled_days


async def send_from_configs(
    send_configs: list[SendBaseConfig],
    bot: Bot,
    skip_not_current_day: bool,
    sys_exit_if_email_not_arrived: bool = False,
) -> None:
    '''Получение и отправка рассылок из конфигов'''
    for send_config in send_configs:
        if not send_config.is_active:
            continue
        if skip_not_current_day:
            if not is_current_day_in_schedule(send_config.schedule_kwargs_config.day_of_week):
                continue
        try:
            await get_and_send_message(
                send_config=send_config,
                bot=bot,
                with_attempts=False,
                raise_if_email_not_arrived=sys_exit_if_email_not_arrived,
            )
        except EmailNotArrivedYet as ex:
            logger.error(f'Ошибка отсутствия письма с сегодняшней датой, принудительный выход с кодом 111')
            sys.exit(111)
        except Exception as ex:
            logger.error(f'Ошибка при получении или отправке рассылки: {ex}')
            continue


async def async_main(email: bool, reminder: bool):
    """Запуск рассылок ботом"""
    try:
        logger.info('Старт получения и отправки рассылки')
        if email:
            await send_from_configs(
                send_configs=config.get_email_configs(),
                bot=bot,
                skip_not_current_day=False,
                sys_exit_if_email_not_arrived=True,
            )
            await asyncio.sleep(5)
        if reminder:
            await send_from_configs(
                send_configs=config.get_reminder_configs(),
                bot=bot,
                skip_not_current_day=True,
            )
    except Exception as ex:
        logger.error(f'Ошибка при получении и отправки рассылки: {ex}')
    finally:
        await bot.session.close()
        logger.info('Бот завершил работу')


@click.command()
@click.option('--all', 'send_all', is_flag=True, default=True, help='Отправить все рассылки (по умолчанию)')
@click.option('--email', is_flag=True, help='Отправить только email-рассылки')
@click.option('--reminder', is_flag=True, help='Отправить только напоминания')
def cli(send_all: bool, email: bool, reminder: bool):
    """Запуск рассылок ботом"""
    if email or reminder:
        send_all = False
    if send_all:
        email, reminder = True, True
    asyncio.run(async_main(email, reminder))


if __name__ == '__main__':
    cli()
