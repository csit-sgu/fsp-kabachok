import json

import seaborn
from api import Api
from models import SourceModel
from telebot.async_telebot import AsyncTeleBot
from view.states import BotState
from view.texts import Texts, get_text

from shared.models import Metric, MetricType


# TODO(granatam): Implement this
def register_get_state_plots_handlers(bot: AsyncTeleBot, api: Api):
    @bot.message_handler(
        state=BotState.Start,
        func=lambda message: message.text
        == get_text("ru", Texts.GET_STATE_PLOTS_BUTTON),
    )
    async def process_get_state_plots(message):
        chat_id = message.chat.id

        await bot.set_state(message.from_user.id, BotState.Start, chat_id)
        databases = [
            SourceModel(id=db.source_id, name=db.display_name)
            for db in await api.get_db(user_id=message.from_user.id)
        ]

        if not databases:
            await bot.send_message(chat_id, get_text("ru", Texts.NO_DBS))
            return
