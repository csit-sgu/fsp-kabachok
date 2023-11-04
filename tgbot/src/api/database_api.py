from typing import List
from uuid import UUID

import httpx
from pydantic import BaseModel, TypeAdapter

from shared.models import Metric


class Database(BaseModel):
    source_id: UUID
    display_name: str
    conn_string: str
    inactive: bool


class DatabaseApi:
    def __init__(self, async_client: httpx.AsyncClient, url_prefix: str):
        self._client = async_client
        self._url_prefix = url_prefix

    async def submit_db(self, *, user_id: int, display_name: str, db_url: str):
        data = dict(
            user_id=user_id, display_name=display_name, conn_string=db_url
        )
        await self._client.post(f"{self._url_prefix}/db/", json=data)

    async def get_dbs(self, *, user_id: int) -> List[Database]:
        r = await self._client.get(f"{self._url_prefix}/users/{user_id}/db")
        validator = TypeAdapter(list[Database])
        return validator.validate_json(r.text)

    async def remove_db(self, db_id: UUID):
        await self._client.delete(f"{self._url_prefix}/db/{db_id}")

    async def get_states(
        self, *, source_id: UUID, locale="ru"
    ) -> List[Metric]:
        validator = TypeAdapter(List[Metric])
        r = await self._client.get(
            f"{self._url_prefix}/state/{source_id}?locale={locale}"
        )
        return validator.validate_json(r.text)
