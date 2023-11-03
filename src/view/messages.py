from enum import Enum


class Message(Enum):
    START_MESSAGE = "start_message"
    ADD_DATABASE = "add_database"
    DELETE_DATABASE = "delete_database"
    CHANGE_DATABASE = "change_database"
    MANAGE = "manage"
    GET_STATE = "get_state"
    GET_STATE_BUTTON = "get_state_button"


MESSAGES = {
    Message.START_MESSAGE: {
        "ru": "Привет от Кабачка!",
        "en": "Hello from Kabachok!",
    },
    Message.ADD_DATABASE: {"ru": "Добавить БД"},
    Message.CHANGE_DATABASE: {"ru": "Изменить БД"},
    Message.DELETE_DATABASE: {"ru": "Удалить БД"},
    Message.GET_STATE: {"ru": "Вот состояние на текущий момент"},
    Message.GET_STATE_BUTTON: {"ru": "Узнать текущее состояние"},
    Message.MANAGE: {"ru": "Управление"},
}


def get_text(lang, attr):
    return MESSAGES[attr][lang]
