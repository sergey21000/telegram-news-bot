import logging
import asyncio
import random
from functools import wraps
from pathlib import Path

from aiogram.types import FSInputFile
from aiogram.enums import ParseMode
from aiogram import Bot

from configs.base import SendBaseConfig
from configs.chats_settings import SendSettingsConfig
from bot.validation import EmailNotArrivedYet, RetryExcept


logger = logging.getLogger(__name__)


def retry_send(max_attempts: int, delay_seconds: int):
    '''Декоратор для повторного запуска корутины coroutine_func, если она завершает работу с ошибкой'''
    def decorator(coroutine_func):
        @wraps(coroutine_func)
        async def wrapper(config: SendBaseConfig):
            for attempt in range(1, max_attempts + 1):
                try:
                    result = await coroutine_func(config)
                    return result
                except EmailNotArrivedYet as ex:
                    log = (
                        f'Ошибка отсутствия письма с сегодняшней датой\n'
                        f'Код ошибки: {ex}\n'
                        f'Попытка {attempt}/{max_attempts} через {delay_seconds/60} минут'
                    )
                    logger.error(log, exc_info=True)
                    if attempt != max_attempts:
                        await asyncio.sleep(delay_seconds)
                except Exception as ex:
                    log = (
                        f'Ошибка выполнения функции {coroutine_func}\n'
                        f'Код ошибки: {ex}\n'
                    )
                    logger.error(log, exc_info=True)
                    raise
            log = f'Исчерпаны {max_attempts} попыток выполнения функции {coroutine_func}'
            logger.error(log, exc_info=True)
            raise RetryExcept(log)
        return wrapper
    return decorator


@retry_send(max_attempts=SendSettingsConfig.max_attempts, delay_seconds=SendSettingsConfig.delay_seconds)
async def get_message_with_attempts(send_config: SendBaseConfig):
    '''Получение рассылки из функции config.parse_func с повторными попытками в случае ошибки'''
    parse_result = await send_config.parse_func(send_config)
    return parse_result


async def get_message_without_attempts(send_config: SendBaseConfig):
    '''Получение рассылки из функции config.parse_func с повторными попытками в случае ошибки'''
    parse_result = await send_config.parse_func(send_config)
    return parse_result


async def sleep_between_send_messages() -> None:
    '''Пауза между отправками сообщений'''
    sleep_seconds = random.random()
    await asyncio.sleep(sleep_seconds)


async def get_and_send_message(
        send_config: SendBaseConfig,
        bot: Bot,
        with_attempts: bool = False,
        raise_if_email_not_arrived: bool = False,
    ) -> None:
    '''Получение и отправка рассылки в чаты send_config.chats'''
    parse_result: str | tuple[str, str | None] | None = None
    get_message_func = get_message_with_attempts if with_attempts else get_message_without_attempts
    try:
        parse_result = await get_message_func(send_config)
    except RetryExcept as ex:
        admin_id = send_config.admin_chat.chat_id
        if SendSettingsConfig.send_errors_to_admin and admin_id is not None:
            await bot.send_message(admin_id, str(ex), parse_mode=None)
        return
    except EmailNotArrivedYet as ex:
        log = f'Ошибка отсутствия письма с сегодняшней датой: {ex}'
        logger.error(log)
        if raise_if_email_not_arrived:
            raise ex
    except Exception as ex:
        logger.error(f'Ошибка при получении рассылки: {ex}')
        return
    if parse_result is None:
        return
    # message and PDF from Proglib
    if isinstance(parse_result, tuple) and len(parse_result) == 2:
        message_to_send, pdf_file_name = parse_result
        if pdf_file_name is not None and Path(pdf_file_name).is_file():
            pdf_file = FSInputFile(pdf_file_name)
            for chat in send_config.chats:
                try:
                    await bot.send_document(
                        chat_id=chat.chat_id,
                        document=pdf_file,
                        caption=message_to_send,
                        parse_mode=ParseMode.HTML,
                        disable_notification=send_config.disable_notification,
                    )
                    await sleep_between_send_messages()
                except Exception as ex:
                    logger.error(f'Ошибка при отправке рассылки в чат {chat}: {ex}')
            Path(pdf_file_name).unlink(missing_ok=True)
            return
        else:
            parse_result = parse_result[0]
    if isinstance(parse_result, str):
        message_to_send = parse_result
        for chat in send_config.chats:
            print(f'DEBUG | message_to_send: {message_to_send}')
            try:
                await bot.send_message(
                    chat_id=chat.chat_id,
                    text=message_to_send,
                    disable_notification=send_config.disable_notification,
                )
                await sleep_between_send_messages()
            except Exception as ex:
                logger.error(f'Ошибка при отправке рассылки в чат {chat}: {ex}')
    else:
        log = f'Результат парсинга не является строкой, тип: {type(parse_result)}'
        logger.error(log)
