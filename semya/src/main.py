import logging
from uuid import UUID, uuid4

from asgi_correlation_id import CorrelationIdMiddleware
from databases import Database
from entities import Source, UserSource, UserSources
from fastapi import FastAPI
from models import SubmitDatabaseRequest
from utils import Message, get_text

import db
from shared.db import PgRepository, create_db_string
from shared.logging import configure_logging
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
        return {
            "healthy": False,
            "message": get_text(locale, Message.NOT_CONNECTED),
        }

    free_space = db.get_free_space(database)
    if free_space < metrics.free_space_threshold:
        return {
            "healthy": False,
            "message": get_text(locale, Message.FREE_SPACE),
        }

    cpu_usage = db.get_cpu_usage(database)
    if cpu_usage > metrics.cpu_usage_threshold:
        return {
            "healthy": False,
            "message": get_text(locale, Message.CPU_USAGE),
        }

    peers_number = db.get_peer_number(database)
    lwlock_count = db.get_lwlock_count(database)
    longest_transaction = db.get_longest_transaction(database)

    return {"healthy": True, "message": get_text(locale, Message.OK)}


@app.on_event("startup")
async def main() -> None:
    configure_logging()
    await ctx.init_db()


@app.on_event("shutdown")
async def dispose() -> None:
    await ctx.dispose_db()
