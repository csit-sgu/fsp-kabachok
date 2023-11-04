from enum import Enum

from tgbot.src.view.messages import Message


class Button(Enum):
    GET_STATE = Message.GET_STATE_BUTTON
    ADD_DATABASE = Message.ADD_DATABASE
    DELETE_DATABASE = Message.DELETE_DATABASE
    CHANGE_DATABASE = Message.CHANGE_DATABASE
    MANAGE = Message.MANAGE
    ADD_DATABASES_FROM_FILE = Message.ADD_DATABASES_FROM_FILE
