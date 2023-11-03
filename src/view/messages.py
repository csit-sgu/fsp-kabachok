from enum import Enum


class Message(Enum):
    START_MESSAGE = "start_message"


MESSAGES = {
    Message.START_MESSAGE: {
        "ru": "Привет от Кабачка!",
        "en": "Hello from Kabachok!",
    }
}


def get_text(lang, attr):
    return MESSAGES[attr][lang]
