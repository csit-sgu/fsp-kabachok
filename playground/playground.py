import asyncio

from databases import Database
from pydantic import BaseModel


class DatabaseCredentials(BaseModel):
    driver: str
    username: str
    password: str
    url: str
    port: int
    db_name: str


def create_db_string(creds: DatabaseCredentials):
    return f"{creds.driver}://{creds.username}:{creds.password}@{creds.url}:{creds.port}/{creds.db_name}?max_size=1000000"


def generate_credentials(url: str, port: int):
    return DatabaseCredentials(
        driver="postgres",
        username="postgres",
        password="1234",
        url=url,
        port=port,
        db_name="playground",
    )


async def connect(**kwargs):
    db = Database(create_db_string(generate_credentials(**kwargs)))
    await db.connect()
    return db


async def many_inserts(**kwargs):
    db = await connect(**kwargs)
    for i in range(100000):
        await db.execute("insert into ovowi values (1, 'aboba', 'aboba');")


async def cpu_intensive(**kwargs):
    db = await connect(**kwargs)

    sql = """
    WITH RECURSIVE cpu_load AS (
    SELECT
        1 AS n
    UNION ALL
    SELECT
        n + 1
      FROM
        cpu_load
      WHERE
        n < 1000000
    )
    SELECT
      md5(random()::text)
    FROM
      cpu_load;
    """
    tasks = [db.execute(sql) for i in range(10000)]
    await asyncio.gather(*tasks)


async def long_sleep(**kwargs):
    db = await connect(**kwargs)

    tasks = [db.execute("select pg_sleep(600);") for i in range(10000)]
    await asyncio.gather(*tasks)
