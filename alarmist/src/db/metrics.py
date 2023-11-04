from typing import Optional

import databases


async def get_active_peers_number(
    connection: databases.core.Connection,
) -> int:
    response = await connection.execute(
        "SELECT COUNT(client_addr) FROM pg_stat_activity;"
    )
    return int(response)


async def get_lwlock_count(connection: databases.core.Connection) -> int:
    response = await connection.execute(
        "SELECT COUNT(*) FROM pg_stat_activity WHERE wait_event = 'LWLock';"
    )
    return int(response)


async def get_longest_transaction(connection: databases.core.Connection):
    response = await connection.fetch_one(
        """
        SELECT pid, now() - xact_start AS time_difference
        FROM pg_stat_activity
        WHERE state IN ('idle in transaction', 'active')
        ORDER BY time_difference DESC
        LIMIT 1;
        """
    )
    return response[0], response[1].total_seconds()


# TODO: Change it from Gb's to %'s of free space
async def get_free_space(
    connection: databases.core.Connection,
) -> Optional[float]:
    await connection.execute("CREATE EXTENSION IF NOT EXISTS plpython3u;")
    await connection.execute(
        """
        CREATE OR REPLACE FUNCTION kabachok_get_space ()
            RETURNS real
        AS $$
            import shutil

            _total, _used, free = shutil.disk_usage("/")

            return free / (2**30)
        $$ LANGUAGE plpython3u;
        """
    )
    response = await connection.execute("SELECT kabachok_get_space ();")
    return float(response)


async def get_cpu_usage(
    connection: databases.core.Connection,
) -> Optional[float]:
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
    response = await connection.execute("SELECT kabachok_get_cpu_usage ();")
    return float(response)
