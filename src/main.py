import telebot
from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(token)


@bot.message_handler(commands=["start"])
def process_start_message(message):
    bot.send_message(message.chat.id, "Hello, Kabachok!")


@bot.message_handler()
def process_message(message):
    bot.send_message(message.chat.id, message.text)


if __name__ == "__main__":
    bot.infinity_polling()
