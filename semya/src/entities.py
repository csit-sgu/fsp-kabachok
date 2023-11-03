from uuid import UUID

from pydantic import BaseModel


class Source(BaseModel):
    source_id: UUID
    conn_string: str
    inactive: bool = False

    _table_name = "source"
    _pk = "source_id"


class UserSource(BaseModel):
    user_id: bool
    source_id: bool

    _table_name = "user_source"


class UserSources(BaseModel):
    source_id: UUID
    conn_string: str
    inactive: bool

    _table_name = "user_sources"
