from api import Api
from models import SourceModel
from pydantic import TypeAdapter
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateStorageBase
from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
)
from view import markups
from view.states import BotState
from view.texts import Texts, get_text
from view.utils import get_selecting_db_text


def register_delete_database_handlers(
    bot: AsyncTeleBot, api: Api, storage: StateStorageBase
):
    @bot.message_handler(
        state=BotState.Manage,
        func=lambda message: message.text
        == get_text("ru", Texts.DELETE_DATABASE),
    )
    async def process_delete_db(message):
        await bot.set_state(
            message.from_user.id,
            BotState.SelectingDBForDelete,
            message.chat.id,
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
                get_text("ru", Texts.NO_DBS),
                reply_markup=markups.start_markup(),
            )
            return

        databases_in_fsm_data = {
            i: db.model_dump() for i, db in enumerate(databases, start=1)
        }
        await bot.add_data(
            message.from_user.id,
            message.chat.id,
            databases=databases_in_fsm_data,
        )

        await bot.send_message(
            message.chat.id,
            get_selecting_db_text(databases),
            reply_markup=ReplyKeyboardRemove(),
        )

    @bot.message_handler(
        state=BotState.SelectingDBForDelete,
        func=lambda message: message.text.startswith("/db")
        and message.text[3:].isnumeric(),
    )
    async def process_selecting_db_for_delete(message):
        db_number = int(message.text[3:])

        data = await storage.get_data(message.from_user.id, message.chat.id)
        db = TypeAdapter(SourceModel).validate_python(
            data["databases"][db_number]
        )

        kb = InlineKeyboardMarkup()
        kb.row_width = 2
        kb.add(
            InlineKeyboardButton(
                get_text("ru", Texts.YES),
                callback_data=f"deldb_{db_number}_{db.id}",
            ),
            InlineKeyboardButton(
                get_text("ru", Texts.NO), callback_data="cancel_deldb"
            ),
        )

        await bot.send_message(
            message.chat.id,
            get_text("ru", Texts.CONFIRM_DB_DELETING).replace(
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

        db = TypeAdapter(SourceModel).validate_python(
            data["databases"][db_number]
        )

        await api.remove_db(db.id)
        await bot.answer_callback_query(cb.id)
        await bot.delete_message(cb.message.chat.id, cb.message.message_id)
        await bot.send_message(
            cb.message.chat.id,
            get_text("ru", Texts.DB_DELETED).replace("%", f'"{db.name}"'),
            reply_markup=markups.start_markup(),
        )

        await bot.set_state(
            cb.message.chat.id, BotState.Start, cb.message.chat.id
        )

    @bot.callback_query_handler(
        state=BotState.SelectingDBForDelete,
        func=lambda cb: cb.data.startswith("cancel_deldb"),
    )
    async def process_cancel_delete_db(cb):
        await bot.answer_callback_query(cb.id)
        await bot.delete_message(cb.message.chat.id, cb.message.message_id)
        await bot.send_message(
            cb.message.chat.id,
            get_text("ru", Texts.DB_DELETING_CANCELED),
            reply_markup=markups.start_markup(),
        )

        await bot.set_state(
            cb.message.chat.id, BotState.Start, cb.message.chat.id
        )
