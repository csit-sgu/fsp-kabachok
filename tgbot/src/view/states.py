from telebot.asyncio_handler_backends import State, StatesGroup


class BotState(StatesGroup):
    Start = State()
    Adding = State()
    Deleting = State()
    Changing = State()
    Managing = State()
    Manage = State()
    EnteringDBName = State()
    EnteringDBURL = State()
    SelectingDBForDelete = State()
    SelectingDBForCheckMetrics = State()
    UploadingDBFile = State()
    EnteringNewMaxConnectionsCount = State()
