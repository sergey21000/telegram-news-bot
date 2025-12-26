import os

from configs.chats_settings import (
    TIMEZONE,
    ADMIN_CHAT,
    CHATS_TO_SEND,
)
from configs.base import (
    ScheduleKwargsConfig,
    SendReminderConfig,
    SendEmailConfig,
    BaseConfig,
)
from bot.parser import EmailParser


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
        chats=[CHATS_TO_SEND.ML_2025_CHAT, CHATS_TO_SEND.ML_2025_2_CHAT],
        parse_func=EmailParser.get_habr_send,
        mail_folder='INBOX/News',
        target_email_sender='Habr',
        disable_notification=True,
        is_active=True,
    )

    # ================= КОНФИГИ НАПОМИНАНИЙ ========================

    # ml_2025_reminder_config = SendReminderConfig(
        # schedule_kwargs_config=ScheduleKwargsConfig(
            # day_of_week='wed,thu',  # (mon,tue,wed,thu,fri,sat,sun)
            # hour=10,
            # minute=00,
            # end_date='2025-12-25',
            # timezone=TIMEZONE,
        # ),
        # admin_chat=ADMIN_CHAT,
        # chats=[CHATS_TO_SEND.ML_2025_CHAT],
        # parse_func=EmailParser.get_reminder_send,
        # reminder_link=os.getenv('ML_2025_REMINDER_LINK'),
        # reminder_time='19:00',
        # disable_notification=True,
        # is_active=True,
    # )

    ml_2025_2_1_reminder_config = SendReminderConfig(
        schedule_kwargs_config=ScheduleKwargsConfig(
            day_of_week='tue',
            hour=10,
            minute=00,
            end_date='2026-04-10',
            timezone=TIMEZONE,
        ),
        admin_chat=ADMIN_CHAT,
        chats=[CHATS_TO_SEND.ML_2025_2_CHAT],
        parse_func=EmailParser.get_reminder_send,
        reminder_link=os.getenv('ML_2025_2_REMINDER_LINK'),
        reminder_time='18:00',
        disable_notification=True,
        is_active=True,
    )

    ml_2025_2_2_reminder_config = SendReminderConfig(
        schedule_kwargs_config=ScheduleKwargsConfig(
            day_of_week='fri',
            hour=10,
            minute=00,
            end_date='2026-04-10',
            timezone=TIMEZONE,
        ),
        admin_chat=ADMIN_CHAT,
        chats=[CHATS_TO_SEND.ML_2025_2_CHAT],
        parse_func=EmailParser.get_reminder_send,
        reminder_link=os.getenv('ML_2025_2_REMINDER_LINK'),
        reminder_time='18:00',
        disable_notification=True,
        is_active=True,
    )
