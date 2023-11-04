from enum import Enum


class Texts(Enum):
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
    Texts.START_MESSAGE: {
        "ru": "Привет от Кабачка!",
        "en": "Hello from Kabachok!",
    },
    Texts.ADD_DATABASE: {"ru": "Добавить БД"},
    Texts.ADD_DATABASES_FROM_FILE: {"ru": "Добавить БД из файла"},
    Texts.UPLOAD_DB_FILE: {
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
    Texts.DATABASES_UPLOADED: {"ru": "Базы данных загружены"},
    Texts.CHANGE_DATABASE: {"ru": "Изменить БД"},
    Texts.DELETE_DATABASE: {"ru": "Удалить БД"},
    Texts.GET_STATE: {"ru": "Вот состояние на текущий момент"},
    Texts.GET_STATE_BUTTON: {"ru": "Узнать текущее состояние"},
    Texts.MANAGE: {"ru": "Управление"},
    Texts.ENTER_DB_DISPLAY_NAME: {
        "ru": "Введите название вашей базы данных, которое будет отображаться в боте"
    },
    Texts.ENTER_DB_URL: {"ru": "Введите строку подсоединения к базе данных"},
    Texts.DB_ADDED: {"ru": "База данных добавлена"},
    Texts.SELECT_DB: {"ru": "Выберите базу данных"},
    Texts.CONFIRM_DB_DELETING: {
        "ru": "Вы точно хотите удалить базу данных с названием %?"
    },
    Texts.DB_DELETED: {"ru": "База с названием % удалена"},
    Texts.DB_DELETING_CANCELED: {"ru": "Удаление отменено"},
    Texts.METRICS_ANALYSIS_RESULT: {"ru": "Результат анализа метрик для "},
    Texts.NO_DBS: {"ru": "У вас нет ни одной базы данных"},
    Texts.YES: {"ru": "Да"},
    Texts.NO: {"ru": "Нет"},
}


def get_text(lang, attr):
    return MESSAGES[attr][lang]
