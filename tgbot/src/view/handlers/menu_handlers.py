from telebot import types
from telebot.async_telebot import AsyncTeleBot

from tgbot.src.api.api import Api
from tgbot.src.view import markups
from tgbot.src.view.states import BotState
from tgbot.src.view.texts import Texts, get_text


def register_menu_handlers(bot: AsyncTeleBot, api: Api):
    @bot.message_handler(commands=["start"])
    async def process_start(message: types.Message):
        chat_id = message.chat.id
        await bot.set_state(message.from_user.id, BotState.Start, chat_id)
        await api.register_user(user_id=message.from_user.id, chat_id=chat_id)
        await bot.send_message(
            chat_id,
            get_text("ru", Texts.START_MESSAGE),
            reply_markup=markups.start_markup(),
        )

    @bot.message_handler(
        state=BotState.Start,
        func=lambda message: message.text == get_text("ru", Texts.MANAGE),
    )
    async def process_manage(message):
        chat_id = message.chat.id

        await bot.set_state(message.from_user.id, BotState.Manage, chat_id)
        await bot.send_message(
            chat_id,
            get_text("ru", Texts.MANAGE),
            reply_markup=markups.manage_markup(),
        )
