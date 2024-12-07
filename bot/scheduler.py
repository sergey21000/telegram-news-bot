from apscheduler.triggers.cron import CronTrigger

from configs.send_config import Config
from bot.message_sender import get_and_send_message


async def start_scheduler(config: Config):
    '''Запуск планировщиком задач из конфигов, которые определены в config'''
    scheduler = config.scheduler
    for send_config in config.get_all_configs():
        if len(send_config.chats) == 0:
            continue
        trigger = CronTrigger(**send_config.schedule_config.asdict())
        scheduler.add_job(get_and_send_message, trigger=trigger, args=[send_config])
    scheduler.start()
