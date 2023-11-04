from api import Api
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateStorageBase
from telebot.types import ReplyKeyboardRemove
from view import markups
from view.states import BotState
from view.texts import Texts, get_text


def register_add_database_handlers(
    bot: AsyncTeleBot, api: Api, storage: StateStorageBase
):
    @bot.message_handler(
        func=lambda message: message.text == get_text("ru", Texts.ADD_DATABASE)
    )
    async def process_add_database(message):
        await bot.set_state(
            message.from_user.id, BotState.EnteringDBName, message.chat.id
        )
        await bot.send_message(
            message.chat.id,
            get_text("ru", Texts.ENTER_DB_DISPLAY_NAME),
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
            message.chat.id, get_text("ru", Texts.ENTER_DB_URL)
        )

    @bot.message_handler(state=BotState.EnteringDBURL)
    async def process_db_url(message):
        data = await storage.get_data(message.from_user.id, message.chat.id)

        db_name = data["db_name"]
        db_url = message.text

        await api.submit_db(
            user_id=message.from_user.id, display_name=db_name, db_url=db_url
        )

        await bot.set_state(
            message.from_user.id, BotState.Start, message.chat.id
        )
        await bot.send_message(
            message.chat.id,
            get_text("ru", Texts.DB_ADDED),
            reply_markup=markups.start_markup(),
        )
