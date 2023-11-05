import databases


async def terminate_process(connection: databases.core.Connection, pid: int):
    await connection.execute(
        f"""
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE pid = {pid};
        """
    )


# TODO(granatam): max_connections is in [1; 262143]. Check this
async def set_max_connections(
    connection: databases.core.Connection, max_connections: int
):
    await connection.execute(
        f"ALTER SYSTEM SET max_connections = {max_connections};"
    )
    await restart_server(connection)


# TODO(granatam): shared_buffers is in [128Kb; ...]. Check this
async def set_shared_buffers(
    connection: databases.core.Connection, shared_buffers: int
):
    await connection.execute(
        f"ALTER SYSTEM SET shared_buffers = {shared_buffers};"
    )
    await restart_server(connection)


async def restart_server(connection: databases.core.Connection):
    await connection.execute("SELECT pg_reload_conf();")
