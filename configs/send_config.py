import pytz
from pytz.tzinfo import BaseTzInfo
from dataclasses import dataclass, field
from typing import Any

from configs.chats_settings import ADMIN_CHAT, CHATS_TO_SEND, TIMEZONE
from configs.config_classes import (
    ChatConfig,
    AdminChatConfig,
    ScheduleKwargsConfig,
    ScheduleBaseConfig,
    ScheduleReminderConfig,
    ScheduleEmailConfig,
)
from bot.parser import EmailParser


class BaseConfig:
    '''Базовый конфиг для конфига с рассылками'''
    timezone: pytz.tzinfo.BaseTzInfo = TIMEZONE
    admin_chat: ChatConfig = field(default_factory=lambda: ADMIN_CHAT, init=False)
    bot: Any = field(default=None, init=False)
    scheduler: Any = field(default=None, init=False)

    def __setattr__(self, key: str, value: Any) -> None:
        super().__setattr__(key, value)
        if key in ('bot',):
            for config in self.get_all_configs():
                setattr(config, key, value)

    def get_reminder_configs(self) -> list[ScheduleReminderConfig]:
        return [value for key, value in self.__dict__.items() if key.endswith('_reminder_config')]

    def get_email_configs(self) -> list[ScheduleEmailConfig]:
        return [value for key, value in self.__dict__.items() if key.endswith('_email_config')]

    def get_all_configs(self)-> list[ScheduleBaseConfig]:
        return self.get_reminder_configs() + self.get_email_configs()


# ================= КОНФИГИ РАССЫЛКИ ============================

@dataclass
class Config(BaseConfig):
    '''Конфиг с конфигами для рассылок'''

    # ================= КОНФИГИ РАССЫЛКИ ИЗ ПОЧТЫ ==========================

    proglib_email_config: ScheduleEmailConfig = field(default_factory=lambda: ScheduleEmailConfig(
        schedule_config=ScheduleKwargsConfig(
            day_of_week='sat',
            hour=12,
            minute=30,
            timezone=TIMEZONE,
        ),
        admin_chat=ADMIN_CHAT,
        chats=CHATS_TO_SEND,
        parse_func=EmailParser.get_proglib_send,
        mail_folder='INBOX/proglib',
        target_email_sender='Proglib AI',
        )
    )

    habr_email_config: ScheduleEmailConfig = field(default_factory=lambda: ScheduleEmailConfig(
        schedule_config=ScheduleKwargsConfig(
            day_of_week='*',
            hour=12,
            minute=30,
            timezone=TIMEZONE,
        ),
        admin_chat=ADMIN_CHAT,
        chats=CHATS_TO_SEND,
        parse_func=EmailParser.get_habr_send,
        mail_folder='INBOX/News',
        target_email_sender='Habr',
        )
    )

    # ================= КОНФИГИ НАПОМИНАНИЙ ========================

    # test_reminder_config: ScheduleReminderConfig = field(default_factory=lambda: ScheduleReminderConfig(
    #     schedule_config=ScheduleKwargsConfig(
    #         day_of_week='*',  # дни рассылки (mon,tue,wed,thu,fri,sat,sun)
    #         hour=10,  # часы рассылки
    #         minute=00,  # минуты рассылки
    #         end_date='2025-02-01',  # дата окончания рассылки
    #         timezone=TIMEZONE,  # часовой пояс
    #     ),
    #     admin_chat=ADMIN_CHAT,  # чат админа для отправки отчетов об ошибках
    #     chats=CHATS_TO_SEND,  # чаты для рассылки
        
    #     # функция получения сообщения для рассылки
    #     # принимает текущий экземпляр конфига ScheduleReminderConfig
    #     parse_func=EmailParser.get_reminder_send,
        
    #     # доп аргументы, присущие конкретному конфигу
    #     reminder_link='https://my.mts-link.ru/j/innopolisooc/webinar_link1',
    #     reminder_time='19:00',
    #     )
    # )
