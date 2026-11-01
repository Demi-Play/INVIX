import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError
from config import settings
from handlers import router

logger = logging.getLogger(__name__)

RETRY_DELAY_SECONDS = 5


async def main() -> None:
    if not settings.telegram_bot_token:
        raise SystemExit("TELEGRAM_BOT_TOKEN не задан")

    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    try:
        while True:
            try:
                logger.info("Запуск бота в режиме long polling")
                await dispatcher.start_polling(
                    bot,
                    allowed_updates=dispatcher.resolve_used_update_types(),
                )
                return
            except TelegramNetworkError as exc:
                # сеть1 может  быть временно недоступны не уходитт в краш луп
                logger.warning(
                    "Telegram API недоступен (%s), повтор через %s с",
                    exc,
                    RETRY_DELAY_SECONDS,
                )
                await asyncio.sleep(RETRY_DELAY_SECONDS)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    asyncio.run(main())
