from telebot import types
from view.messages import get_text
from view.utils import Button


def start_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add(types.KeyboardButton(get_text("ru", Button.GET_STATE.value)))
    markup.add(types.KeyboardButton(get_text("ru", Button.MANAGE.value)))
    return markup


def manage_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add(types.KeyboardButton(get_text("ru", Button.ADD_DATABASE.value)))
    markup.add(
        types.KeyboardButton(get_text("ru", Button.DELETE_DATABASE.value))
    )
    markup.add(
        types.KeyboardButton(get_text("ru", Button.CHANGE_DATABASE.value))
    )

    return markup
