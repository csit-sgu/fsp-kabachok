import logging
import os
from typing import List

import httpx
from api import Api
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import StateFilter
from telebot.asyncio_storage import StatePickleStorage
from view.handlers.add_database_from_file_handlers import (
    register_add_database_from_file_handlers,
)
from view.handlers.add_database_handlers import register_add_database_handlers
from view.handlers.delete_database_handlers import (
    register_delete_database_handlers,
)
from view.handlers.get_state_handlers import register_get_state_handlers
from view.handlers.menu_handlers import register_menu_handlers

from shared.entities import User
from shared.logging import configure_logging
from shared.models import Database
from shared.resources import SharedResources
from shared.utils import SHARED_CONFIG_PATH

logger = logging.getLogger("app")


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


class Context:
    def init_bot(self):
        storage = StatePickleStorage(file_path="cache/.state_save/states.pkl")
        self.bot = AsyncTeleBot(
            self.token,
            state_storage=storage,
        )
        register_menu_handlers(self.bot, self.api)
        register_get_state_handlers(self.bot, self.api)
        register_add_database_handlers(self.bot, self.api, storage)
        register_delete_database_handlers(self.bot, self.api, storage)
        register_add_database_from_file_handlers(self.bot, self.api)
        self.bot.add_custom_filter(StateFilter(self.bot))

    def init_scheduler(self):
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(
            perform_healthcheck,
            "interval",
            seconds=self.shared_settings.watchdog.interval,
            args=(self.bot, self.api),
        )

    def __init__(self):
        load_dotenv()

        self.backend_url_prefix = os.getenv("BACKEND_URL")

        self.token = os.getenv("BOT_TOKEN")
        httpx_client = httpx.AsyncClient()
        self.api = Api(httpx_client, self.backend_url_prefix)
        self.shared_settings = SharedResources(
            f"{SHARED_CONFIG_PATH}/settings.json"
        )

        self.init_bot()
        self.init_scheduler()


ctx = Context()


if __name__ == "__main__":
    import asyncio

    configure_logging()
    logger.info("Starting healthcheck scheduler")
    loop = asyncio.get_event_loop()
    if not ctx.shared_settings.watchdog.disable_healthcheck:
        ctx.scheduler.start()
    logger.info("Starting bot polling")
    loop.run_until_complete(ctx.bot.polling(non_stop=True))
