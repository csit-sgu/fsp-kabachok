import logging
from typing import List
from uuid import UUID, uuid4

import db.metrics as metrics
from asgi_correlation_id import CorrelationIdMiddleware
from databases import Database
from entities import Source, UserSource, UserSources
from fastapi import FastAPI, Response
from models import PatchDatabaseRequest, SubmitDatabaseRequest
from utils import Message

from shared.db import PgRepository, create_db_string
from shared.entities import User
from shared.logging import configure_logging
from shared.models import Alert, AlertType, Metric, MetricType
from shared.resources import SharedResources
from shared.utils import SHARED_CONFIG_PATH

app = FastAPI()
app.add_middleware(CorrelationIdMiddleware)
logger = logging.getLogger("app")


@app.get("/")
async def hello():
    return {"message": "Semya is running"}


class Context:
    def __init__(self):
        self.shared_settings = SharedResources(
            f"{SHARED_CONFIG_PATH}/settings.json"
        )
        self.pg = Database(create_db_string(self.shared_settings.pg_creds))
        self.source_repo = PgRepository(self.pg, Source)
        self.relation_repo = PgRepository(self.pg, UserSource)
        self.source_view_repo = PgRepository(self.pg, UserSources)
        self.user_repo = PgRepository(self.pg, User)

    async def init_db(self) -> None:
        await self.pg.connect()

    async def dispose_db(self) -> None:
        await self.pg.disconnect()


ctx = Context()


@app.post("/api/user", status_code=204)
async def register(user: User):
    await ctx.user_repo.add(user)


@app.get("/api/user")
async def get_all_users():
    return await ctx.user_repo.get()


@app.post("/api/db/", status_code=204)
async def submit(entry: SubmitDatabaseRequest):
    uuid = uuid4()
    await ctx.source_repo.add(
        Source(
            source_id=uuid,
            display_name=entry.display_name,
            conn_string=entry.conn_string,
        )
    )
    await ctx.relation_repo.add(
        UserSource(user_id=entry.user_id, source_id=uuid)
    )


@app.get("/api/users/{user_id}/db")
async def fetch(user_id: int):
    result = await ctx.source_view_repo.get(field="user_id", value=user_id)
    return list(filter(lambda x: not x.inactive, result))


@app.get("/api/db/{source_id}")
async def retrieve(source_id: UUID) -> List[Source]:
    return await ctx.source_repo.get(field="source_id", value=source_id)


@app.patch("/api/db/{source_id}", status_code=204)
async def update(source_id: UUID, entry: PatchDatabaseRequest):
    await ctx.source_repo.update(
        Source(
            source_id=source_id,
            conn_string=entry.conn_string,
            display_name=entry.display_name,
            inactive=entry.inactive,
        ),
        fields=["conn_string", "inactive", "display_name"],
    )


@app.delete("/api/db/{source_id}")
async def remove(source_id: UUID):
    source = (await retrieve(source_id))[0]
    source.inactive = True
    await ctx.source_repo.update(source, fields=["inactive"])


@app.get("/api/healthcheck/{source_id}")
async def healthcheck(source_id: UUID, locale: str):
    metrics_limits = ctx.shared_settings.metrics
    source: Source = (await retrieve(source_id))[0]

    async with Database(source.conn_string) as database:
        if not database.is_connected:
            return list(
                Alert(
                    type=AlertType.NOT_CONNECTED, message=Message.NOT_CONNECTED
                )
            )

        alerts = list()

        try:
            free_space = await metrics.get_free_space(database)
            if free_space < metrics_limits.free_space_threshold:
                alerts.append(
                    Alert(
                        type=AlertType.FREE_SPACE, message=Message.FREE_SPACE
                    )
                )

            cpu_usage = await metrics.get_cpu_usage(database)
            if cpu_usage > metrics_limits.cpu_usage_threshold:
                alerts.append(Alert(type=AlertType.CPU, message=Message.CPU))
        except:
            # TODO(nrydanpov): Add proper handling
            pass

        max_active_peers = await metrics.get_max_active_peers(database)
        peers_number = await metrics.get_active_peers_number(database)
        if (
            peers_number
            > max_active_peers * metrics_limits.max_active_peers_ratio
        ):
            alerts.append(
                Alert(
                    type=AlertType.ACTIVE_PEERS, message=Message.ACTIVE_PEERS
                )
            )

        lwlock_count = await metrics.get_lwlock_count(database)
        if lwlock_count > metrics_limits.max_lwlock_count:
            alerts.append(
                Alert(
                    type=AlertType.LWLOCK_COUNT, message=Message.LWLOCK_COUNT
                )
            )

        # TODO: "Transaction with id %pid is running %longest_transaction seconds"
        pid, transaction_duration = await metrics.get_longest_transaction(
            database
        )
        if transaction_duration > metrics_limits.max_transaction_duration:
            alerts.append(
                Alert(type=AlertType.TIMEOUT, message=Message.TIMEOUT)
            )

        return alerts


@app.get("/api/state/{source_id}")
async def get_state(source_id: UUID, locale: str):
    source: Source = (await retrieve(source_id))[0]

    async with Database(source.conn_string) as database:
        if not database.is_connected:
            # TODO(granatam): Change status code
            return Response(
                status_code=400, content=Alert(Message.NOT_CONNECTED, locale)
            )

        try:
            free_space = Metric(
                type=MetricType.FREE_SPACE,
                value=await metrics.get_free_space(database),
            )
            cpu_usage = Metric(
                tyoe=MetricType.CPU_USAGE,
                value=await metrics.get_cpu_usage(database),
            )
        # TODO(nrydanov): Add proper handling
        except:
            free_space = Metric(type=MetricType.FREE_SPACE, value=None)
            cpu_usage = Metric(type=MetricType.CPU_USAGE, value=None)
        active_peers = Metric(
            type=MetricType.ACTIVE_PEERS,
            value=await metrics.get_active_peers_number(database),
        )
        lwlock_count = Metric(
            type=MetricType.LWLOCK_TRANSACTIONS,
            value=await metrics.get_lwlock_count(database),
        )
        # longest_transaction = Metric(
        #     MetricType.LONGEST_TRANSACTION,
        #     await metrics.get_longest_transaction(database),
        # )

        return [
            free_space,
            cpu_usage,
            active_peers,
            lwlock_count,
            # longest_transaction,
        ]


@app.on_event("startup")
async def main() -> None:
    configure_logging()
    await ctx.init_db()


@app.on_event("shutdown")
async def dispose() -> None:
    await ctx.dispose_db()
