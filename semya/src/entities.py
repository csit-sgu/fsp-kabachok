from uuid import UUID

from pydantic import BaseModel


class Source(BaseModel):
    source_id: UUID
    conn_string: str

    _table_name = "source"
