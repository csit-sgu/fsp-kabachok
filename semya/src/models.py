from pydantic import BaseModel


class SubmitDatabaseRequest(BaseModel):
    user_id: int
    conn_string: str
