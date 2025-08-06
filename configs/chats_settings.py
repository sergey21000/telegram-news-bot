import logging
from importlib.util import find_spec
from dataclasses import dataclass
from types import SimpleNamespace

import pytz
from pytz.tzinfo import BaseTzInfo

from configs.base import ChatConfig, AdminChatConfig


# часовой пояс
TIMEZONE: BaseTzInfo = pytz.timezone('Europe/Moscow')


# =============== УСТАНОВКА ЧАТОВ ДЛЯ РАССЫЛКИ ===================

# ID чата админа для отправки отчетов об ошибках (необязательно, установить None если нет)
ADMIN_CHAT: AdminChatConfig = AdminChatConfig(chat_id=1025909168)
# ADMIN_CHAT: AdminChatConfig = AdminChatConfig(chat_id=None)

# чаты для рассылки новостей (обязательно)
# формат: CHAT_NAME=ChatConfig(chat_id=CHAT_ID)
CHATS_TO_SEND: dict[str, ChatConfig] = dict(
    ML_2025_CHAT=ChatConfig(chat_id=-1002633135386),
    ML_2025_2_CHAT=ChatConfig(chat_id=-1002740121366),
)


# =============== НАСТРОЙКИ РАССЫЛКИ ============================

@dataclass
class SendSettingsConfig:
    '''Конфиг настройки параметров рассылки'''
    max_attempts: int = 10  # кол-во попыток выполнения функции получения рассылки
    delay_seconds: int = 1800  # интервал между попытками, сек
    send_errors_to_admin: bool = True  # отправлять админу инфо о том что попытки исчерпаны
    send_pdf_to_proglib: bool = False  # отправлять PDF вместе с рассылкой Proglib


# ==================================================================

# проверка что библиотека weasyprint установлена если включено send_pdf_to_proglib
if SendSettingsConfig.send_pdf_to_proglib:
    if find_spec('weasyprint') is None:
        logger = logging.getLogger(__name__)
        logger.warning('Библиотека weasyprint не установлена, рассылка будет происходить без PDF')
        SendSettingsConfig.send_pdf_to_proglib = False

CHATS_TO_SEND = SimpleNamespace(**CHATS_TO_SEND)
[setattr(value, 'chat_name', key) for key, value in vars(CHATS_TO_SEND).items()]
