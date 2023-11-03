import os

from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import StateFilter
from telebot.asyncio_storage import StatePickleStorage

import view.markups as markup
from states import BotState
from view.messages import Message, get_text
from view.utils import Button

load_dotenv()

token = os.getenv("BOT_TOKEN")


bot = AsyncTeleBot(
    token,
    state_storage=StatePickleStorage(file_path="cache/.state_save/states.pkl"),
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

    if text == get_text("ru", Button.MANAGE.value):
        await bot.set_state(message.from_user.id, BotState.Manage, chat_id)
    elif text == get_text("ru", Button.GET_STATE.value):
        await bot.set_state(message.from_user.id, BotState.GetState, chat_id)


@bot.message_handler(state=BotState.GetState)
async def retrieve_state(message):
    chat_id = message.chat.id
    await bot.set_state(message.from_user.id, BotState.Start, chat_id)
    await bot.send_message(chat_id, get_text("ru", Message.GET_STATE))
    # TODO(nrydanov): Realize based on function from Postgres API
    pass


@bot.message_handler(state=BotState.Manage)
async def manage(message):
    chat_id = message.chat.id
    await bot.set_state(message.from_user.id, BotState.Manage, chat_id)
    await bot.send_message(
        chat_id,
        get_text("ru", Message.MANAGE),
        reply_markup=markup.manage_markup(),
    )


if __name__ == "__main__":
    import asyncio

    asyncio.run(bot.polling(non_stop=True))
