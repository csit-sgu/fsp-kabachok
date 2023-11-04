from pydantic import TypeAdapter
from telebot.async_telebot import AsyncTeleBot
from telebot.types import ReplyKeyboardRemove

from tgbot.src.api.api import Api
from tgbot.src.models import DatabaseFromFile
from tgbot.src.view import markups
from tgbot.src.view.states import BotState
from tgbot.src.view.texts import Texts, get_text


def register_add_database_from_file_handlers(bot: AsyncTeleBot, api: Api):
    @bot.message_handler(
        func=lambda message: message.text
        == get_text("ru", Texts.ADD_DATABASES_FROM_FILE)
    )
    async def process_add_database_from_file(message):
        await bot.set_state(
            message.from_user.id, BotState.UploadingDBFile, message.chat.id
        )

        await bot.send_message(
            message.chat.id,
            get_text("ru", Texts.UPLOAD_DB_FILE),
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="MarkdownV2",
        )

    @bot.message_handler(
        content_types=["document"], state=BotState.UploadingDBFile
    )
    async def process_uploading_db_file(message):
        file_info = await bot.get_file(message.document.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)

        validator = TypeAdapter(list[DatabaseFromFile])

        for db in validator.validate_json(downloaded_file):
            await api.submit_db(
                user_id=message.from_user.id,
                display_name=db.display_name,
                db_url=db.db_url,
            )

        await bot.set_state(
            message.from_user.id, BotState.Start, message.chat.id
        )

        await bot.send_message(
            message.chat.id,
            get_text("ru", Texts.DATABASES_UPLOADED),
            reply_markup=markups.start_markup(),
        )
