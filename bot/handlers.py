import io
import logging
from urllib.parse import urlsplit

import aiohttp
from aiogram import Bot, Router
from aiogram.enums import ContentType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import BaseFilter, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    Message,
    WebAppInfo,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import FormData
from config import settings

logger = logging.getLogger(__name__)

router = Router()

START_TEXT = "Добро пожаловать! Каталог товаров доступен в мини-приложении."
ADMIN_PROMPT_TEXT = (
    "Отлично! Пришлите фото с подпиской - фото станет картинкой товара, "
    "а подписка станет его названием."
)

CREATE_CALLBACK = "admin:new"
DELETE_CALLBACK_PREFIX = "admin:del:"


def mini_app_available(url: str) -> bool:
    # tg открывает web только по по с-ке
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    if parts.scheme != "https" or not host:
        return False
    return host not in {"localhost", "127.0.0.1", "::1"}


def is_admin(message: Message) -> bool:
    user = message.from_user
    return user is not None and user.id in settings.admin_id_set


def is_admin_callback(callback: CallbackQuery) -> bool:
    user = callback.from_user
    return user is not None and user.id in settings.admin_id_set


class PhotoFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.content_type == ContentType.PHOTO


async def create_product_in_backend(name: str, image_bytes: bytes) -> dict:
    form = FormData()
    form.add_field("name", name)
    form.add_field(
        "image",
        io.BytesIO(image_bytes),
        filename="product.jpg",
        content_type="image/jpeg",
    )

    async with (
        aiohttp.ClientSession() as session,
        session.post(
            f"{settings.backend_url.rstrip('/')}/product/upload/",
            data=form,
            timeout=aiohttp.ClientTimeout(total=30),
        ) as response,
    ):
        if response.status >= 400:
            detail = await response.json()
            raise RuntimeError(
                f"Backend не создал товар: HTTP {response.status} {detail}"
            )
        return await response.json()


async def delete_product_in_backend(product_id: int) -> bool:
    async with (
        aiohttp.ClientSession() as session,
        session.delete(
            f"{settings.backend_url.rstrip('/')}/product/{product_id}",
            timeout=aiohttp.ClientTimeout(total=10),
        ) as response,
    ):
        return response.status == 204


@router.message(CommandStart())
async def start(message: Message) -> None:
    url = settings.mini_app_url.strip()

    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="Открыть каталог", web_app=WebAppInfo(url=url))
    )
    if is_admin(message):
        builder.add(
            InlineKeyboardButton(
                text="➕ Добавить товар", callback_data=CREATE_CALLBACK
            )
        )

    if not mini_app_available(url):
        # localhost и http Telegram отклоняет как URL кнопки, поэтому отдаём ссылку текстом
        text = f"{START_TEXT}\n\n{url}" if url else START_TEXT
        await message.answer(text)
        return

    try:
        await message.answer(START_TEXT, reply_markup=builder.as_markup())
    except TelegramBadRequest:
        logger.exception("Telegram отклонил кнопку с URL %s", url)
        await message.answer(f"{START_TEXT}\n\n{url}")


@router.callback_query()
async def callback_handler(callback: CallbackQuery) -> None:
    data = callback.data or ""

    if data == CREATE_CALLBACK:
        if not is_admin_callback(callback):
            await callback.answer("Недостаточно прав", show_alert=True)
            return
        await callback.answer()
        await callback.message.answer(ADMIN_PROMPT_TEXT)
        return

    if data.startswith(DELETE_CALLBACK_PREFIX):
        if not is_admin_callback(callback):
            await callback.answer("Недостаточно прав", show_alert=True)
            return
        product_id = int(data[len(DELETE_CALLBACK_PREFIX) :])
        deleted = await delete_product_in_backend(product_id)
        if deleted:
            await callback.answer("Товар удалён", show_alert=True)
        else:
            await callback.answer("Не удалось удалить товар", show_alert=True)
        return

    await callback.answer("Неизвестная кнопка", show_alert=True)


@router.message(PhotoFilter())
async def create_product(message: Message, bot: Bot) -> None:
    if not is_admin(message):
        # добавление товаров доступно только администратору
        return

    caption = (message.caption or "").strip()
    if not caption:
        await message.reply("Подпишите фото — так будет название товара.")
        return

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    stream = await bot.download_file(file.file_path)
    image_bytes = stream.read() if stream is not None else b""

    product = await create_product_in_backend(caption, image_bytes)
    product_id = product.get("id")

    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="🗑 Удалить товар",
            callback_data=f"{DELETE_CALLBACK_PREFIX}{product_id}",
        )
    )

    await message.answer(
        f"Товар «{caption}» опубликован",
        reply_markup=builder.as_markup(),
    )
