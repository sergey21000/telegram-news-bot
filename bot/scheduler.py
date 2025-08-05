from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from configs.send_config import Config
from bot.message_sender import get_and_send_message

 
async def start_scheduler(scheduler: AsyncIOScheduler, config: Config) -> None:
    '''Запуск планировщиком задач из конфигов, которые определены в config'''
    for send_config in config.get_all_configs():
        if not send_config.is_active:
            continue
        if len(send_config.chats) == 0:
            continue
        trigger = CronTrigger(**send_config.schedule_kwargs_config.asdict())
        scheduler.add_job(get_and_send_message, trigger=trigger, args=[send_config, config.bot])
    scheduler.start()
