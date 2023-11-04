import databases


async def terminate_process(connection: databases.core.Connection, pid: int):
    await connection.execute(
        f"""
        SELECT pg_terminate_backend(pid) 
        FROM pg_stat_activity 
        WHERE pid = {pid};
        """
    )
