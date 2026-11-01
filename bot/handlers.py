import logging
from urllib.parse import urlsplit

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, Message, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import settings

logger = logging.getLogger(__name__)

router = Router()

START_TEXT = "Добро пожаловать в INVIX! Каталог товаров доступен в мини-приложении."


def mini_app_available(url: str) -> bool:
    # tg открывает web только по по с-ке
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    if parts.scheme != "https" or not host:
        return False
    return host not in {"localhost", "127.0.0.1", "::1"}


@router.message(CommandStart())
async def start(message: Message) -> None:
    url = settings.mini_app_url.strip()

    # для теста добавил
    if not mini_app_available(url):
        text = f"{START_TEXT}\n\n{url}" if url else START_TEXT
        await message.answer(text)
        return

    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="Открыть каталог", web_app=WebAppInfo(url=url))
    )

    try:
        await message.answer(START_TEXT, reply_markup=builder.as_markup())
    except TelegramBadRequest:
        logger.exception("Telegram отклонил кнопку с URL %s", url)
        await message.answer(f"{START_TEXT}\n\n{url}")
