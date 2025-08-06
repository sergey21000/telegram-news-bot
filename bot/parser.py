import os
import logging
import asyncio
import aioimaplib
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

import aiohttp

import email
import email.message
from email.header import decode_header
from email import utils

import pytz
from pytz.tzinfo import BaseTzInfo

from bs4 import BeautifulSoup

from dotenv import load_dotenv
load_dotenv()

from configs.base import SendReminderConfig, SendEmailConfig
from configs.chats_settings import SendSettingsConfig

if SendSettingsConfig.send_pdf_to_proglib:
    from weasyprint import HTML, CSS
    logging.getLogger('weasyprint').setLevel(logging.ERROR)


logger = logging.getLogger(__name__)


@dataclass
class Message:
    '''Класс для хранения объекта сообщения электронной почты'''
    email_message: email.message.Message
    email_sender: str
    email_num: int
    email_datetime: datetime


class EmailParser:
    '''Класс для работы с сообщениями электронной почты и формирования рассылок'''
    
    # ========================= COMMON UTILS ===============================

    @classmethod
    async def get_last_email_message(cls, email_config: SendEmailConfig) -> Message:
        '''Получение последнего письма из папки почты email_config.mail_folder'''
        imap_client = aioimaplib.IMAP4_SSL(host='imap.mail.ru')
        await imap_client.wait_hello_from_server()
        await imap_client.login(os.getenv('MAIL_ADDRESS'), os.getenv('MAIL_PASSWORD'))

        res, data = await imap_client.select(email_config.mail_folder)
        if res != 'OK':
            await imap_client.logout()
            raise Exception(f'Не удалось выбрать папку почты {email_config.mail_folder}')

        res, numbers = await imap_client.search('ALL')
        if len(numbers) == 0:
            await imap_client.logout()
            raise Exception(f'В папке почты {email_config.mail_folder} нет писем')

        email_numbers = numbers[0].split()
        while True:
            if len(email_numbers) == 0:
                await imap_client.logout()
                raise Exception(f'Не не найдено письма с отправителем {email_config.target_email_sender}')

            email_num = email_numbers.pop(-1).decode('utf-8')
            res, msg = await imap_client.fetch(email_num, '(RFC822)')
            email_body = msg[1]
            email_message = email.message_from_bytes(email_body)
            email_sender = cls.get_email_sender(email_message)
            if email_config.target_email_sender in email_sender:
                break
            else:
                continue

        email_datetime = cls.get_email_datetime(email_message, email_config.schedule_kwargs_config.timezone)
        message = Message(
            email_message=email_message,
            email_sender=email_sender,
            email_num=email_num,
            email_datetime=email_datetime,
            )
        await imap_client.logout()
        return message


    @classmethod
    async def get_available_email_message(cls, email_config: SendEmailConfig) -> Message:
        '''Получение письма с отправителем email_config.target_email_sender, которое еще не было отправлено'''
        message = await cls.get_last_email_message(email_config)
        if message.email_num in email_config.email_numbers:
            raise Exception(f'Письмо под номером {message.email_num} от отправителя {email_config.target_email_sender} уже есть в БД')
        current_datetime = datetime.now(email_config.schedule_kwargs_config.timezone)
        if message.email_datetime.date() < current_datetime.date():
            raise Exception(f'Письмо от отправителя {email_config.target_email_sender} '
                            f'раньше сегодняшней даты ({message.email_datetime.date()} < {current_datetime.date()})')
        email_config.email_numbers[message.email_num] = True
        return message


    @staticmethod
    def get_email_sender(email_message: email.message.Message) -> str:
        '''Получение названия отправителя письма из письма электронной почты'''
        from_ = email_message.get('From')
        decoded_header = decode_header(from_)
        email_sender = ''
        for part, encoding in decoded_header:
            if isinstance(part, bytes):
                email_sender += part.decode(encoding or 'utf-8')
            else:
                email_sender += part
        return email_sender


    @staticmethod
    def get_email_datetime(email_message: email.message.Message, timezone: BaseTzInfo) -> str:
        '''Получение даты получения письма из письма электронной почты'''
        datestring = email_message['date']
        datetime_obj = utils.parsedate_to_datetime(datestring)
        email_datetime = datetime_obj.astimezone(timezone)
        return email_datetime


    @staticmethod
    def get_content_from_email_message(email_message: email.message.Message, to_html: bool) -> str | None:
        '''Парсинг текста или html содержимого из письма электронной почты'''
        content = None
        content_type = 'text/html' if to_html else 'text/plain'
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == content_type:
                    content = part.get_payload(decode=True).decode()
                    break
        elif email_message.get_content_type() == content_type:
            content = email_message.get_payload(decode=True).decode()
        return content

    # ======================== PROGLIB UTILS ==================================

    @staticmethod
    def get_web_link_from_html(html_content: str, search_string: str) -> str:
        '''Парсинг ссылки с текстом search_string из html содержимого'''
        soup = BeautifulSoup(html_content, 'html.parser')
        web_link = soup.find('a', string=search_string)
        if not web_link:
            raise Exception('Не удалось получить URL ссылку из письма')
        web_link = web_link['href']
        return web_link

    # ======================== HABR UTILS ==================================

    @classmethod
    async def get_text_from_habr_message(cls, message: Message) -> str:
        '''Формирование текста рассылки новостей из письма от Хабр'''
        email_text = cls.get_content_from_email_message(message.email_message, to_html=False)
        emails_list = email_text.split('\r\n\r\n')
        emails_list = emails_list[2:-6]
        message_to_remove = '\r\nБыть в курсе событий\r\n---'
        if message_to_remove in emails_list:
            emails_list.remove(message_to_remove)
        message_to_send = f'<u><b>📨 Ежедневная рассылка статей от Хабр {message.email_datetime.date()}</b></u>\n\n'
        for email_msg in emails_list:
            if 'https://' in email_msg:
                email_title, email_link = email_msg.split('https://')
                email_title = email_title.strip()
                email_link = 'https://' + email_link.strip()
                message_to_send += f'📰 <b>{email_title}</b>\n'
                message_to_send += f'<a href="{email_link}">🔗 Читать статью</a>\n\n'
        return message_to_send

    # ========================= GENERAL UTILS ======================

    @classmethod
    async def get_proglib_send(cls, email_config: SendEmailConfig) -> tuple[str, str]:
        '''Получение и формирование рассылки новостей из письма от Proglib (PDF и ссылка на сайт с новостью)'''
        message = await cls.get_available_email_message(email_config)
        html_content = cls.get_content_from_email_message(message.email_message, to_html=True)
        web_link = cls.get_web_link_from_html(html_content, search_string='Веб-версия')
        
        pdf_file_name = None
        if SendSettingsConfig.send_pdf_to_proglib:
            pdf_file_name = await UrlToPdf.pdf_from_web_link(web_link)
            
        message_to_send = f'<u><b>📨 Еженедельная рассылка ИИ новоcтей от Proglib AI {message.email_datetime.date()}</b></u>\n\n'
        message_to_send += f'<a href="{web_link}">🔗 Веб-версия</a>\n'
        # message_to_send += '\n#proglibрассылка'
        return message_to_send, pdf_file_name


    @classmethod
    async def get_habr_send(cls, email_config: SendEmailConfig) -> str:
        '''Получение и формирование рассылки новостей из письма от Хабр'''
        message = await cls.get_available_email_message(email_config)
        message_to_send = await cls.get_text_from_habr_message(message)
        return message_to_send


    @staticmethod
    async def get_reminder_send(reminder_config: SendReminderConfig) -> str:
        '''Извлечение атрибута message_to_send из конфига для отправки напоминаний'''
        return reminder_config.message_to_send


