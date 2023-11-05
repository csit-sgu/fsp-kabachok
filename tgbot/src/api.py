import logging
from typing import Dict, List
from uuid import UUID

import httpx
from graph import create_graph
from pydantic import TypeAdapter

from shared.entities import User
from shared.models import Alert, Database, Metric, MetricType
from shared.routes import AlarmistRoutes

logger = logging.getLogger("app")


class Api:
    def __init__(self, async_client: httpx.AsyncClient, url_prefix: str):
        self._client = async_client
        self._url_prefix = url_prefix

    async def submit_db(self, *, user_id: int, display_name: str, db_url: str):
        logger.debug(
            f"Api.submit_db called with params: {user_id=} {display_name=} {db_url=}"
        )

        data = dict(
            user_id=user_id, display_name=display_name, conn_string=db_url
        )
        await self._client.post(
            f"{self._url_prefix}{AlarmistRoutes.DB.value}", json=data
        )

    async def get_db(self, *, user_id: int) -> List[Database]:
        logger.debug(f"Api.get_db called with params: {user_id=}")

        r = await self._client.get(
            f"{self._url_prefix}{AlarmistRoutes.USER.value}{user_id}/db"
        )
        validator = TypeAdapter(list[Database])
        return validator.validate_json(r.text)

    async def retrieve_db(self, *, source_id: UUID) -> Database:
        logger.debug(f"Api.retrieve_db called with params: {source_id=}")

        r = await self._client.get(
            f"{self._url_prefix}{AlarmistRoutes.DB.value}{source_id}"
        )
        validator = TypeAdapter(Database)
        return validator.validate_json(r.text)

    async def remove_db(self, db_id: UUID):
        logger.debug(f"Api.remove_db called with params: {db_id=}")

        await self._client.delete(
            f"{self._url_prefix}{AlarmistRoutes.DB.value}{db_id}"
        )

    async def register_user(self, user_id: int, chat_id: int):
        await self._client.post(
            f"{self._url_prefix}{AlarmistRoutes.USER.value}",
            json={"user_id": user_id, "chat_id": chat_id},
        )

    async def get_states(
        self, *, source_id: UUID, locale="ru"
    ) -> List[Metric]:
        logger.debug(
            f"Api.get_states called with params: {source_id=} {locale=}"
        )

        validator = TypeAdapter(List[Metric])
        r = await self._client.get(
            f"{self._url_prefix}{AlarmistRoutes.STATE.value}{source_id}?locale={locale}"
        )
        if r.status_code == 400:
            return []
        return validator.validate_json(r.text)

    async def get_states_plots(self, source_id):
        logger.debug(f"Api.get_states_plots called with params: {source_id=}")
        validator = TypeAdapter(Dict[MetricType, Dict[float, float]])
        r = await self._client.get(
            f"{self._url_prefix}{AlarmistRoutes.STATE.value}{source_id}/plots"
        )
        return validator.validate_json(r.text)

    async def healthcheck(self, source_id, locale="ru"):
        logger.debug(
            f"Api.healthcheck called with params: {source_id=} {locale=}"
        )
        validator = TypeAdapter(List[Alert] | None)
        r = await self._client.get(
            f"{self._url_prefix}{AlarmistRoutes.HEALTHCHECK.value}{source_id}?locale={locale}"
        )
        if r.status_code == 400:
            logger.debug(f"404: {r=}")
            return []

        await self.get_states_plots(source_id)
        return validator.validate_json(r.text)

    async def get_users(self):
        logger.debug("Api.get_users called")

        validator = TypeAdapter(List[User])
        url = f"{self._url_prefix}{AlarmistRoutes.USER.value}"
        logger.debug(f"Sending GET request to {url}")
        r = await self._client.get(url)
        return validator.validate_json(r.text)

    async def manage(self, source_id, action, body):
        r = await self._client.post(
            f"{self._url_prefix}{AlarmistRoutes.MANAGE.value}{action.value}?source_id={source_id}",
            json=body,
        )
