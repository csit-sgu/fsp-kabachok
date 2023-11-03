from pydantic import BaseModel


class SubmitDatabaseRequest(BaseModel):
    user_id: int
    display_name: str
    conn_string: str


class PatchDatabaseRequest(BaseModel):
    conn_string: str
    display_name: str
    inactive: bool
