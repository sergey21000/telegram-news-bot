from configs.chats_settings import (
    TIMEZONE,
    ADMIN_CHAT,
    CHATS_TO_SEND,
)
from configs.config_classes import (
    ScheduleKwargsConfig,
    SendBaseConfig,
    SendReminderConfig,
    SendEmailConfig,
)
from bot.parser import EmailParser


class BaseConfig:
    '''Базовый конфиг для конфига с рассылками'''
    @classmethod
    def get_reminder_configs(cls) -> list[SendReminderConfig]:
        return [value for key, value in cls.__dict__.items() if key.endswith('_reminder_config')]

    @classmethod
    def get_email_configs(cls) -> list[SendEmailConfig]:
        return [value for key, value in cls.__dict__.items() if key.endswith('_email_config')]

    @classmethod
    def get_all_configs(cls) -> list[SendBaseConfig]:
        return cls.get_email_configs() + cls.get_reminder_configs()


# ================= КОНФИГИ РАССЫЛКИ ============================

class Config(BaseConfig):
    '''Конфиг с конфигами для рассылок'''

    # ================= КОНФИГИ РАССЫЛКИ ИЗ ПОЧТЫ ==========================

    habr_email_config = SendEmailConfig(
        schedule_kwargs_config=ScheduleKwargsConfig(
            day_of_week='*',
            hour=12,
            minute=30,
            timezone=TIMEZONE,
        ),
        admin_chat=ADMIN_CHAT,
        chats=[ADMIN_CHAT],
        parse_func=EmailParser.get_habr_send,
        mail_folder='INBOX/News',
        target_email_sender='Habr',
        is_active=True,
    )

    # ================= КОНФИГИ НАПОМИНАНИЙ ========================

    ml_2025_reminder_config = SendReminderConfig(
        schedule_kwargs_config=ScheduleKwargsConfig(
            day_of_week='wed,thu',
            hour=10,
            minute=00,
            end_date='2025-12-25',
            timezone=TIMEZONE,
        ),
        admin_chat=ADMIN_CHAT,
        chats=[ADMIN_CHAT],
        parse_func=EmailParser.get_reminder_send,
        reminder_link='https://my.mts-link.ru/j/innopolisooc/ml-2025',
        reminder_time='19:00',
        is_active=True,
    )

    ml_2025_2_reminder_config = SendReminderConfig(
        schedule_kwargs_config=ScheduleKwargsConfig(
            day_of_week='tue,fri',
            hour=10,
            minute=00,
            end_date='2026-04-10',
            timezone=TIMEZONE,
        ),
        admin_chat=ADMIN_CHAT,
        chats=[CHATS_TO_SEND.ML_2025_2_CHAT],
        parse_func=EmailParser.get_reminder_send,
        reminder_link='https://my.mts-link.ru/j/innopolisooc/ml-2025-2',
        reminder_time='19:00',
        is_active=False,
    )

