from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel


class Source(BaseModel):
    source_id: UUID
    conn_string: str
    inactive: bool = False

    _table_name: ClassVar[str] = "source"
    _pk: ClassVar[str] = "source_id"


class UserSource(BaseModel):
    user_id: int
    source_id: UUID

    _table_name: ClassVar[str] = "user_source"


class UserSources(BaseModel):
    source_id: UUID
    conn_string: str
    inactive: bool

    _table_name: ClassVar[str] = "user_sources"
