from aiogram import F, Router, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode

from configs.chats_settings import ADMIN_CHAT


router = Router()

async def admin_filter(message):
    if ADMIN_CHAT.chat_id is not None:
        return message.from_user.id == ADMIN_CHAT.chat_id
    return True

@router.message(Command('getid'), admin_filter)
async def get_chat_id(message: Message, bot: Bot):
    info = f'<b>Название чата:</b> {message.chat.full_name}\n<b>ID чата:</b> {message.chat.id}'
    if ADMIN_CHAT.chat_id is not None:
        await bot.send_message(ADMIN_CHAT.chat_id, info, parse_mode=ParseMode.HTML)
        await message.delete()
    else:
        await message.answer(info, parse_mode=ParseMode.HTML)

