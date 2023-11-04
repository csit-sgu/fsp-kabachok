from telebot import types

from tgbot.src.view.texts import Texts, get_text


def start_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add(types.KeyboardButton(get_text("ru", Texts.GET_STATE_BUTTON)))
    markup.add(types.KeyboardButton(get_text("ru", Texts.MANAGE)))
    return markup


def manage_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add(types.KeyboardButton(get_text("ru", Texts.ADD_DATABASE)))
    markup.add(
        types.KeyboardButton(get_text("ru", Texts.ADD_DATABASES_FROM_FILE))
    )
    markup.add(types.KeyboardButton(get_text("ru", Texts.DELETE_DATABASE)))
    markup.add(types.KeyboardButton(get_text("ru", Texts.CHANGE_DATABASE)))

    return markup
