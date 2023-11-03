from enum import Enum


class Message(Enum):
    START_MESSAGE = "start_message"
    ADD_DATABASE = "add_database"
    DELETE_DATABASE = "delete_database"
    CHANGE_DATABASE = "change_database"


MESSAGES = {
    Message.START_MESSAGE: {
        "ru": "Привет от Кабачка!",
        "en": "Hello from Kabachok!",
    },
    Message.ADD_DATABASE: {"ru": "Добавить БД"},
    Message.CHANGE_DATABASE: {"ru": "Изменить БД"},
    Message.DELETE_DATABASE: {"ru": "Удалить БД"},
}


def get_text(lang, attr):
    return MESSAGES[attr][lang]
