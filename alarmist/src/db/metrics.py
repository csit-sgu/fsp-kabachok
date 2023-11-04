import logging
from typing import Optional

import asyncpg
import databases

logger = logging.getLogger()


async def get_max_active_peers(connection: databases.core.Connection) -> int:
    response = await connection.execute("SHOW max_connections;")

    return int(response)


async def get_active_peers_number(
    connection: databases.core.Connection,
) -> int:
    try:
        response = await connection.execute(
            "SELECT COUNT(client_addr) FROM pg_stat_activity;"
        )
    except asyncpg.exceptions.TooManyConnectionsError:
        return None
    return int(response)


async def get_lwlock_count(connection: databases.core.Connection) -> int:
    try:
        response = await connection.execute(
            "SELECT COUNT(*) FROM pg_stat_activity WHERE wait_event = 'LWLock';"
        )
    except asyncpg.exceptions.TooManyConnectionsError:
        return None
    return int(response)


async def get_long_transactions(connection: databases.core.Connection):
    response = await connection.fetch_one(
        """
        SELECT pid, now() - xact_start AS duration
        FROM pg_stat_activity
        WHERE state = 'active' AND now() - xact_start > interval '4 seconds';
        """
    )
    if not response:
        return {}
    result = dict(map(lambda x: (x[0], x[1]), response))
    logger.info(f"Found long transactions: {result}")
    return result


async def get_free_space(
    connection: databases.core.Connection,
) -> Optional[float]:
    try:
        await connection.execute("CREATE EXTENSION IF NOT EXISTS plpython3u;")
        await connection.execute(
            """
            CREATE OR REPLACE FUNCTION kabachok_get_space ()
                RETURNS real
            AS $$
                import shutil

                total, _used, free = shutil.disk_usage("/")

                return free / total * 100
            $$ LANGUAGE plpython3u;
            """
        )
        response = await connection.execute("SELECT kabachok_get_space ();")
        return float(response)
    except asyncpg.exceptions.FeatureNotSupportedError:
        return None


async def get_cpu_usage(
    connection: databases.core.Connection,
) -> Optional[float]:
    try:
        await connection.execute("CREATE EXTENSION IF NOT EXISTS plpython3u;")
        await connection.execute(
            """
            CREATE OR REPLACE FUNCTION kabachok_get_cpu_usage ()
                RETURNS real
            AS $$
                import os
                import time

                with open('/proc/stat') as stat_file:
                    lines = stat_file.readlines()

                cpu_stats = lines[0].split()[1:]
                total_time = sum(map(int, cpu_stats))
                idle_time = int(cpu_stats[3])

                return 100.0 - (idle_time / total_time * 100.0)
            $$ LANGUAGE plpython3u;
            """
        )
        response = await connection.execute(
            "SELECT kabachok_get_cpu_usage ();"
        )
        return float(response)
    except asyncpg.exceptions.FeatureNotSupportedError:
        return None
