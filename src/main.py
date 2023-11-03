import os

from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import StateFilter
from telebot.asyncio_storage import StatePickleStorage
from telebot.types import ReplyKeyboardRemove

import view.markups as markup
from states import BotState
from view.messages import Message, get_text
from view.utils import Button

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


@bot.message_handler(func=lambda message: message.text == get_text("ru", Button.ADD_DATABASE.value))
async def process_add_database(message):
    await bot.set_state(message.from_user.id, BotState.EnteringDBName, message.chat.id)
    await bot.send_message(
        message.chat.id, 
        get_text("ru", Message.ENTER_DB_DISPLAY_NAME), 
        reply_markup=ReplyKeyboardRemove()
    )


@bot.message_handler(state=BotState.EnteringDBName)
async def process_db_name(message):
    await bot.add_data(message.from_user.id, message.chat.id, db_name=message.text)
    await bot.set_state(message.from_user.id, BotState.EnteringDBURL, message.chat.id)
    await bot.send_message(message.chat.id, get_text("ru", Message.ENTER_DB_URL))


@bot.message_handler(state=BotState.EnteringDBURL)
async def process_db_url(message):
    data = await storage.get_data(message.from_user.id, message.chat.id)

    db_name = data['db_name']
    db_url = message.text

    # TODO: Add db

    await bot.set_state(message.from_user.id, BotState.Start, message.chat.id)
    await bot.send_message(message.chat.id, get_text("ru", Message.DB_ADDED), reply_markup=markup.start_markup())


if __name__ == "__main__":
    import asyncio

    asyncio.run(bot.polling(non_stop=True))
