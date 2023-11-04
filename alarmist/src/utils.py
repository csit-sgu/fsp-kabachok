from enum import Enum


class Message(Enum):
    TOO_MANY_CONNECTIONS = "too_many_connections"
    ACTIVE_PEERS = "active_peers"
    CPU = "cpu_usage"
    FREE_SPACE = "free_space"
    UNAVAILABLE = "unavailable"
    LWLOCK_COUNT = "lwlock_count"
    TIMEOUT = "timeout"


MESSAGES = {
    Message.TOO_MANY_CONNECTIONS: {
        "ru": "Достигнуто максимальное количество подключений",
        "en": "Too many connections",
    },
    Message.CPU: {
        "ru": "Слишком большая нагрузка на CPU",
        "en": "Extensive CPU load",
    },
    Message.FREE_SPACE: {
        "ru": "Слишком мало свободного места на диске",
        "en": "Disk is almost full",
    },
    Message.UNAVAILABLE: {
        "ru": "Не удалось подключиться к базе данных",
        "en": "Could not establish database connection",
    },
    Message.ACTIVE_PEERS: {
        "ru": "Слишком много активных подключений",
        "en": "Too many connections",
    },
    Message.LWLOCK_COUNT: {
        "ru": "Слишком много блокировок",
        "en": "Too many blockings",
    },
    Message.TIMEOUT: {
        "ru": "Слишком долгая операция",
        "en": "Operation timeout",
    },
}


def get_text(lang, attr):
    return MESSAGES[attr][lang]
