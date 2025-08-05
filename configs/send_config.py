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

# class Config(BaseConfig):
#     '''Конфиг с конфигами для рассылок'''

#     # ================= КОНФИГИ РАССЫЛКИ ИЗ ПОЧТЫ ==========================

#     habr_email_config = SendEmailConfig(
#         schedule_kwargs_config=ScheduleKwargsConfig(
#             day_of_week='*',
#             hour=12,
#             minute=30,
#             timezone=TIMEZONE,
#         ),
#         admin_chat=ADMIN_CHAT,
#         chats=[CHATS_TO_SEND.ML_2025_2_CHAT],
#         parse_func=EmailParser.get_habr_send,
#         mail_folder='INBOX/News',
#         target_email_sender='Habr',
#         is_active=True,
#     )

#     # ================= КОНФИГИ НАПОМИНАНИЙ ========================

#     ml_2025_reminder_config = SendReminderConfig(
#         schedule_kwargs_config=ScheduleKwargsConfig(
#             day_of_week='wed,thu',
#             hour=10,
#             minute=00,
#             end_date='2025-12-25',
#             timezone=TIMEZONE,
#         ),
#         admin_chat=ADMIN_CHAT,
#         chats=[CHATS_TO_SEND.ML_2025_CHAT],
#         parse_func=EmailParser.get_reminder_send,
#         reminder_link='https://my.mts-link.ru/j/innopolisooc/ml-2025',
#         reminder_time='19:00',
#         is_active=True,
#     )

#     ml_2025_2_reminder_config = SendReminderConfig(
#         schedule_kwargs_config=ScheduleKwargsConfig(
#             day_of_week='tue,fri',
#             hour=10,
#             minute=00,
#             end_date='2026-04-10',
#             timezone=TIMEZONE,
#         ),
#         admin_chat=ADMIN_CHAT,
#         chats=[CHATS_TO_SEND.ML_2025_2_CHAT],
#         parse_func=EmailParser.get_reminder_send,
#         reminder_link='https://my.mts-link.ru/j/innopolisooc/ml-2025-2',
#         reminder_time='19:00',
#         is_active=False,
#     )








class Config(BaseConfig):
    '''Конфиг с конфигами для рассылок'''

    # ================= КОНФИГИ РАССЫЛКИ ИЗ ПОЧТЫ ==========================

    habr_email_config = SendEmailConfig(
        schedule_kwargs_config=ScheduleKwargsConfig(
            day_of_week='*',
            hour=1,
            minute=5,
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
            day_of_week='tue,thu',
            hour=1,
            minute=8,
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
            hour=1,
            minute=5,
            end_date='2026-04-10',
            timezone=TIMEZONE,
        ),
        admin_chat=ADMIN_CHAT,
        chats=[ADMIN_CHAT],
        parse_func=EmailParser.get_reminder_send,
        reminder_link='https://my.mts-link.ru/j/innopolisooc/ml-2025-2',
        reminder_time='19:00',
        is_active=False,
    )





# ========================= EXAMPLE ===========================

# @dataclass
# class Config(BaseConfig):
#     '''Конфиг с конфигами для рассылок'''

    # ================= КОНФИГИ РАССЫЛКИ ИЗ ПОЧТЫ ==========================

    # proglib_email_config = ScheduleEmailConfig(
        # schedule_kwargs_config=ScheduleKwargsConfig(
            # day_of_week='sat',
            # hour=17,
            # minute=28,
            # timezone=TIMEZONE,
        # ),
        # admin_chat=ADMIN_CHAT,
        # chats=CHATS_TO_SEND,
        # parse_func=EmailParser.get_proglib_send,
        # mail_folder='INBOX/proglib',
        # target_email_sender='Proglib AI',
    # )

    # ================= КОНФИГИ НАПОМИНАНИЙ ========================

    # test_reminder_config = SendReminderConfig(
    #     schedule_kwargs_config=ScheduleKwargsConfig(
    #         day_of_week='*',  # дни рассылки (mon,tue,wed,thu,fri,sat,sun)
    #         hour=10,  # часы рассылки
    #         minute=00,  # минуты рассылки
    #         end_date='2025-02-01',  # дата окончания рассылки (год-месяц-день)
    #         timezone=TIMEZONE,  # часовой пояс
    #     ),
    #     admin_chat=ADMIN_CHAT,  # чат админа для отправки отчетов об ошибках
    #     chats=CHATS_TO_SEND,  # чаты для рассылки
        
    #     # функция получения сообщения для рассылки
    #     # принимает текущий экземпляр конфига SendReminderConfig
    #     parse_func=EmailParser.get_reminder_send,
        
    #     # доп аргументы, присущие конкретному конфигу
    #     reminder_link='https://my.mts-link.ru/j/innopolisooc/webinar_link1',
    #     reminder_time='19:00',
    # )