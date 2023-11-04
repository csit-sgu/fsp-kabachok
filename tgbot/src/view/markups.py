from telebot import types

from tgbot.src.view.messages import Message, get_text


def start_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add(types.KeyboardButton(get_text("ru", Message.GET_STATE_BUTTON)))
    markup.add(types.KeyboardButton(get_text("ru", Message.MANAGE)))
    return markup


def manage_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add(types.KeyboardButton(get_text("ru", Message.ADD_DATABASE)))
    markup.add(
        types.KeyboardButton(get_text("ru", Message.ADD_DATABASES_FROM_FILE))
    )
    markup.add(types.KeyboardButton(get_text("ru", Message.DELETE_DATABASE)))
    markup.add(types.KeyboardButton(get_text("ru", Message.CHANGE_DATABASE)))

    return markup
