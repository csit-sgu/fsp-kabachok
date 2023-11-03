import databases
from databases import Database


async def connect(db_url):
    database = Database(db_url)
    await database.connect()
    return database


async def get_peer_number(connection: databases.core.Connection) -> int:
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
    response = await connection.execute(
        "SELECT max(now() - xact_start) FROM pg_stat_activity"
        " WHERE state IN ('idle in transaction', 'active');"
    )
    return response


async def get_space(connection: databases.core.Connection):
    response = await connection.execute(
        """
        CREATE FUNCTION pymax (a integer, b integer)
            RETURNS integer
        AS $$
            import shutil

            total, used, free = shutil.disk_usage("/")

            print("Total: %d GiB" % (total // (2**30)))
            print("Used: %d GiB" % (used // (2**30)))
            print("Free: %d GiB" % (free // (2**30)))
        $$ LANGUAGE plpython3u;
        """
    )
    return response


async def get_cpu_usage(connection: databases.core.Connection):
    response = await connection.execute(
        """
        CREATE FUNCTION pymax (a integer, b integer)
            RETURNS integer
        AS $$
            import psutil

            print('The CPU usage is: ', psutil.cpu_percent(1))
        $$ LANGUAGE plpython3u;
        """
    )
    return response
