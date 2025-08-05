import logging
import asyncio
import random
from functools import wraps
from pathlib import Path

from aiogram.types import FSInputFile
from aiogram.enums import ParseMode
from aiogram import Bot

from configs.config_classes import SendBaseConfig
from configs.chats_settings import SendSettingsConfig


logger = logging.getLogger(__name__)


class RetryExcept(Exception):
    '''Исключение когда попытки закончились'''


def retry_send(max_attempts: int, delay_seconds: int):
    '''Декоратор для повторного запуска корутины coroutine_func, если она завершает работу с ошибкой'''
    def decorator(coroutine_func):
        @wraps(coroutine_func)
        async def wrapper(config: SendBaseConfig):
            for attempt in range(1, max_attempts + 1):
                try:
                    parse_result = await coroutine_func(config)
                    return parse_result
                except Exception as ex:
                    log = (
                        f'Ошибка выполнения функции {coroutine_func}\n'
                        f'Код ошибки: {ex}\n'
                        f'Попытка {attempt}/{max_attempts} через {delay_seconds/60} минут'
                    )
                    logger.error(log, exc_info=True)
                    if attempt != max_attempts:
                        await asyncio.sleep(delay_seconds)
            log = f'Исчерпаны {max_attempts} попыток выполнения функции {coroutine_func}'
            logger.error(log, exc_info=True)
            raise RetryExcept(log)
        return wrapper
    return decorator


@retry_send(max_attempts=SendSettingsConfig.max_attempts, delay_seconds=SendSettingsConfig.delay_seconds)
async def get_message(send_config: SendBaseConfig):
    '''Получение рассылки из функции config.parse_func с повторными попытками в случае ошибки'''
    parse_result = await send_config.parse_func(send_config)
    return parse_result


async def sleep_between_send_messages() -> None:
    '''Пауза между отправками сообщений'''
    sleep_seconds = random.random()
    await asyncio.sleep(sleep_seconds)


async def get_and_send_message(send_config: SendBaseConfig, bot: Bot) -> None:
    '''Получение и отправка рассылки в чаты send_config.chats'''
    try:
        parse_result = await get_message(send_config)
        if parse_result is None:
            return
    except RetryExcept as ex:
        admin_id = send_config.admin_chat.chat_id
        if SendSettingsConfig.send_errors_to_admin and admin_id is not None:
            await bot.send_message(admin_id, str(ex), parse_mode=None)
        return
    
    # message and PDF from Proglib
    if isinstance(parse_result, tuple) and len(parse_result) == 2:
        message_to_send, pdf_file_name = parse_result
        if pdf_file_name is not None and Path(pdf_file_name).is_file():
            pdf_file = FSInputFile(pdf_file_name)
            for chat in send_config.chats:
                await bot.send_document(
                    chat_id=chat.chat_id,
                    document=pdf_file,
                    caption=message_to_send,
                    parse_mode=ParseMode.HTML,
                )
                await sleep_between_send_messages()
            Path(pdf_file_name).unlink(missing_ok=True)
            return
        else:
            parse_result = parse_result[0]

    if isinstance(parse_result, str):
        message_to_send = parse_result
        for chat in send_config.chats:
            await bot.send_message(chat.chat_id, message_to_send, disable_notification=False)
            await sleep_between_send_messages()
