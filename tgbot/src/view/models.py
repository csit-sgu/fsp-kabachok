from uuid import UUID

from pydantic import BaseModel


class SourceModel(BaseModel):
    id: UUID
    name: str


class DatabaseFromFile(BaseModel):
    display_name: str
    db_url: str
