from typing import Any, Callable
from dataclasses import dataclass, field
from pytz.tzinfo import BaseTzInfo


@dataclass
class ChatConfig:
    '''Конфиг чата'''
    chat_id: int


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
class ScheduleBaseConfig:
    '''Базовый конфиг для рассылки'''
    schedule_config: ScheduleKwargsConfig
    admin_chat: ChatConfig
    chats: list[ChatConfig]
    parse_func: Callable[['ScheduleBaseConfig'], str | tuple[str, str]]
    bot: Any = field(default=None, init=False)

        
@dataclass
class ScheduleEmailConfig(ScheduleBaseConfig):
    '''Конфиг для рассылки сообщений из электронной почты'''
    mail_folder: str
    target_email_sender: str
    email_numbers: dict[int, bool] = field(default_factory=dict, init=False)


@dataclass
class ScheduleReminderConfig(ScheduleBaseConfig):
    '''Конфиг для рассылки напоминаний'''
    reminder_link: str
    reminder_time: str
    
    def __post_init__(self):
        self.message_to_send = (
            f'🎓 Ссылка на консультацию сегодня '
            f'в {self.reminder_time} МСК\n{self.reminder_link}'
        )
