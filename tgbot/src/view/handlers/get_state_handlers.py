from api import Api
from models import SourceModel
from telebot.async_telebot import AsyncTeleBot
from view.states import BotState
from view.texts import Texts, get_text

from shared.models import Metric


def register_get_state_handlers(bot: AsyncTeleBot, api: Api):
    @bot.message_handler(
        state=BotState.Start,
        func=lambda message: message.text
        == get_text("ru", Texts.GET_STATE_BUTTON),
    )
    async def process_get_state(message):
        chat_id = message.chat.id

        await bot.set_state(message.from_user.id, BotState.Start, chat_id)
        await bot.send_message(chat_id, get_text("ru", Texts.GET_STATE))
        databases = [
            SourceModel(id=db.source_id, name=db.display_name)
            for db in await api.get_db(user_id=message.from_user.id)
        ]

        if not databases:
            await bot.send_message(chat_id, get_text("ru", Texts.NO_DBS))
            return

        entries = []
        for db in databases:
            metrics: list[Metric] = await api.get_states(source_id=db.id)
            entry: str = "\n".join(
                list(map(lambda y: f"*{y.type.value}*: {y.value}", metrics))
            )

            entries.append(
                get_text("ru", Texts.METRICS_ANALYSIS_RESULT)
                + f"{db.name}\n{entry}"
            )

        await bot.send_message(
            message.chat.id, "\n".join(entries), parse_mode="markdown"
        )
