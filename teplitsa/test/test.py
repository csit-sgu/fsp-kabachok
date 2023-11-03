import asyncio

import databases


async def infinite_loop(connection: databases.core.Connection):
    i = 0
    while i < 1000:
        asyncio.create_task(connection.execute("select pg_sleep(30);"))


async def main():
    # TODO: Add connection
    await infinite_loop()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