# ================= HTML TO PDF ====================================

class UrlToPdf:
    '''Преобразование Web-страницы в PDF'''
    @staticmethod
    async def html_from_url(web_link: str) -> str:
        '''Получает HTML-контент по URL'''
        async with aiohttp.ClientSession() as session:
            async with session.get(web_link) as response:
                response.raise_for_status()
                return await response.text()


    @staticmethod
    def clean_html(html_content: str) -> str:
        '''Удаление из HTML нижней части страницы из рассылки от Proglib'''
        slice_indx = html_content.find('class="row row-3"')
        if slice_indx == -1:
            logger.warning('Маркер для обрезки HTML не найден')
            return html_content
        end_html = '<!-- End -->\n</body>\n</html>'
        cleaned_html = html_content[:slice_indx - 62] + end_html
        return cleaned_html


    @staticmethod
    def html_to_pdf(html_content: str, pdf_file_name: str, css: str | None) -> None:
        '''Преобразование HTML в PDF'''
        stylesheets = [] if css is None else [css]
        HTML(string=html_content).write_pdf(target=pdf_file_name, stylesheets=stylesheets)


    @classmethod
    async def pdf_from_web_link(cls, web_link: str, css: str = None) -> str | None:
        '''Получение HTML по ссылке и преобразование его в PDF'''
        pdf_file_name = 'news.pdf'
        try:
            html_content = await cls.html_from_url(web_link)
        except Exception as ex:
            msg = f'Не удалось получить HTML из URL {web_link}\nКод ошибки:\n{ex}'
            logger.error(msg, exc_info=True)
            return None
        try:
            cleaned_html = cls.clean_html(html_content)
        except Exception as ex:
            msg = f'Не удалось очистить HTML содержимое из ссылки {web_link}\nКод ошибки:\n{ex}'
            logger.warning(msg, exc_info=True)
            cleaned_html = html_content
        try:
            await asyncio.to_thread(cls.html_to_pdf, cleaned_html, pdf_file_name, css)
        except Exception as ex:
            msg = f'Не удалось преобразовать HTML в PDF из URL {web_link}\nКод ошибки:\n{ex}'
            logger.error(msg, exc_info=True)
            return None
        return pdf_file_name
