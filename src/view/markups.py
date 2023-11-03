from telebot import types


def start_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    return markup
