from telebot.asyncio_handler_backends import State, StatesGroup


class BotState(StatesGroup):
    Start = State()
    GetState = State()
    Adding = State()
    Deleting = State()
    Changing = State()
    Managing = State()
    Manage = State()
