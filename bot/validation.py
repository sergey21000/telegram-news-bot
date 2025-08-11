import os
import logging
import importlib
from pathlib import Path
from collections.abc import Callable, Coroutine, Awaitable
from types import SimpleNamespace

from dotenv import load_dotenv
load_dotenv()

if __name__ == '__main__':
    import asyncio
    import bot.setup_logging

from configs.chats_settings import CHATS_TO_SEND, SendSettingsConfig

if SendSettingsConfig.send_pdf_to_proglib:
    from bot.parser import UrlToPdf


logger = logging.getLogger(__name__)


class EmailNotArrivedYet(Exception):
    """Исключение для случая, когда письмо еще не пришло сегодня"""


class RetryExcept(Exception):
    '''Исключение когда попытки выполнения корутины закончились'''


class ValidationError(Exception):
    '''Общее исключение при валидации'''
    PREFIX = 'Ошибка валидации: '

    def __init__(self, message_error: str = ''):
        self.message_error = message_error

    def __str__(self):
        return f'{self.PREFIX}{self.message_error}'


class ConfigValidationError(ValidationError):
    '''Исключение при работе с конфигами'''
    PREFIX = ValidationError.PREFIX + 'Ошибка конфигурации: '


class EnvValidationError(ValidationError):
    '''Исключение при работе с переменными окружения'''
    PREFIX = ValidationError.PREFIX + 'Ошибка env: '


class HtmlToPdfValidationError(ValidationError):
    '''Исключение при преобразовании HTML в PDF'''
    PREFIX = ValidationError.PREFIX + 'Ошибка преобразования HTML в PDF: '


class ImportValidationError(ValidationError):
    '''Исключение при импорте не установленной библиотеки'''
    PREFIX = ValidationError.PREFIX + 'Ошибка импорта: '


def validate_env_file() -> None:
    '''Проверка на отсутствие файла .env'''
    msg = 'Отсутствует файл .env в корневой директории программы'
    env_path = Path.cwd() / '.env'
    if not env_path.exists():
        raise EnvValidationError(msg)


def validate_bot_token() -> None:
    '''Проверка на отсутствие токена бота в файле .env'''
    msg = 'Не установлен токен бота в переменной BOT_TOKEN в файле .env'
    if os.getenv('BOT_TOKEN') is None:
        raise EnvValidationError(msg)


def validate_mail_credentials() -> None:
    '''Проверка на отсутствие адреса и пароля почты в файле .env'''
    msg = 'Не устанвлены логин и/или пароль почты в переменных MAIL_ADRESS и MAIL_PASSWORD в файле .env'
    if not os.getenv('MAIL_ADDRESS') or not os.getenv('MAIL_PASSWORD'):
        raise EnvValidationError(msg)


def validate_chats() -> None:
    '''Проверка на пустой список с чатами для отправки рассылок'''
    msg = 'Не передано ни одного ID чата в переменную CHATS_IDS_TO_SEND в файле configs.py'
    if isinstance(CHATS_TO_SEND, SimpleNamespace):
        num_chats = len(vars(CHATS_TO_SEND))
    else:
        num_chats = len(CHATS_TO_SEND)
    if num_chats == 0:
        logger.warning(msg)


def validate_imports() -> None:
    '''Проверка на установленные библиотеки и ошибки импортов'''
    validation_errors = []
    import_module_names = [
        'aioimaplib',
        'aiogram',
        'bs4',
        'apscheduler',
    ]
    if SendSettingsConfig.send_pdf_to_proglib:
        import_module_names.append('weasyprint')

    for module_name in import_module_names:
        try:
            importlib.import_module(module_name)
        except ModuleNotFoundError as ex:
            msg = f'Библиотека {module_name} не установлена'
            validation_errors.append(msg)
        except Exception as ex:
            msg = f'Ошибка при импорте библиотеки {module_name}\nКод ошибки:\n{ex}'
            validation_errors.append(msg)

    if len(validation_errors) > 0:
        errors_msg = '\n'.join(validation_errors)
        msg = 'Валидация импортов завершена, обнаружены ошибки:\n' + errors_msg
        raise ImportValidationError(msg)


async def validate_html_to_pdf() -> None:
    '''Проверка преобразования HTML cодержимого веб-страницы в PDF'''
    web_link = 'https://geteml.com/ru/web_letter?action=6t8bgbygi56tsrtfj557bj6pejsawgpsg9wck6fbi6qpr11i8py3o'
    try:
        pdf_file_name = await UrlToPdf.pdf_from_web_link(web_link)
        if pdf_file_name is None:
            msg = 'Функция pdf_from_web_link завершилась с ошибкой, подробности в логах'
            raise HtmlToPdfValidationError(msg)
            
        if Path(pdf_file_name).is_file():
            msg = f'Валидация преобразования HTML в PDF завершена без ошибок, создан PDF файл: {pdf_file_name}'
            logger.info(msg)
        else:
            msg = 'Функция pdf_from_web_link отработала без ошибки, но PDF файл отсутствует'
            raise HtmlToPdfValidationError(msg)

    except Exception as ex:
        msg = f'Непредвиденная ошибка работы функции pdf_from_web_link\nКод ошибки:\n{ex}'
        raise HtmlToPdfValidationError(msg)


async def run_validation(
    func: Callable | Coroutine, 
    exceptions: list[Exception], 
    is_async: bool = False,
    *args, **kwargs,
    ) -> str | None:
    '''Запуск функции или корутины func с обработкой исключений'''
    try:
        if is_async:
            await func(*args, **kwargs,)
        else:
            func(*args, **kwargs)
    except exceptions as ex:
        return f'Ошибка валидации функции {func}\nКод ошибки:\n{ex}'
    except Exception as ex:
        return f'Непредвиденная ошибка валидации функции {func}\nКод ошибки:\n{ex}'
    return None


async def validate_all(validate_pdf: bool = False) -> None:
    '''Запуск всех добавленных проверок'''
    validation_errors = []
    validation_exceptions = (
        ConfigValidationError,
        EnvValidationError,
        HtmlToPdfValidationError,
        ImportValidationError,
        )
    validation_funcs = [
        validate_env_file,
        validate_bot_token,
        validate_mail_credentials,
        validate_imports,
        validate_chats,
    ]

    for func in validation_funcs:
        error = await run_validation(func, validation_exceptions)
        if error is not None:
            validation_errors.append(error)

    if validate_pdf and SendSettingsConfig.send_pdf_to_proglib:
        error = await run_validation(validate_html_to_pdf, validation_exceptions, is_async=True)
        if error is not None:
            validation_errors.append(error)

    if len(validation_errors) == 0:
        logger.info('Все функции валидации завершены без ошибок')
    else:
        errors_msg = '\n'.join(validation_errors)
        msg = 'Валидация всех функций завершена, обнаружены ошибки:\n' + errors_msg
        logger.error(msg, exc_info=True)
        raise ValidationError(msg)


if __name__ == '__main__':
    validate_pdf = SendSettingsConfig.send_pdf_to_proglib
    asyncio.run(validate_all(validate_pdf=validate_pdf))
