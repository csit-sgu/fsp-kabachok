import logging
import os
from typing import List

import httpx
import view.markups as markup
from api.api import Api
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from pydantic import TypeAdapter
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import StateFilter
from telebot.asyncio_storage import StatePickleStorage
from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
)
from view.messages import Message, get_text

from shared.entities import User
from shared.logging import configure_logging
from shared.models import Database, Metric
from tgbot.src.models import DatabaseFromFile, SourceModel
from tgbot.src.view.states import BotState

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


async def perform_healthcheck(bot: AsyncTeleBot, api: Api):
    users: List[User] = await api.get_users()
    for user in users:
        db_objects: List[Database] = await api.get_db(user_id=user.user_id)
        for db in db_objects:
            r = await api.healthcheck(db.source_id)
            output = "\n".join(list(map(lambda x: x.message, r)))
            if output:
                await bot.send_message(
                    user.chat_id,
                    output,
                )

    logger.info("Performing scheduled healthcheck!")


scheduler = AsyncIOScheduler()
scheduler.add_job(perform_healthcheck, "interval", seconds=10, args=(bot, api))


@bot.message_handler(commands=["start"])
async def process_start(message):
    chat_id = message.chat.id
    await bot.set_state(message.from_user.id, BotState.Start, chat_id)
    await api.register_user(user_id=message.from_user.id, chat_id=chat_id)
    await bot.send_message(
        chat_id,
        get_text("ru", Message.START_MESSAGE),
        reply_markup=markup.start_markup(),
    )


@bot.message_handler(
    state=BotState.Start,
    func=lambda message: message.text
    == get_text("ru", Message.GET_STATE_BUTTON),
)
async def process_get_state(message):
    chat_id = message.chat.id

    await bot.set_state(message.from_user.id, BotState.Start, chat_id)
    await bot.send_message(chat_id, get_text("ru", Message.GET_STATE))
    databases = [
        SourceModel(id=db.source_id, name=db.display_name)
        for db in await api.get_db(user_id=message.from_user.id)
    ]

    if not databases:
        await bot.send_message(chat_id, get_text("ru", Message.NO_DBS))
        return

    entries = []
    for db in databases:
        metrics: List[Metric] = await api.get_states(source_id=db.id)
        entry: str = "\n".join(
            list(map(lambda y: f"*{y.type.value}*: {y.value}", metrics))
        )

        entries.append(
            get_text("ru", Message.METRICS_ANALYSIS_RESULT)
            + f"{db.name}\n{entry}"
        )

    await bot.send_message(
        message.chat.id, "\n".join(entries), parse_mode="markdown"
    )


@bot.message_handler(
    state=BotState.Start,
    func=lambda message: message.text == get_text("ru", Message.MANAGE),
)
async def process_manage(message):
    chat_id = message.chat.id

    await bot.set_state(message.from_user.id, BotState.Manage, chat_id)
    await bot.send_message(
        chat_id,
        get_text("ru", Message.MANAGE),
        reply_markup=markup.manage_markup(),
    )


@bot.message_handler(
    func=lambda message: message.text == get_text("ru", Message.ADD_DATABASE)
)
async def process_add_database(message):
    await bot.set_state(
        message.from_user.id, BotState.EnteringDBName, message.chat.id
    )
    await bot.send_message(
        message.chat.id,
        get_text("ru", Message.ENTER_DB_DISPLAY_NAME),
        reply_markup=ReplyKeyboardRemove(),
    )


@bot.message_handler(state=BotState.EnteringDBName)
async def process_db_name(message):
    await bot.add_data(
        message.from_user.id, message.chat.id, db_name=message.text
    )
    await bot.set_state(
        message.from_user.id, BotState.EnteringDBURL, message.chat.id
    )
    await bot.send_message(
        message.chat.id, get_text("ru", Message.ENTER_DB_URL)
    )


@bot.message_handler(state=BotState.EnteringDBURL)
async def process_db_url(message):
    data = await storage.get_data(message.from_user.id, message.chat.id)

    db_name = data["db_name"]
    db_url = message.text

    await api.submit_db(
        user_id=message.from_user.id, display_name=db_name, db_url=db_url
    )

    await bot.set_state(message.from_user.id, BotState.Start, message.chat.id)
    await bot.send_message(
        message.chat.id,
        get_text("ru", Message.DB_ADDED),
        reply_markup=markup.start_markup(),
    )


