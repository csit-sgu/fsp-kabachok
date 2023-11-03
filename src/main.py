import os

from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StatePickleStorage

import view.markups as markup
from states import BotState
from view.messages import Message, get_text

load_dotenv()

token = os.getenv("BOT_TOKEN")


bot = AsyncTeleBot(
    token,
    state_storage=StatePickleStorage(file_path="cache/.state_save/states.pkl"),
)


@bot.message_handler(commands=["start"])
async def process_start_message(message):
    chat_id = message.chat.id
    await bot.set_state(message.from_user.id, BotState.start, chat_id)
    await bot.send_message(
        chat_id,
        get_text("ru", Message.START_MESSAGE),
        reply_markup=markup.start_markup(),
    )


@bot.message_handler()
async def process_message(message):
    await bot.send_message(message.chat.id, message.text)


if __name__ == "__main__":
    import asyncio

    asyncio.run(bot.polling(non_stop=True))
