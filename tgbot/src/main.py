import logging
import os
from typing import List

import httpx
from api.api import Api
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import StateFilter
from telebot.asyncio_storage import StatePickleStorage

from shared.entities import User
from shared.logging import configure_logging
from shared.models import Database
from tgbot.src.view.handlers.add_database_from_file_handlers import (
    register_add_database_from_file_handlers,
)
from tgbot.src.view.handlers.add_database_handlers import (
    register_add_database_handlers,
)
from tgbot.src.view.handlers.delete_database_handlers import (
    register_delete_database_handlers,
)
from tgbot.src.view.handlers.get_state_handlers import (
    register_get_state_handlers,
)
from tgbot.src.view.handlers.menu_handlers import register_menu_handlers

load_dotenv()

logger = logging.getLogger("app")

token = os.getenv("BOT_TOKEN")
backend_url_prefix = os.getenv(
    "BACKEND_URL_PREFIX", "http://localhost:8001/api"
)

httpx_client = httpx.AsyncClient()
api = Api(httpx_client, backend_url_prefix)

storage = StatePickleStorage(file_path="cache/.state_save/states.pkl")
bot = AsyncTeleBot(
    token,
    state_storage=storage,
)

bot.add_custom_filter(StateFilter(bot))

register_menu_handlers(bot, api)
register_get_state_handlers(bot, api)
register_add_database_handlers(bot, api, storage)
register_delete_database_handlers(bot, api, storage)
register_add_database_from_file_handlers(bot, api)


async def perform_healthcheck(tgbot: AsyncTeleBot, api_service: Api):
    users: List[User] = await api_service.get_users()
    for user in users:
        db_objects: List[Database] = await api_service.get_db(
            user_id=user.user_id
        )
        for db in db_objects:
            r = await api_service.healthcheck(db.source_id)
            output = "\n".join(list(map(lambda x: x.message, r)))
            if output:
                await tgbot.send_message(
                    user.chat_id,
                    output,
                )

    logger.info("Performing scheduled healthcheck!")


scheduler = AsyncIOScheduler()
scheduler.add_job(perform_healthcheck, "interval", seconds=10, args=(bot, api))


if __name__ == "__main__":
    import asyncio

    configure_logging()
    logger.info("Starting healthcheck scheduler")
    loop = asyncio.get_event_loop()
    scheduler.start()
    logger.info("Starting bot polling")
    loop.run_until_complete(bot.polling(non_stop=True))
