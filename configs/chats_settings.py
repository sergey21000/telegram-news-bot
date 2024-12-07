import logging
from importlib.util import find_spec
from dataclasses import dataclass, field

import pytz
from pytz.tzinfo import BaseTzInfo

from configs.config_classes import ChatConfig, AdminChatConfig


# =============== УСТАНОВКА ЧАТОВ ДЛЯ РАССЫЛКИ ===================

# часовой пояс
TIMEZONE: BaseTzInfo = pytz.timezone('Europe/Moscow')

# ID чата админа для отправки отчетов об ошибках (необязательно)
ADMIN_CHAT_ID = None
# ADMIN_CHAT_ID = 123456789

# ID чатов для рассылки новостей (обязательно)
CHATS_IDS_TO_SEND = [
    # 123456789,
]

# =============== НАСТРОЙКИ РАССЫЛКИ ============================

@dataclass
class SendSettingsConfig:
    '''Конфиг настройки параметров рассылки'''
    max_attempts: int = 10  # кол-во попыток выполнения функции получения рассылки
    delay_seconds: int = 1800  # интервал между попытками, сек
    send_errors_to_admin: bool = True  # отправлять админу инфо о том что попытки исчерпаны
    send_pdf_to_proglib: bool = True  # отправлять PDF вместе с рассылкой Proglib


# ==================================================================

ADMIN_CHAT: AdminChatConfig = AdminChatConfig(chat_id=ADMIN_CHAT_ID)
CHATS_TO_SEND: list[ChatConfig] = [ChatConfig(chat_id=id) for id in CHATS_IDS_TO_SEND]

# ==================================================================

# проверка что библиотека weasyprint установлена если включено send_pdf_to_proglib
if SendSettingsConfig.send_pdf_to_proglib:
    if find_spec('weasyprint') is None:
        logger = logging.getLogger(__name__)
        logger.warning('Библиотека weasyprint не установлена, рассылка будет происходить без PDF')
        SendSettingsConfig.send_pdf_to_proglib = False
