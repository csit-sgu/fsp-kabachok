from enum import Enum

from messages import get_text


class Button(Enum):
    GET_STATE = "get_state"
    ADD_DATABASE = "add_database"
    DELETE_DATABASE = "delete_database"
    CHANGE_DATABASE = "change_database"

    def get_formatted(self, lang):
        return get_text(lang, self.value)
