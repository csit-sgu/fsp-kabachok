import logging

from api import Api
from graph import create_graph
from models import SourceModel
from pydantic import TypeAdapter
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateStorageBase
from view.states import BotState
from view.texts import Texts, get_text
from view.utils import get_selecting_db_text

from shared.models import Metric, MetricType

logger = logging.getLogger("app")


def register_get_state_handlers(
    bot: AsyncTeleBot, api: Api, storage: StateStorageBase
):
    @bot.message_handler(
        state=BotState.Start,
        func=lambda message: message.text
        == get_text("ru", Texts.GET_STATE_BUTTON),
    )
    async def process_get_state(message: types.Message):
        chat_id = message.chat.id

        databases = [
            SourceModel(id=db.source_id, name=db.display_name)
            for db in await api.get_db(user_id=message.from_user.id)
        ]

        if not databases:
            await bot.send_message(chat_id, get_text("ru", Texts.NO_DBS))
            return

        databases_in_fsm_data = {
            i: db.model_dump() for i, db in enumerate(databases, start=1)
        }
        await bot.add_data(
            message.from_user.id,
            chat_id,
            databases=databases_in_fsm_data,
        )

        await bot.send_message(
            chat_id, get_selecting_db_text(databases, prefix="/metrics")
        )

    @bot.message_handler(
        func=lambda message: message.text.startswith("/metrics")
        and message.text[8:].isnumeric()
    )
    async def process_select_db_for_check_metrics(message: types.Message):
        db_number = int(message.text[8:])

        data = await storage.get_data(message.from_user.id, message.chat.id)
        if not (databases := data.get("databases")):
            return

        db = TypeAdapter(SourceModel).validate_python(databases[db_number])

        metrics: list[Metric] = await api.get_states(source_id=db.id)
        text = _get_metrics_text(metrics=metrics, database_name=db.name)

        metric_types_with_graphs = [
            MetricType.CPU_USAGE,
            MetricType.FREE_SPACE,
            MetricType.ACTIVE_PEERS,
        ]
        stats = await api.get_states_plots(source_id=db.id)
        logger.debug(f"{stats=}")
        for stat, values in stats.items():
            if stat in metric_types_with_graphs:
                image = create_graph(stat, values)
                await bot.send_photo(message.chat.id, image)

        await bot.send_message(message.chat.id, text, parse_mode="markdown")


def _get_metrics_text(metrics: list[Metric], database_name: str) -> str:
    lines = [f"_{database_name}_"]
    for metric in metrics:
        match metric.type:
            case MetricType.FREE_SPACE:
                lines.append(f"💿 *{metric.type.value}*: {metric.value:.2f}%")
            case MetricType.CPU_USAGE:
                lines.append(f"💻 *{metric.type.value}*: {metric.value:.2f}%")
            case MetricType.ACTIVE_PEERS:
                lines.append(f"👤 *{metric.type.value}*: {int(metric.value)}")
            case MetricType.LWLOCK_TRANSACTIONS:
                lines.append(f"🔒 *{metric.type.value}*: {int(metric.value)}")
            case MetricType.LONG_TRANSACTION:
                lines.append(f"⌛ *{metric.type.value}*: {int(metric.value)}")

    return "\n".join(lines)
