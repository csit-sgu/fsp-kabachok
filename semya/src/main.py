import logging
from uuid import UUID, uuid4

import db.metrics as metrics
from asgi_correlation_id import CorrelationIdMiddleware
from databases import Database
from entities import Source, UserSource, UserSources
from fastapi import FastAPI, Response
from models import SubmitDatabaseRequest
from utils import Alert, Message

from shared.db import PgRepository, create_db_string
from shared.logging import configure_logging
from shared.metric import Metric, MetricType
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

    async def init_db(self) -> None:
        await self.pg.connect()

    async def dispose_db(self) -> None:
        await self.pg.disconnect()


ctx = Context()


@app.post("/api/db/", status_code=204)
async def submit(entry: SubmitDatabaseRequest):
    uuid = uuid4()
    await ctx.source_repo.add(
        Source(source_id=uuid, conn_string=entry.conn_string)
    )
    await ctx.relation_repo.add(
        UserSource(user_id=entry.user_id, source_id=uuid)
    )


@app.get("/api/users/{user_id}/db")
async def fetch(user_id: int):
    return await ctx.source_view_repo.get(field="user_id", value=user_id)


@app.get("/api/db/{source_id}")
async def retrieve(source_id: UUID) -> Source:
    return await ctx.source_repo.get(field="source_id", value=source_id)


@app.patch("/api/db/", status_code=204)
async def update(entry: SubmitDatabaseRequest):
    return await ctx.source_repo.update(entry)


@app.delete("/api/db/{source_id}")
async def remove(source_id: UUID):
    source = retrieve(source_id)
    source.inactive = True
    return await ctx.source_repo.update(source)


@app.post("/api/healthcheck/{source_id}")
async def healthcheck(source_id: UUID, locale: str):
    metrics = ctx.shared_settings.metrics
    source: Source = await retrieve(source_id)

    database = Database(source.conn_string)
    await database.connect()

    if not database.is_connected:
        return list(Alert(Message.NOT_CONNECTED, locale))

    alerts = list()

    free_space = metrics.get_free_space(database)
    if free_space < metrics.free_space_threshold:
        alerts.append(Alert(Message.FREE_SPACE, locale))

    cpu_usage = metrics.get_cpu_usage(database)
    if cpu_usage > metrics.cpu_usage_threshold:
        alerts.append(Alert(Message.CPU_USAGE, locale))

    peers_number = metrics.get_active_peers_number(database)
    lwlock_count = metrics.get_lwlock_count(database)
    longest_transaction = metrics.get_longest_transaction(database)

    return alerts


@app.post("/api/get_state/{source_id}")
async def get_state(source_id: UUID, locale: str, response: Response):
    metrics = ctx.shared_settings.metrics
    source: Source = await retrieve(source_id)

    database = Database(source.conn_string)
    await database.connect()

    if not database.is_connected:
        # TODO(granatam): Change status code
        return Response(
            status_code=400, content=Alert(Message.NOT_CONNECTED, locale)
        )

    free_space = Metric(
        MetricType.FREE_SPACE, metrics.get_free_space(database)
    )
    cpu_usage = Metric(MetricType.CPU_USAGE, metrics.get_cpu_usage(database))
    active_peers = Metric(
        MetricType.ACTIVE_PEERS, metrics.get_active_peers_number(database)
    )
    lwlock_count = Metric(
        MetricType.LWLOCK_TRANSACTIONS, metrics.get_lwlock_count(database)
    )
    longest_transaction = Metric(
        MetricType.LONGEST_TRANSACTION,
        metrics.get_longest_transaction(database),
    )

    return [
        free_space,
        cpu_usage,
        active_peers,
        lwlock_count,
        longest_transaction,
    ]


@app.on_event("startup")
async def main() -> None:
    configure_logging()
    await ctx.init_db()


@app.on_event("shutdown")
async def dispose() -> None:
    await ctx.dispose_db()
