import datetime
import logging
from typing import List
from uuid import UUID, uuid4

import collect
import db.manage as actions
import db.metrics as metrics
import redis
from asgi_correlation_id import CorrelationIdMiddleware
from databases import Database
from db.redis import RedisRepository
from entities import Source, UserSource, UserSources
from fastapi import FastAPI, Request, Response
from models import PatchDatabaseRequest, SubmitDatabaseRequest
from pydantic import TypeAdapter

from shared.db import PgRepository, create_db_string
from shared.entities import User
from shared.logging import configure_logging
from shared.models import Action, Metric, MetricType
from shared.resources import SharedResources
from shared.routes import AlarmistRoutes
from shared.utils import ACTION_BODY_MAPPING, SHARED_CONFIG_PATH

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

        redis_creds = self.shared_settings.redis_creds
        self.redis = redis.Redis(
            host=redis_creds.host,
            port=redis_creds.port,
            # username=redis_creds.username,
            # password=redis_creds.password,
            decode_responses=True,
        )

        self.active_peers_repo = RedisRepository(
            self.redis, MetricType.ACTIVE_PEERS
        )
        self.cpu_usage_repo = RedisRepository(self.redis, MetricType.CPU_USAGE)
        self.disk_space_repo = RedisRepository(
            self.redis, MetricType.FREE_SPACE
        )

    async def init_db(self) -> None:
        await self.pg.connect()

    async def dispose_db(self) -> None:
        await self.pg.disconnect()


ctx = Context()


@app.post(AlarmistRoutes.USER.value, status_code=204)
async def register(user: User):
    await ctx.user_repo.add(user, ignore_conflict=True)


@app.get(AlarmistRoutes.USER.value)
async def get_all_users():
    return await ctx.user_repo.get()


@app.get(AlarmistRoutes.DB.value)
async def get_all_sources():
    return await ctx.sources_repo.get()


@app.post(AlarmistRoutes.DB.value, status_code=204)
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


@app.get(AlarmistRoutes.USER.value + "{user_id}/db")
async def fetch(user_id: int):
    result = await ctx.source_view_repo.get(field="user_id", value=user_id)
    return list(filter(lambda x: not x.inactive, result))


@app.get(AlarmistRoutes.DB.value + "{source_id}")
async def retrieve(source_id: UUID) -> List[Source]:
    return await ctx.source_repo.get(field="source_id", value=source_id)


@app.patch(AlarmistRoutes.DB.value + "{source_id}", status_code=204)
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


@app.delete(AlarmistRoutes.DB.value + "{source_id}")
async def remove(source_id: UUID):
    source = (await retrieve(source_id))[0]
    source.inactive = True
    await ctx.source_repo.update(source, fields=["inactive"])


@app.get(AlarmistRoutes.HEALTHCHECK.value + "{source_id}")
async def healthcheck(source_id: UUID, locale: str, response: Response):
    logger.debug(f"Healthcheck {source_id=}")
    metrics_limits = ctx.shared_settings.metrics
    source: Source = (await retrieve(source_id))[0]

    ok, r = await collect.try_connect(source_id, source, locale)

    if not ok:
        response.status_code = 400
        return r

    database = r

    alerts = list()

    alert_tasks = [
        collect.check_peers,
        collect.check_free_space,
        collect.check_cpu_usage,
        collect.check_lwlocks,
        collect.check_long_transactions,
    ]

    metrics = {
        collect.check_peers: metrics_limits.max_active_peers_ratio,
        collect.check_free_space: metrics_limits.free_space_threshold,
        collect.check_cpu_usage: metrics_limits.cpu_usage_threshold,
        collect.check_lwlocks: metrics_limits.max_lwlock_count,
        collect.check_long_transactions: metrics_limits.max_transaction_duration,
    }

    repos = {
        collect.check_peers: ctx.active_peers_repo,
        collect.check_free_space: ctx.disk_space_repo,
        collect.check_cpu_usage: ctx.cpu_usage_repo,
        collect.check_lwlocks: None,
        collect.check_long_transactions: None,
    }

    for task in alert_tasks:
        ok, alert = await task(
            source_id, database, metrics[task], locale, repos[task]
        )
        if not ok:
            alerts.append(alert)

    await database.disconnect()
    return alerts


@app.get(AlarmistRoutes.STATE.value + "{source_id}")
async def get_state(source_id: UUID, locale: str, response: Response):
    source: Source = (await retrieve(source_id))[0]

    ok, r = await collect.try_connect(source_id, source, locale)

    if not ok:
        response.status_code = 400
        return r

    database = r

    free_space = Metric(
        type=MetricType.FREE_SPACE,
        value=await metrics.get_free_space(database),
    )
    cpu_usage = Metric(
        type=MetricType.CPU_USAGE,
        value=await metrics.get_cpu_usage(database),
    )
    # TODO(nrydanov): Add proper handling
    active_peers = Metric(
        type=MetricType.ACTIVE_PEERS,
        value=await metrics.get_active_peers_number(database),
    )
    lwlock_count = Metric(
        type=MetricType.LWLOCK_TRANSACTIONS,
        value=await metrics.get_lwlock_count(database),
    )
    lt = await metrics.get_long_transactions(database)
    long_transactions = Metric(
        type=MetricType.LONG_TRANSACTION, value=len(lt), context=lt
    )

    await database.disconnect()

    return [
        free_space,
        cpu_usage,
        active_peers,
        lwlock_count,
        long_transactions,
    ]


# TODO(granatam): Change endpoint and test this
@app.get(AlarmistRoutes.STATE.value + "{source_id}/plots")
async def get_state_graphics(source_id: UUID):
    cpu_usage = await ctx.cpu_usage_repo.get(str(source_id))
    active_peers = await ctx.active_peers_repo.get(str(source_id))
    free_space = await ctx.disk_space_repo.get(str(source_id))

    return {
        MetricType.FREE_SPACE: free_space,
        MetricType.CPU_USAGE: cpu_usage,
        MetricType.ACTIVE_PEERS: active_peers,
    }


@app.post(AlarmistRoutes.MANAGE.value + "{action}")
async def manage(
    source_id: UUID, action: Action, request: Request, response: Response
):
    source: Source = (await retrieve(source_id))[0]
    mapping = ACTION_BODY_MAPPING[action]
    body = TypeAdapter(mapping).validate_python(await request.json())
    ok, r = await collect.try_connect(source_id, source, body.locale)
    if not ok:
        response.status_code = 400
        return r
    conn = r
    match action:
        case Action.SET_MAX_CONNECTIONS:
            logger.info(
                f"Trying to set a new max connections cap, source_id: {source_id}"
            )
            await actions.set_max_connections(conn, body.max_connections)
        case Action.TERMINATE_PROCESS:
            logger.info(
                f"Trying to terminate processes, source_id: {source_id}"
            )
            for pid in body.pids:
                await actions.terminate_process(conn, pid)
        case Action.SET_SHARED_BUFFERS:
            await actions.set_shared_buffers(conn, body.shared_buffers)
        case Action.RESTART_SERVER:
            await actions.restart_server(conn)
        case _:
            response.status_code = 400
            logger.error(
                f"Unexpected action in manage endpoint, source_id: {source_id}"
            )
            return


@app.on_event("startup")
async def main() -> None:
    configure_logging()
    await ctx.init_db()


@app.on_event("shutdown")
async def dispose() -> None:
    await ctx.dispose_db()
