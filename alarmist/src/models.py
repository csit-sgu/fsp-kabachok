from pydantic import BaseModel
from utils import MESSAGES, Message


class SubmitDatabaseRequest(BaseModel):
    user_id: int
    display_name: str
    conn_string: str


class PatchDatabaseRequest(BaseModel):
    conn_string: str
    display_name: str
    inactive: bool


class Alert:
    def __init__(self, type: Message, locale: str):
        self.type = type
        self.message = MESSAGES[type][locale]
