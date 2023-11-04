from enum import Enum


class Message(Enum):
    START_MESSAGE = "start_message"
    ADD_DATABASE = "add_database"
    ADD_DATABASES_FROM_FILE = "add_database_from_file"
    UPLOAD_DB_FILE = "upload_db_file"
    DATABASES_UPLOADED = "databases_uploaded"
    DELETE_DATABASE = "delete_database"
    CHANGE_DATABASE = "change_database"
    MANAGE = "manage"
    GET_STATE = "get_state"
    GET_STATE_BUTTON = "get_state_button"
    ENTER_DB_DISPLAY_NAME = "enter_db_display_name"
    ENTER_DB_URL = "enter_db_url"
    DB_ADDED = "db_added"
    SELECT_DB = "select_db"
    CONFIRM_DB_DELETING = "confirm_db_deleting"
    DB_DELETED = "db_deleted"
    DB_DELETING_CANCELED = "db_deleting_canceled"
    METRICS_ANALYSIS_RESULT = "metrics_analysis_result"
    NO_DBS = "no_dbs"
    YES = "yes"
    NO = "no"


MESSAGES = {
    Message.START_MESSAGE: {
        "ru": "Привет от Кабачка!",
        "en": "Hello from Kabachok!",
    },
    Message.ADD_DATABASE: {"ru": "Добавить БД"},
    Message.ADD_DATABASES_FROM_FILE: {"ru": "Добавить БД из файла"},
    Message.UPLOAD_DB_FILE: {
        "ru": """Загрузите файл в следующем формате

```JSON
[
    {
        "display_name": "Название базы данных",
        "db_url": "Строка подлключения к БД"
    },
    {
        "display_name": "Название базы данных",
        "db_url": "Строка подлключения к БД"
    },
    ...
]
```
"""
    },
    Message.DATABASES_UPLOADED: {"ru": "Базы данных загружены"},
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
    Message.SELECT_DB: {"ru": "Выберите базу данных"},
    Message.CONFIRM_DB_DELETING: {
        "ru": "Вы точно хотите удалить базу данных с названием %?"
    },
    Message.DB_DELETED: {"ru": "База с названием % удалена"},
    Message.DB_DELETING_CANCELED: {"ru": "Удаление отменено"},
    Message.METRICS_ANALYSIS_RESULT: {"ru": "Результат анализа метрик для "},
    Message.NO_DBS: {"ru": "Ни одной базы данных"},
    Message.YES: {"ru": "Да"},
    Message.NO: {"ru": "Нет"},
}


def get_text(lang, attr):
    return MESSAGES[attr][lang]