@bot.message_handler(
    state=BotState.Manage,
    func=lambda message: message.text
    == get_text("ru", Message.DELETE_DATABASE),
)
async def process_delete_db(message):
    await bot.set_state(
        message.from_user.id, BotState.SelectingDBForDelete, message.chat.id
    )

    databases = [
        SourceModel(id=db.source_id, name=db.display_name)
        for db in await api.get_db(user_id=message.from_user.id)
    ]

    if not databases:
        await bot.set_state(
            message.from_user.id, BotState.Start, message.chat.id
        )
        await bot.send_message(
            message.chat.id,
            get_text("ru", Message.NO_DBS),
            reply_markup=markup.start_markup(),
        )
        return

    databases_in_fsm_data = {
        i: db.model_dump() for i, db in enumerate(databases, start=1)
    }
    await bot.add_data(
        message.from_user.id, message.chat.id, databases=databases_in_fsm_data
    )

    message_text_parts = [
        f"/db{i} {db.name}" for i, db in enumerate(databases, start=1)
    ]
    message_text = (
        get_text("ru", Message.SELECT_DB)
        + "\n"
        + "\n".join(message_text_parts)
    )

    await bot.send_message(
        message.chat.id, message_text, reply_markup=ReplyKeyboardRemove()
    )


@bot.message_handler(
    state=BotState.SelectingDBForDelete,
    func=lambda message: message.text.startswith("/db")
    and message.text[3:].isnumeric(),
)
async def process_selecting_db_for_delete(message):
    db_number = int(message.text[3:])

    data = await storage.get_data(message.from_user.id, message.chat.id)
    db = TypeAdapter(SourceModel).validate_python(data["databases"][db_number])

    kb = InlineKeyboardMarkup()
    kb.row_width = 2
    kb.add(
        InlineKeyboardButton(
            get_text("ru", Message.YES),
            callback_data=f"deldb_{db_number}_{db.id}",
        ),
        InlineKeyboardButton(
            get_text("ru", Message.NO), callback_data="cancel_deldb"
        ),
    )

    await bot.send_message(
        message.chat.id,
        get_text("ru", Message.CONFIRM_DB_DELETING).replace(
            "%", f'"{db.name}"'
        ),
        reply_markup=kb,
    )


@bot.callback_query_handler(
    state=BotState.SelectingDBForDelete,
    func=lambda cb: cb.data.startswith("deldb_"),
)
async def process_delete_db(cb):
    data = await storage.get_data(cb.message.chat.id, cb.message.chat.id)
    db_number, db_id = cb.data[6:].split("_")
    db_number = int(db_number)

    db = TypeAdapter(SourceModel).validate_python(data["databases"][db_number])

    await api.remove_db(db.id)
    await bot.answer_callback_query(cb.id)
    await bot.delete_message(cb.message.chat.id, cb.message.message_id)
    await bot.send_message(
        cb.message.chat.id,
        get_text("ru", Message.DB_DELETED).replace("%", f'"{db.name}"'),
        reply_markup=markup.start_markup(),
    )

    await bot.set_state(cb.message.chat.id, BotState.Start, cb.message.chat.id)


@bot.callback_query_handler(
    state=BotState.SelectingDBForDelete,
    func=lambda cb: cb.data.startswith("cancel_deldb"),
)
async def process_cancel_delete_db(cb):
    await bot.answer_callback_query(cb.id)
    await bot.delete_message(cb.message.chat.id, cb.message.message_id)
    await bot.send_message(
        cb.message.chat.id,
        get_text("ru", Message.DB_DELETING_CANCELED),
        reply_markup=markup.start_markup(),
    )

    await bot.set_state(cb.message.chat.id, BotState.Start, cb.message.chat.id)


@bot.message_handler(
    func=lambda message: message.text
    == get_text("ru", Message.ADD_DATABASES_FROM_FILE)
)
async def process_add_database_from_file(message):
    await bot.set_state(
        message.from_user.id, BotState.UploadingDBFile, message.chat.id
    )

    await bot.send_message(
        message.chat.id,
        get_text("ru", Message.UPLOAD_DB_FILE),
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="MarkdownV2",
    )


@bot.message_handler(
    content_types=["document"], state=BotState.UploadingDBFile
)
async def process_uploading_db_file(message):
    # NOTE(nrydanov): Why is this variable is unused?
    file_name = message.document.file_name
    file_info = await bot.get_file(message.document.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)

    validator = TypeAdapter(list[DatabaseFromFile])

    for db in validator.validate_json(downloaded_file):
        await api.submit_db(
            user_id=message.from_user.id,
            display_name=db.display_name,
            db_url=db.db_url,
        )

    await bot.set_state(message.from_user.id, BotState.Start, message.chat.id)

    await bot.send_message(
        message.chat.id,
        get_text("ru", Message.DATABASES_UPLOADED),
        reply_markup=ReplyKeyboardRemove(),
    )


if __name__ == "__main__":
    import asyncio

    configure_logging()
    logger.info("Starting healthcheck scheduler")
    loop = asyncio.get_event_loop()
    scheduler.start()
    logger.info("Starting bot polling")
    loop.run_until_complete(bot.polling(non_stop=True))
