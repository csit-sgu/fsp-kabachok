from enum import Enum


class Message(Enum):
    OK = "ok"
    ACTIVE_PEERS = "active_peers"
    CPU_USAGE = "cpu_usage"
    FREE_SPACE = "free_space"
    NOT_CONNECTED = "not_connected"


MESSAGES = {
    Message.OK: {
        "ru": "ОК",
        "en": "OK",
    },
    Message.CPU_USAGE: {
        "ru": "Слишком большая нагрузка на CPU",
        "en": "Extensive CPU load",
    },
    Message.FREE_SPACE: {
        "ru": "Слишком мало свободного места на диске",
        "en": "Disk is almost full",
    },
    Message.NOT_CONNECTED: {
        "ru": "Не удалось подключиться к базе данных",
        "en": "Could not establish database connection",
    },
}


def get_text(lang, attr):
    return MESSAGES[attr][lang]
