import os
import uuid

import view.markups as markup
from dotenv import load_dotenv
from states import BotState
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import StateFilter
from telebot.asyncio_storage import StatePickleStorage
from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
)
from view.messages import Message, get_text
from view.utils import Button
from view.viewmodels import DatabaseViewModel

load_dotenv()

token = os.getenv("BOT_TOKEN")

storage = StatePickleStorage(file_path="cache/.state_save/states.pkl")
bot = AsyncTeleBot(
    token,
    state_storage=storage,
)

bot.add_custom_filter(StateFilter(bot))


@bot.message_handler(commands=["start"])
async def process_start(message):
    chat_id = message.chat.id
    await bot.set_state(message.from_user.id, BotState.Start, chat_id)
    await bot.send_message(
        chat_id,
        get_text("ru", Message.START_MESSAGE),
        reply_markup=markup.start_markup(),
    )


@bot.message_handler(state=BotState.Start)
async def process_start_message(message):
    chat_id = message.chat.id
    text = message.text

    if text == get_text("ru", Button.GET_STATE.value):
        chat_id = message.chat.id
        await bot.set_state(message.from_user.id, BotState.Start, chat_id)
        await bot.send_message(chat_id, get_text("ru", Message.GET_STATE))
        # TODO(nrydanov): Realize based on function from Postgres API
    elif text == get_text("ru", Button.MANAGE.value):
        chat_id = message.chat.id
        await bot.set_state(message.from_user.id, BotState.Manage, chat_id)
        await bot.send_message(
            chat_id,
            get_text("ru", Message.MANAGE),
            reply_markup=markup.manage_markup(),
        )


@bot.message_handler(
    func=lambda message: message.text
    == get_text("ru", Button.ADD_DATABASE.value)
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

    # TODO: Add db

    await bot.set_state(message.from_user.id, BotState.Start, message.chat.id)
    await bot.send_message(
        message.chat.id,
        get_text("ru", Message.DB_ADDED),
        reply_markup=markup.start_markup(),
    )


@bot.message_handler(
    state=BotState.Manage,
    func=lambda message: message.text
    == get_text("ru", Button.DELETE_DATABASE.value),
)
async def process_delete_db(message):
    await bot.set_state(
        message.from_user.id, BotState.SelectingDBForDelete, message.chat.id
    )

    # TODO: Get databases

    databases = [
        DatabaseViewModel(
            uuid.uuid4(), f"Базаданных для кондитерских изделий #{i}"
        )
        for i in range(1, 20 + 1)
    ]

    databases_in_fsm_data = {
        i: db.to_dict() for i, db in enumerate(databases, start=1)
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
    db = DatabaseViewModel.from_dict(data["databases"][db_number])

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

    # TODO: Delete db
    db = DatabaseViewModel.from_dict(data["databases"][db_number])

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


if __name__ == "__main__":
    import asyncio

    asyncio.run(bot.polling(non_stop=True))
