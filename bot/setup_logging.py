import sys
import logging
from datetime import datetime

from configs.chats_settings import TIMEZONE


def setup_logging(log_to_file: bool, level: int) -> None:
    '''Настройка логгирования под конкретный часовой пояс'''
    logging.Formatter.converter = lambda *args: datetime.now(tz=TIMEZONE).timetuple()
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_to_file:
        log_file_name = 'bot_log.log'
        handlers.append(logging.FileHandler(log_file_name))
    
    format = '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s: %(message)s'
    logging.basicConfig(
        level=level,
        format=format,
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=handlers,
        force=True,
    )


LOG_TO_FILE = True
LEVEL = logging.INFO
setup_logging(log_to_file=LOG_TO_FILE, level=LEVEL)

