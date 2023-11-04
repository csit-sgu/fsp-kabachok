import logging

import asyncpg
import db.metrics as metrics
from databases import Database
from utils import Message, get_text

from shared.models import Alert, AlertType

logger = logging.getLogger("app")


async def try_connect(source_id, source, locale):
    try:
        database = Database(source.conn_string)
        logger.info("Attempting to connect to DB")
        await database.connect()
    except asyncpg.exceptions.TooManyConnectionsError:
        logger.warn(
            f"Can't connect to source {source_id}, too many connections."
        )
        return False, [
            Alert(
                type=AlertType.ACTIVE_PEERS,
                message=get_text(locale, Message.TOO_MANY_CONNECTIONS),
            )
        ]
    except Exception:
        logger.warn(
            f"Can't connect to source {source_id}, database is unavailable."
        )
        return False, [
            Alert(
                type=AlertType.UNAVAILABLE,
                message=get_text(locale, Message.UNAVAILABLE),
            )
        ]
    return True, database


async def check_peers(source_id, database, max_ratio, locale):
    max_active_peers = await metrics.get_max_active_peers(database)
    peers_number = await metrics.get_active_peers_number(database)
    if peers_number is None or peers_number > max_active_peers * max_ratio:
        logger.warn(
            f"Alert detected. Source {source_id} has too many active peers."
        )
        return False, Alert(
            type=AlertType.ACTIVE_PEERS,
            message=get_text(locale, Message.ACTIVE_PEERS),
        )
    return True, None


async def check_free_space(source_id, database, max_threshold, locale):
    free_space = await metrics.get_free_space(database)
    if free_space is not None and free_space < max_threshold:
        logger.warn(
            f"Alert detected. Source {source_id} hasn't much free space left."
        )
        return False, Alert(
            type=AlertType.FREE_SPACE,
            message=get_text(locale, Message.FREE_SPACE),
        )
    return True, None


async def check_cpu_usage(source_id, database, max_threshold, locale):
    cpu_usage = await metrics.get_cpu_usage(database)
    if cpu_usage is not None and cpu_usage > max_threshold:
        logger.warn(
            f"Alert detected. Source {source_id} has too high CPU usage."
        )
        return False, Alert(
            type=AlertType.CPU,
            message=get_text(locale, Message.CPU),
        )
    return True, None


async def check_lwlocks(source_id, database, max_count, locale):
    lwlock_count = await metrics.get_lwlock_count(database)
    if lwlock_count > max_count:
        logger.warn(
            f"Alert detected. Source {source_id} has too much LW locks"
        )
        return False, Alert(
            type=AlertType.LWLOCK_COUNT,
            message=get_text(locale, Message.LWLOCK_COUNT),
        )
    return True, None


async def check_long_transactions(source_id, database, max_duration, locale):
    response = await metrics.get_long_transactions(database)
    if response:
        logger.warn(
            f"Alert detected. Source {source_id} has too long transactions"
        )
        return False, Alert(
            type=AlertType.TIMEOUT,
            message=get_text(locale, Message.TIMEOUT),
        )
    return True, None
