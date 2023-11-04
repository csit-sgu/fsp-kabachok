from pydantic import BaseModel


class SourceModel(BaseModel):
    id: str
    name: str


class DatabaseFromFile(BaseModel):
    display_name: str
    db_url: str
