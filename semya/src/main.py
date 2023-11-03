import logging
from uuid import UUID

from asgi_correlation_id import CorrelationIdMiddleware
from databases import Database
from entities import Source
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
        self.db_repo = PgRepository(self.pg, Source)

    async def init_db(self) -> None:
        await self.pg.connect()

    async def dispose_db(self) -> None:
        await self.pg.disconnect()


ctx = Context()


@app.post("/api/db/")
async def submit(entry: SubmitDatabaseRequest):
    pass


@app.get("/api/db/{user_id}")
async def fetch(user_id: int):
    pass


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
