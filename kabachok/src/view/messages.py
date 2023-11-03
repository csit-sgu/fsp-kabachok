from enum import Enum


class Message(Enum):
    START_MESSAGE = "start_message"
    ADD_DATABASE = "add_database"
    DELETE_DATABASE = "delete_database"
    CHANGE_DATABASE = "change_database"
    MANAGE = "manage"
    GET_STATE = "get_state"
    GET_STATE_BUTTON = "get_state_button"

    ENTER_DB_DISPLAY_NAME = "enter_db_display_name"
    ENTER_DB_URL = "enter_db_url"
    DB_ADDED = "db_added"


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
    Message.ENTER_DB_DISPLAY_NAME: {
        "ru": "Введите название вашей базы данных, которое будет отображаться в боте"
    },
    Message.ENTER_DB_URL: {"ru": "Введите строку подсоединения к базе данных"},
    Message.DB_ADDED: {"ru": "База данных добавлена"},
}


def get_text(lang, attr):
    return MESSAGES[attr][lang]
