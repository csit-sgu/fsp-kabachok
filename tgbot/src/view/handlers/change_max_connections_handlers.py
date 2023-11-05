import logging

from api import Api
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateStorageBase
from view.markups import start_markup
from view.states import BotState

logger = logging.getLogger("app")


def register_change_max_connections_handlers(
    bot: AsyncTeleBot, api: Api, storage: StateStorageBase
):
    @bot.callback_query_handler(
        func=lambda cb: cb.data.startswith("chngmaxconn_")
    )
    async def process_change_max_connections(cb: types.CallbackQuery):
        source_id = cb.data[12:]
        await bot.add_data(
            cb.message.chat.id, cb.message.chat.id, source_id=source_id
        )
        await bot.set_state(
            cb.message.chat.id,
            BotState.EnteringNewMaxConnectionsCount,
            cb.message.chat.id,
        )

        # TODO: Unharcode texts
        await bot.answer_callback_query(cb.id)
        await bot.send_message(
            cb.message.chat.id,
            "Введите новое кол-во максимальных соединений",
            reply_markup=types.ReplyKeyboardRemove(),
        )

    @bot.message_handler(state=BotState.EnteringNewMaxConnectionsCount)
    async def process_new_max_connections_count(message: types.Message):
        data = await storage.get_data(message.from_user.id, message.chat.id)

        source_id = data["source_id"]
        max_connections = int(message.text)

        # TODO: Implement
        logger.info("aboba" * 100)
        logger.info(source_id, max_connections)

        await bot.set_state(
            message.chat.id,
            BotState.EnteringNewMaxConnectionsCount,
            message.chat.id,
        )
        await bot.send_message(
            message.chat.id,
            "Новое кол-во максимальных соеденинений установлено",
            reply_markup=start_markup(),
        )
