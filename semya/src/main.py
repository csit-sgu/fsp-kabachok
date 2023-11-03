import logging
from uuid import UUID, uuid4

from asgi_correlation_id import CorrelationIdMiddleware
from databases import Database
from entities import Source, UserSource, UserSources
from fastapi import FastAPI
from models import SubmitDatabaseRequest

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


@app.post("/api/db/")
async def submit(entry: SubmitDatabaseRequest):
    uuid = uuid4()
    ctx.source_repo.add(Source(source_id=uuid, **entry.model_dump()))
    ctx.source_repo.add(UserSource(user_id=entry.user_id, source_id=uuid))


@app.get("/api/db/{user_id}")
async def fetch(user_id: int):
    return await ctx.source_view_repo.get(field="user_id", value=user_id)


@app.patch("/api/db/")
async def update(entry_id: UUID):
    pass


@app.delete("/api/db/")
async def remove(entry_id: UUID):
    pass


@app.post("/api/healthcheck")
async def healthcheck(entry_id: UUID):
    pass


@app.on_event("startup")
async def main() -> None:
    configure_logging()
    await ctx.init_db()


@app.on_event("shutdown")
async def dispose() -> None:
    await ctx.dispose_db()
