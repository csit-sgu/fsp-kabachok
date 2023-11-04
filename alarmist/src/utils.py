from enum import Enum


class Message(Enum):
    ACTIVE_PEERS = "active_peers"
    CPU_USAGE = "cpu_usage"
    FREE_SPACE = "free_space"
    NOT_CONNECTED = "not_connected"


MESSAGES = {
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
