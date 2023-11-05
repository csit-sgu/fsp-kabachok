import databases


async def restart_server(connection):
    await connection.execute("CREATE EXTENSION IF NOT EXISTS plpython3u;")
    await connection.execute(
        """
            CREATE OR REPLACE FUNCTION kabachok_restart_server()
            RETURNS int
            AS $$
            subprocess.run(['pgctl', 'restart', '-t', '0'], check=True)
            return 0
            $$ LANGUAGE plpython3u;
            """
    )


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
    await reload_configuration(connection)


# TODO(granatam): shared_buffers is in [128Kb; ...]. Check this
async def set_shared_buffers(
    connection: databases.core.Connection, shared_buffers: int
):
    await connection.execute(
        f"ALTER SYSTEM SET shared_buffers = {shared_buffers};"
    )
    await reload_configuration(connection)


async def reload_configuration(connection: databases.core.Connection):
    await connection.execute("SELECT pg_reload_conf();")
