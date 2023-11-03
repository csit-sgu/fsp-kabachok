from telebot.asyncio_handler_backends import State, StatesGroup


class BotState(StatesGroup):
    start = State()
