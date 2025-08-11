from typing import Callable
from dataclasses import dataclass, field
from pytz.tzinfo import BaseTzInfo


@dataclass
class ChatConfig:
    '''Конфиг чата'''
    chat_id: int
    chat_name: str | None = None


@dataclass
class AdminChatConfig:
    '''Конфиг чата админа'''
    chat_id: int | None


@dataclass
class ScheduleKwargsConfig:
    '''Конфиг раписания для планировщика задач AsyncIOScheduler'''
    day_of_week: str
    hour: int
    minute: int
    timezone: BaseTzInfo
    end_date: str | None = None
    jitter: int = 10
    
    def asdict(self):
        return self.__dict__


@dataclass
class SendBaseConfig:
    '''Базовый конфиг для рассылки'''
    schedule_kwargs_config: ScheduleKwargsConfig
    admin_chat: AdminChatConfig
    chats: list[ChatConfig]
    parse_func: Callable[['SendBaseConfig'], str | tuple[str, str]]
    disable_notification: bool
    is_active: bool

    def __post_init__(self):
        if isinstance(self.chats, ChatConfig):
            self.chats = [self.chats]


@dataclass
class SendEmailConfig(SendBaseConfig):
    '''Конфиг для рассылки сообщений из электронной почты'''
    mail_folder: str
    target_email_sender: str
    email_numbers: dict[int, bool] = field(default_factory=dict, init=False)


@dataclass
class SendReminderConfig(SendBaseConfig):
    '''Конфиг для рассылки напоминаний'''
    reminder_link: str
    reminder_time: str
    
    def __post_init__(self):
        self.message_to_send = (
            f'🎓 Ссылка на консультацию сегодня '
            f'в {self.reminder_time} МСК\n{self.reminder_link}'
        )


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
